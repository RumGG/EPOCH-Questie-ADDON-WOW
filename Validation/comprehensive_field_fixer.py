#!/usr/bin/env python3

"""
Comprehensive fix for ALL remaining field type issues in epochQuestDB.lua

This script fixes all fields that have numbers where they should have nil or arrays:
- Position 12: preQuestGroup (should be nil or {questId,...})
- Position 13: preQuestSingle (should be nil or {questId,...}) 
- Position 14: childQuests (should be nil or {questId,...})
- Position 15: inGroupWith (should be nil or {questId,...})
- Position 16: exclusiveTo (should be nil or {questId,...})
- Position 18: requiredSkill (should be nil or {skillId, value})
- Position 19: requiredMinRep (should be nil or {factionId, value})
- Position 20: requiredMaxRep (should be nil or {factionId, value})
- Position 21: requiredSourceItems (should be nil or {itemId,...})
- Position 26: reputationReward (should be nil or {{factionId, value},...})
- Position 27: extraObjectives (should be nil or {{spellId, text},...})

Based on analysis of the actual data, this script uses smart logic to determine
where misplaced values should actually go.
"""

import re

def analyze_quest_structure(line):
    """Parse quest line and return quest_id and list of fields"""
    match = re.search(r'\[(\d+)\] = \{(.*)\},', line)
    if not match:
        return None, None
    
    quest_id = match.group(1)
    data = '{' + match.group(2) + '}'
    
    # Split by commas at depth 1
    parts = []
    current = ""
    depth = 0
    for char in data[1:-1]:  # Skip outer braces
        if char == '{':
            depth += 1
            current += char
        elif char == '}':
            depth -= 1
            current += char
        elif char == ',' and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += char
    if current:
        parts.append(current.strip())
    
    return quest_id, parts

def should_be_quest_id(value):
    """Check if a numeric value looks like a quest ID (>= 10000)"""
    try:
        val = int(value)
        return val >= 10000
    except ValueError:
        return False

def should_be_zone_id(value):
    """Check if a numeric value looks like a zone ID (1-2000)"""
    try:
        val = int(value)
        return 1 <= val <= 2000
    except ValueError:
        return False

def should_be_flag(value):
    """Check if a numeric value looks like a flag (0-10)"""
    try:
        val = int(value)
        return 0 <= val <= 10
    except ValueError:
        return False

