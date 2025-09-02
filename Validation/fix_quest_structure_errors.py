#!/usr/bin/env python3

"""
Fix quest structure errors where objectives or other array fields are malformed.
The error "bad argument #1 to 'rshift' (number expected, got table)" happens when
Questie tries to process malformed data structures.
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
    in_string = False
    escape = False
    
    for char in data[1:-1]:  # Skip outer braces
        if escape:
            current += char
            escape = False
            continue
            
        if char == '\\':
            escape = True
            current += char
            continue
            
        if char == '"' and not escape:
            in_string = not in_string
            current += char
        elif not in_string:
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
        else:
            current += char
            
    if current:
        parts.append(current.strip())
    
    return quest_id, parts

def fix_objectives_field(objectives_str):
    """Fix objectives field to have exactly 6 elements"""
    if objectives_str == 'nil':
        return 'nil'
    
    # Parse the objectives structure
    if not objectives_str.startswith('{'):
        return 'nil'
    
    # Remove outer braces
    inner = objectives_str[1:-1] if objectives_str.endswith('}') else objectives_str[1:]
    
    # Split into parts
    parts = []
    current = ""
    depth = 0
    for char in inner:
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
    
    # Ensure we have exactly 6 elements
    while len(parts) < 6:
        parts.append('nil')
    
    # If we have more than 6, truncate
    parts = parts[:6]
    
    return '{' + ','.join(parts) + '}'

def fix_quest_structure():
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
        
        # Fix objectives field (position 10)
        if len(new_fields) > 9 and new_fields[9] != 'nil':
            objectives = new_fields[9]
            if objectives.startswith('{'):
                # Count the number of top-level elements
                fixed_objectives = fix_objectives_field(objectives)
                if fixed_objectives != objectives:
                    new_fields[9] = fixed_objectives
                    fixed = True
                    print(f"Quest {quest_id}: Fixed objectives structure")
        
        # Fix preQuestGroup (position 12) - should be nil or {questId,...}
        if len(new_fields) > 11 and new_fields[11] != 'nil':
            prequests = new_fields[11]
            # Check if it contains nested arrays like {{questId}}
            if '{{' in prequests:
                # Flatten nested arrays
                prequests = prequests.replace('{{', '{').replace('}}', '}')
                new_fields[11] = prequests
                fixed = True
                print(f"Quest {quest_id}: Fixed preQuestGroup nesting")
        
        # Fix preQuestSingle (position 13) - should be nil or {questId,...}
        if len(new_fields) > 12 and new_fields[12] != 'nil':
            prequests = new_fields[12]
            if '{{' in prequests:
                prequests = prequests.replace('{{', '{').replace('}}', '}')
                new_fields[12] = prequests
                fixed = True
                print(f"Quest {quest_id}: Fixed preQuestSingle nesting")
        
        # Fix childQuests (position 14) - should be nil or {questId,...}
        if len(new_fields) > 13 and new_fields[13] != 'nil':
            childquests = new_fields[13]
            if '{{' in childquests:
                childquests = childquests.replace('{{', '{').replace('}}', '}')
                new_fields[13] = childquests
                fixed = True
                print(f"Quest {quest_id}: Fixed childQuests nesting")
        
        # Ensure we have at least 30 fields
        while len(new_fields) < 30:
            new_fields.append('nil')
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
    
    print(f'\n✅ Fixed {fixes_made} quests with structure errors')

if __name__ == "__main__":
    fix_quest_structure()