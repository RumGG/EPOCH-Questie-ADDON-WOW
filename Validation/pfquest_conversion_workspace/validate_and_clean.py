#!/usr/bin/env python3
"""
Validate and clean the pfQuest converted database for Project Epoch
Detects contamination from TBC/Wrath and fixes incomplete entries
"""

import re
import json
from collections import defaultdict

# Known contamination indicators
SUSPICIOUS_QUEST_RANGES = {
    'tbc': (8000, 11999),      # TBC quests typically 8000-11999
    'wrath': (12000, 14999),   # Wrath quests typically 12000-14999
    'cata': (15000, 25999),    # Cataclysm quests 15000-25999
}

# Valid NPC ID ranges for vanilla/custom
VALID_NPC_RANGES = [
    (1, 20000),         # Vanilla NPCs
    (25000, 50000),     # Custom server NPCs (Epoch)
    (100000, 200000),   # More custom NPCs
]

# Zone IDs that are TBC/Wrath (should not appear)
CONTAMINATED_ZONES = {
    530: "Outland",           # TBC
    571: "Northrend",         # Wrath
    609: "Ebon Hold",         # Wrath DK area
    # Add more as needed
}

def is_valid_npc_id(npc_id):
    """Check if NPC ID is in valid ranges"""
    if not npc_id:
        return True
    npc_id = int(npc_id)
    for min_id, max_id in VALID_NPC_RANGES:
        if min_id <= npc_id <= max_id:
            return True
    return False

def detect_contamination(quest_id, quest_data):
    """Detect if quest is likely from TBC/Wrath"""
    issues = []
    quest_id = int(quest_id)
    
    # Check quest ID ranges
    for expansion, (min_id, max_id) in SUSPICIOUS_QUEST_RANGES.items():
        if min_id <= quest_id <= max_id:
            issues.append(f"Quest ID {quest_id} in {expansion.upper()} range")
    
    # Parse quest data to check NPCs
    npc_pattern = r'\{\{([0-9,]+)\}\}'
    npc_matches = re.findall(npc_pattern, quest_data)
    
    for match in npc_matches:
        npcs = match.split(',')
        for npc in npcs:
            if npc and not is_valid_npc_id(npc):
                issues.append(f"Invalid NPC ID: {npc}")
    
    # Check for zone contamination
    zone_pattern = r',\s*(\d+)\s*,.*?,\s*(\d+)\s*,'  # positions 17 and 23 often have zone data
    zone_match = re.search(zone_pattern, quest_data)
    if zone_match:
        for zone_str in zone_match.groups():
            try:
                zone_id = int(zone_str)
                if zone_id in CONTAMINATED_ZONES:
                    issues.append(f"Contaminated zone: {CONTAMINATED_ZONES[zone_id]} ({zone_id})")
            except:
                pass
    
    return issues

def fix_incomplete_entry(line):
    """Fix incomplete quest entries by adding missing fields"""
    # Count existing commas to determine how many fields we have
    comma_count = line.count(',')
    
    # Quest entries should have 29 commas (30 fields)
    if comma_count < 29:
        # Find where the entry is cut off (usually after comment)
        comment_match = re.search(r'--[^,]*$', line)
        if comment_match:
            # Remove the comment temporarily
            comment = comment_match.group()
            line_without_comment = line[:comment_match.start()].rstrip()
            
            # Count fields in the line
            fields_present = comma_count + 1
            fields_needed = 30 - fields_present
            
            # Add nil fields
            missing_fields = ',nil' * fields_needed
            
            # Close any open brackets
            open_brackets = line_without_comment.count('{') - line_without_comment.count('}')
            closing_brackets = '}' * open_brackets
            
            # Reconstruct the line
            fixed_line = line_without_comment + closing_brackets + missing_fields + '}, ' + comment
        else:
            # No comment, just add missing fields
            fields_present = comma_count + 1
            fields_needed = 30 - fields_present
            missing_fields = ',nil' * fields_needed
            
            # Close any open brackets
            open_brackets = line.count('{') - line.count('}')
            closing_brackets = '}' * open_brackets
            
            fixed_line = line.rstrip() + closing_brackets + missing_fields + '},'
        
        return fixed_line
    
    return line