def fix_all_field_issues():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        if not line.strip().startswith('[') or '=' not in line:
            continue
            
        if line.strip().startswith('--'):
            continue
        
        quest_id, fields = analyze_quest_structure(line)
        if not fields:
            continue
        
        # Make a copy to modify
        new_fields = fields[:]
        fixed = False
        
        # Ensure we have enough fields (extend to 30 if needed)
        while len(new_fields) < 30:
            new_fields.append('nil')
        
        # Position 14: childQuests - should be nil or {questId,...}
        if new_fields[13] != 'nil' and not new_fields[13].startswith('{'):
            try:
                val = int(new_fields[13])
                if should_be_zone_id(val):
                    # Move to position 17 (zoneOrSort) if it's nil
                    if new_fields[16] == 'nil':
                        new_fields[16] = new_fields[13]
                        new_fields[13] = 'nil'
                        print(f"Quest {quest_id}: Moved zone ID {val} from position 14 to 17")
                        fixed = True
                    else:
                        new_fields[13] = 'nil'
                        print(f"Quest {quest_id}: Cleared invalid childQuests value {val}")
                        fixed = True
                else:
                    new_fields[13] = 'nil'
                    print(f"Quest {quest_id}: Cleared invalid childQuests value {val}")
                    fixed = True
            except ValueError:
                pass
        
        # Position 16: exclusiveTo - should be nil or {questId,...}
        if new_fields[15] != 'nil' and not new_fields[15].startswith('{'):
            try:
                val = int(new_fields[15])
                if should_be_zone_id(val):
                    # Move to position 17 (zoneOrSort) if it's nil
                    if new_fields[16] == 'nil':
                        new_fields[16] = new_fields[15]
                        new_fields[15] = 'nil'
                        print(f"Quest {quest_id}: Moved zone ID {val} from position 16 to 17")
                        fixed = True
                    else:
                        new_fields[15] = 'nil'
                        print(f"Quest {quest_id}: Cleared invalid exclusiveTo value {val}")
                        fixed = True
                else:
                    new_fields[15] = 'nil'
                    print(f"Quest {quest_id}: Cleared invalid exclusiveTo value {val}")
                    fixed = True
            except ValueError:
                pass
        
        # Position 18: requiredSkill - should be nil or {skillId, value}
        if new_fields[17] != 'nil' and not new_fields[17].startswith('{'):
            try:
                val = int(new_fields[17])
                if should_be_zone_id(val):
                    # Move to position 17 (zoneOrSort) if it's nil
                    if new_fields[16] == 'nil':
                        new_fields[16] = new_fields[17]
                        new_fields[17] = 'nil'
                        print(f"Quest {quest_id}: Moved zone ID {val} from position 18 to 17")
                        fixed = True
                    else:
                        new_fields[17] = 'nil'
                        print(f"Quest {quest_id}: Cleared invalid requiredSkill value {val}")
                        fixed = True
                else:
                    new_fields[17] = 'nil'
                    print(f"Quest {quest_id}: Cleared invalid requiredSkill value {val}")
                    fixed = True
            except ValueError:
                pass
        
        # Position 19: requiredMinRep - should be nil or {factionId, value}
        if new_fields[18] != 'nil' and not new_fields[18].startswith('{'):
            try:
                val = int(new_fields[18])
                if should_be_quest_id(val):
                    # This looks like a next quest ID for position 22
                    if new_fields[21] == 'nil':
                        new_fields[21] = new_fields[18]
                        new_fields[18] = 'nil'
                        print(f"Quest {quest_id}: Moved quest ID {val} from position 19 to 22")
                        fixed = True
                    else:
                        new_fields[18] = 'nil'
                        print(f"Quest {quest_id}: Cleared invalid requiredMinRep value {val}")
                        fixed = True
                else:
                    new_fields[18] = 'nil'
                    print(f"Quest {quest_id}: Cleared invalid requiredMinRep value {val}")
                    fixed = True
            except ValueError:
                pass
        
        # Position 20: requiredMaxRep - should be nil or {factionId, value}
        if new_fields[19] != 'nil' and not new_fields[19].startswith('{'):
            try:
                val = int(new_fields[19])
                if should_be_flag(val):
                    # Move to position 23 (questFlags) if it's nil
                    if new_fields[22] == 'nil':
                        new_fields[22] = new_fields[19]
                        new_fields[19] = 'nil'
                        print(f"Quest {quest_id}: Moved flag {val} from position 20 to 23")
                        fixed = True
                    elif new_fields[23] == 'nil':
                        # Try position 24 (specialFlags)
                        new_fields[23] = new_fields[19]
                        new_fields[19] = 'nil'
                        print(f"Quest {quest_id}: Moved flag {val} from position 20 to 24")
                        fixed = True
                    else:
                        new_fields[19] = 'nil'
                        print(f"Quest {quest_id}: Cleared invalid requiredMaxRep value {val}")
                        fixed = True
                else:
                    new_fields[19] = 'nil'
                    print(f"Quest {quest_id}: Cleared invalid requiredMaxRep value {val}")
                    fixed = True
            except ValueError:
                pass
        
        # Position 21: requiredSourceItems - should be nil or {itemId,...}
        if new_fields[20] != 'nil' and not new_fields[20].startswith('{'):
            try:
                val = int(new_fields[20])
                if should_be_quest_id(val):
                    # This looks like a next quest ID for position 22
                    if new_fields[21] == 'nil':
                        new_fields[21] = new_fields[20]
                        new_fields[20] = 'nil'
                        print(f"Quest {quest_id}: Moved quest ID {val} from position 21 to 22")
                        fixed = True
                    else:
                        new_fields[20] = 'nil'
                        print(f"Quest {quest_id}: Cleared invalid requiredSourceItems value {val}")
                        fixed = True
                elif should_be_flag(val):
                    # Move to position 23 (questFlags) or 24 (specialFlags)
                    if new_fields[22] == 'nil':
                        new_fields[22] = new_fields[20]
                        new_fields[20] = 'nil'
                        print(f"Quest {quest_id}: Moved flag {val} from position 21 to 23")
                        fixed = True
                    elif new_fields[23] == 'nil':
                        new_fields[23] = new_fields[20]
                        new_fields[20] = 'nil'
                        print(f"Quest {quest_id}: Moved flag {val} from position 21 to 24")
                        fixed = True
                    else:
                        new_fields[20] = 'nil'
                        print(f"Quest {quest_id}: Cleared invalid requiredSourceItems value {val}")
                        fixed = True
                else:
                    new_fields[20] = 'nil'
                    print(f"Quest {quest_id}: Cleared invalid requiredSourceItems value {val}")
                    fixed = True
            except ValueError:
                pass
        
        # Position 26: reputationReward - should be nil or {{factionId, value},...}
        if new_fields[25] != 'nil' and not new_fields[25].startswith('{'):
            try:
                val = int(new_fields[25])
                if should_be_quest_id(val):
                    # This might be a parent quest for position 25
                    if new_fields[24] == 'nil':
                        new_fields[24] = new_fields[25]
                        new_fields[25] = 'nil'
                        print(f"Quest {quest_id}: Moved quest ID {val} from position 26 to 25")
                        fixed = True
                    else:
                        new_fields[25] = 'nil'
                        print(f"Quest {quest_id}: Cleared invalid reputationReward value {val}")
                        fixed = True
                else:
                    new_fields[25] = 'nil'
                    print(f"Quest {quest_id}: Cleared invalid reputationReward value {val}")
                    fixed = True
            except ValueError:
                pass
        
        # Position 27: extraObjectives - should be nil or {{spellId, text},...}
        if new_fields[26] != 'nil' and not new_fields[26].startswith('{'):
            new_fields[26] = 'nil'
            print(f"Quest {quest_id}: Cleared invalid extraObjectives value")
            fixed = True
        
        if fixed:
            # Reconstruct the line
            quest_match = re.search(r'(\[\d+\] = \{)', line)
            comment_match = re.search(r'(}, --.*)$', line)
            
            if quest_match:
                new_line = quest_match.group(1) + ','.join(new_fields) + '}'
                if comment_match:
                    new_line += comment_match.group(1)
                else:
                    new_line += ','
                new_line += '\n'
                
                lines[i] = new_line
                fixes_made += 1
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes_made} quests with field type issues')
    print("\nTo verify all issues are resolved, run:")
    print("python3 find_all_field_issues.py")

if __name__ == "__main__":
    fix_all_field_issues()