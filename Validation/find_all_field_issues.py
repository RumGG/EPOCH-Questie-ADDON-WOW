#!/usr/bin/env python3

"""
Find ALL quests with numbers in fields that should be nil or arrays
"""

import re

def analyze_quest_structure(line):
    """Parse quest line and return list of fields"""
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

def find_all_field_issues():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Fields that should be nil or arrays, not plain numbers
    # Position -> Field Name
    array_fields = {
        12: "preQuestGroup",
        13: "preQuestSingle", 
        14: "childQuests",
        15: "inGroupWith",
        16: "exclusiveTo",
        18: "requiredSkill",  # Should be {skillId, value} or nil
        19: "requiredMinRep",  # Should be {factionId, value} or nil
        20: "requiredMaxRep",  # Should be {factionId, value} or nil
        21: "requiredSourceItems",  # Should be {itemId,...} or nil
        26: "reputationReward",  # Should be {{factionId, value},...} or nil
        27: "extraObjectives"  # Should be {{spellId, text},...} or nil
    }
    
    issues = {}
    
    for i, line in enumerate(lines, 1):
        if not line.strip().startswith('[') or '=' not in line:
            continue
            
        if line.strip().startswith('--'):
            continue
        
        quest_id, fields = analyze_quest_structure(line)
        if not fields:
            continue
        
        # Check each field that should be nil or array
        for pos, field_name in array_fields.items():
            if len(fields) > pos - 1:  # Convert to 0-based index
                field_value = fields[pos - 1]
                # Check if it's a plain number (not nil, not array/table)
                if field_value and field_value != 'nil' and not field_value.startswith('{'):
                    try:
                        int(field_value)
                        if field_name not in issues:
                            issues[field_name] = []
                        issues[field_name].append({
                            'quest_id': quest_id,
                            'line': i,
                            'value': field_value,
                            'position': pos
                        })
                    except ValueError:
                        pass
    
    # Print summary
    print("=== Field Issues Summary ===\n")
    total_issues = 0
    for field_name, quest_list in sorted(issues.items()):
        print(f"{field_name} (position {quest_list[0]['position']}): {len(quest_list)} quests with issues")
        total_issues += len(quest_list)
        # Show first few examples
        for quest in quest_list[:3]:
            print(f"  - Quest {quest['quest_id']} (line {quest['line']}): has value {quest['value']}")
        if len(quest_list) > 3:
            print(f"  ... and {len(quest_list) - 3} more")
        print()
    
    print(f"Total issues found: {total_issues}")
    
    # Save detailed list for requiredSourceItems (position 21)
    if 'requiredSourceItems' in issues:
        print("\n=== RequiredSourceItems Issues (Position 21) ===")
        for quest in issues['requiredSourceItems']:
            print(f"Quest {quest['quest_id']} (line {quest['line']}): has {quest['value']} in position 21")

if __name__ == "__main__":
    find_all_field_issues()