def validate_file(filepath):
    """Validate and clean the quest database file"""
    print(f"Validating {filepath}...")
    
    contaminated_quests = []
    incomplete_entries = []
    fixed_lines = []
    quest_count = 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    in_quest_data = False
    for i, line in enumerate(lines):
        # Check if we're in the quest data section
        if 'epochQuestDataMerged = {' in line or 'pfQuestConvertedData = {' in line:
            in_quest_data = True
            fixed_lines.append(line)
            continue
        
        if in_quest_data and line.strip() == '}':
            in_quest_data = False
            fixed_lines.append(line)
            continue
        
        if in_quest_data:
            # Parse quest entries
            quest_match = re.match(r'\s*\[(\d+)\]\s*=\s*\{(.+)', line)
            if quest_match:
                quest_id = quest_match.group(1)
                quest_data = quest_match.group(2)
                quest_count += 1
                
                # Check for contamination
                issues = detect_contamination(quest_id, quest_data)
                if issues:
                    contaminated_quests.append((quest_id, issues))
                
                # Check if entry is incomplete
                if not quest_data.rstrip().endswith('},'):
                    incomplete_entries.append(quest_id)
                    # Fix the entry
                    fixed_line = fix_incomplete_entry(line)
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    # Generate report
    report = f"""
VALIDATION REPORT FOR {filepath}
{'='*60}

Total Quests Analyzed: {quest_count}

CONTAMINATION DETECTION:
Found {len(contaminated_quests)} potentially contaminated quests:
"""
    
    for quest_id, issues in contaminated_quests[:20]:  # Show first 20
        report += f"  Quest {quest_id}:\n"
        for issue in issues:
            report += f"    - {issue}\n"
    
    if len(contaminated_quests) > 20:
        report += f"  ... and {len(contaminated_quests) - 20} more\n"
    
    report += f"""
INCOMPLETE ENTRIES:
Found {len(incomplete_entries)} incomplete entries
"""
    if incomplete_entries:
        report += f"Quest IDs: {', '.join(incomplete_entries[:10])}"
        if len(incomplete_entries) > 10:
            report += f" ... and {len(incomplete_entries) - 10} more"
    
    report += "\n\nAll incomplete entries have been fixed in the output file."
    
    return fixed_lines, report, contaminated_quests

def main():
    # Validate the merged file
    merged_file = "epochQuestDB_MERGED.lua"
    fixed_lines, report, contaminated = validate_file(merged_file)
    
    # Write the cleaned file
    clean_file = "epochQuestDB_CLEANED.lua"
    with open(clean_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    # Write the validation report
    with open("validation_report_detailed.txt", 'w') as f:
        f.write(report)
    
    # Create a contamination removal script if needed
    if contaminated:
        print(f"\nFound {len(contaminated)} potentially contaminated quests")
        print("Creating removal script...")
        
        with open("remove_contaminated.py", 'w') as f:
            f.write("#!/usr/bin/env python3\n")
            f.write("# Script to remove contaminated quests\n")
            f.write("import re\n\n")
            f.write(f"contaminated_ids = {[int(q[0]) for q in contaminated]}\n\n")
            f.write("""
with open('epochQuestDB_CLEANED.lua', 'r') as f:
    lines = f.readlines()

with open('epochQuestDB_FINAL.lua', 'w') as f:
    skip_next = False
    for line in lines:
        match = re.match(r'\s*\[(\d+)\]', line)
        if match and int(match.group(1)) in contaminated_ids:
            skip_next = True
            continue
        if skip_next and line.strip().endswith('},'):
            skip_next = False
            continue
        f.write(line)
""")
    
    print(f"Validation complete!")
    print(f"- Cleaned file: {clean_file}")
    print(f"- Report: validation_report_detailed.txt")
    if contaminated:
        print(f"- Contamination removal script: remove_contaminated.py")

if __name__ == "__main__":
    main()