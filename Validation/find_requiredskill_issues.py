#!/usr/bin/env python3

"""
Find quests with numbers in the requiredSkill field (position 18)
RequiredSkill should be either nil or {skillId, value}
"""

import re

def analyze_quest_structure(line):
    """Parse quest line and return list of fields"""
    # Extract the quest data between outer braces
    match = re.search(r'\[(\d+)\] = \{(.*)\},', line)
    if not match:
        return None, None
    
    quest_id = match.group(1)
    data = '{' + match.group(2) + '}'
    
    # Split by commas at depth 1 (not inside nested structures)
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

def find_requiredskill_issues():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    
    for i, line in enumerate(lines, 1):
        if not line.strip().startswith('[') or '=' not in line:
            continue
            
        # Skip comments
        if line.strip().startswith('--'):
            continue
        
        quest_id, fields = analyze_quest_structure(line)
        if not fields or len(fields) < 18:
            continue
        
        # Check position 18 (requiredSkill) - index 17 in 0-based
        if len(fields) > 17:
            field_18 = fields[17]
            # Check if it's a plain number (not nil, not a pair like {x,y})
            if field_18 and field_18 != 'nil' and not field_18.startswith('{'):
                try:
                    # See if it's a number
                    int(field_18)
                    
                    # Also check what's in position 17 (zoneOrSort)
                    field_17 = fields[16] if len(fields) > 16 else 'missing'
                    
                    issues.append({
                        'quest_id': quest_id,
                        'line': i,
                        'field_17': field_17,
                        'field_18': field_18
                    })
                    
                    print(f"Quest {quest_id} (line {i}):")
                    print(f"  Position 17 (zoneOrSort): {field_17}")
                    print(f"  Position 18 (requiredSkill): {field_18} <- SHOULD BE nil or {{skillId,value}}")
                except ValueError:
                    pass
    
    print(f"\n✅ Found {len(issues)} quests with requiredSkill issues")
    return issues

if __name__ == "__main__":
    find_requiredskill_issues()