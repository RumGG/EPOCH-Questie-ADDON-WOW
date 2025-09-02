#!/usr/bin/env python3
"""
Final fix for the pfQuest merged database
Properly formats all quest entries to Questie's 30-field structure
"""

import re

def parse_quest_entry(line):
    """Parse a quest entry line and extract its components"""
    # Match the quest ID and the start of the data
    match = re.match(r'(\s*\[(\d+)\]\s*=\s*\{)', line)
    if not match:
        return None
    
    indent = match.group(1)
    quest_id = match.group(2)
    
    # Extract the quest name if present
    name_match = re.search(r'"([^"]*)"', line)
    quest_name = name_match.group(1) if name_match else "[Epoch] Quest " + quest_id
    
    # Extract NPC arrays if present
    # Look for patterns like {{number,number}} or {{number}}
    npc_pattern = r'\{\{([0-9,\s]*)\}\}'
    npc_matches = re.findall(npc_pattern, line)
    
    quest_giver_npcs = None
    turn_in_npcs = None
    
    if len(npc_matches) >= 1 and npc_matches[0]:
        quest_giver_npcs = '{{' + npc_matches[0] + '}}'
    if len(npc_matches) >= 2 and npc_matches[1]:
        turn_in_npcs = '{{' + npc_matches[1] + '}}'
    
    # Extract other fields from original line if it has them
    # Look for level info in comments
    level_match = re.search(r'Level (\d+)', line)
    quest_level = level_match.group(1) if level_match else 'nil'
    
    # Build the properly formatted entry with all 30 fields
    fields = []
    fields.append(f'"{quest_name}"')  # 1. name
    fields.append(quest_giver_npcs or 'nil')  # 2. startedBy NPCs
    fields.append(turn_in_npcs or 'nil')  # 3. finishedBy NPCs
    fields.append('nil')  # 4. requiredLevel
    fields.append(quest_level)  # 5. questLevel
    fields.append('nil')  # 6. requiredRaces
    fields.append('nil')  # 7. requiredClasses
    fields.append('nil')  # 8. objectives text
    fields.append('nil')  # 9. triggerEnd
    fields.append('nil')  # 10. objectives
    fields.append('nil')  # 11. sourceItemId
    fields.append('nil')  # 12. preQuestGroup
    fields.append('nil')  # 13. preQuestSingle
    fields.append('nil')  # 14. childQuests
    fields.append('nil')  # 15. inGroupWith
    fields.append('nil')  # 16. exclusiveTo
    fields.append('nil')  # 17. zoneOrSort
    fields.append('nil')  # 18. requiredSkill
    fields.append('nil')  # 19. requiredMinRep
    fields.append('nil')  # 20. requiredMaxRep
    fields.append('nil')  # 21. requiredSourceItems
    fields.append('nil')  # 22. nextQuestInChain
    fields.append('nil')  # 23. questFlags
    fields.append('0')   # 24. specialFlags (common default)
    fields.append('nil')  # 25. parentQuest
    fields.append('nil')  # 26. reputationReward
    fields.append('nil')  # 27. extraObjectives
    fields.append('nil')  # 28. requiredSpell
    fields.append('nil')  # 29. requiredSpecialization
    fields.append('nil')  # 30. requiredMaxLevel
    
    # Preserve any comment from original line
    comment_match = re.search(r'(--.*?)$', line)
    comment = comment_match.group(1) if comment_match else f"-- Quest {quest_id}"
    
    # Build the final line
    return f"{indent}{{{','.join(fields)}}}, {comment}"

def fix_database(input_file, output_file):
    """Fix all quest entries in the database"""
    print(f"Processing {input_file}...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    quest_count = 0
    fixed_count = 0
    in_quest_data = False
    
    for line in lines:
        # Check if we're entering the quest data section
        if 'epochQuestDataMerged = {' in line:
            in_quest_data = True
            fixed_lines.append(line)
            continue
        
        # Check if we're leaving the quest data section
        if in_quest_data and line.strip() == '}':
            in_quest_data = False
            fixed_lines.append(line)
            continue
        
        # Process quest entries
        if in_quest_data and re.match(r'\s*\[\d+\]', line):
            quest_count += 1
            fixed_entry = parse_quest_entry(line)
            if fixed_entry:
                fixed_lines.append(fixed_entry + '\n')
                fixed_count += 1
            else:
                # Keep original if we can't parse it
                fixed_lines.append(line)
        else:
            # Keep all other lines as-is
            fixed_lines.append(line)
    
    # Write the fixed file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Processed {quest_count} quests, fixed {fixed_count}")
    print(f"Output written to {output_file}")
    
    return quest_count, fixed_count

def validate_syntax(filepath):
    """Quick syntax validation"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    open_braces = content.count('{')
    close_braces = content.count('}')
    
    print(f"\nSyntax check for {filepath}:")
    print(f"  Open braces: {open_braces}")
    print(f"  Close braces: {close_braces}")
    
    if open_braces == close_braces:
        print("  ✅ Braces are balanced!")
        return True
    else:
        print(f"  ❌ Brace mismatch: {abs(open_braces - close_braces)} difference")
        return False

def main():
    # Fix the FINAL database
    input_file = "epochQuestDB_FINAL.lua"
    output_file = "epochQuestDB_READY.lua"
    
    quest_count, fixed_count = fix_database(input_file, output_file)
    
    # Validate the result
    if validate_syntax(output_file):
        print(f"\n✅ Database is ready for use: {output_file}")
        print(f"Total quests: {quest_count}")
    else:
        print(f"\n⚠️ Warning: Database may have syntax issues")

if __name__ == "__main__":
    main()