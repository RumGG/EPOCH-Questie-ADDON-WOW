#!/usr/bin/env python3

"""
Fix the remaining type errors found by the validator, especially:
1. Numbers in exclusiveTo field (position 16)
2. Numbers in requiredMinRep field (position 19) 
3. nil in questLevel field (position 5) which should be a number
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

def fix_remaining_errors():
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
        
        # Fix questLevel (position 5) - if nil, set to 1
        if len(new_fields) > 4 and new_fields[4] == 'nil':
            new_fields[4] = '1'  # Default quest level
            fixed = True
            print(f"Quest {quest_id}: Set questLevel to 1 (was nil)")
        
        # Fix exclusiveTo (position 16) - numbers should be nil or wrapped in {}
        if len(new_fields) > 15 and new_fields[15] != 'nil' and not new_fields[15].startswith('{'):
            try:
                val = int(new_fields[15])
                # Large numbers (quest IDs) could be wrapped, small numbers moved
                if val > 1000:
                    # This might be a quest ID that should be wrapped
                    new_fields[15] = '{' + new_fields[15] + '}'
                    print(f"Quest {quest_id}: Wrapped exclusiveTo quest ID {val}")
                else:
                    # Small number - likely belongs elsewhere
                    # Move to position 17 (zoneOrSort) if that's nil
                    if len(new_fields) > 16 and new_fields[16] == 'nil':
                        new_fields[16] = new_fields[15]
                        new_fields[15] = 'nil'
                        print(f"Quest {quest_id}: Moved {val} from exclusiveTo to zoneOrSort")
                    else:
                        new_fields[15] = 'nil'
                        print(f"Quest {quest_id}: Cleared exclusiveTo value {val}")
                fixed = True
            except ValueError:
                pass
        
        # Fix requiredMinRep (position 19) - should be nil or {factionId, value}
        if len(new_fields) > 18 and new_fields[18] != 'nil' and not new_fields[18].startswith('{'):
            try:
                val = int(new_fields[18])
                # Large numbers might be quest IDs for nextQuestInChain (position 22)
                if val > 10000 and len(new_fields) > 21:
                    if new_fields[21] == 'nil':
                        new_fields[21] = new_fields[18]
                        new_fields[18] = 'nil'
                        print(f"Quest {quest_id}: Moved {val} from requiredMinRep to nextQuestInChain")
                    else:
                        new_fields[18] = 'nil'
                        print(f"Quest {quest_id}: Cleared requiredMinRep value {val}")
                else:
                    new_fields[18] = 'nil'
                    print(f"Quest {quest_id}: Cleared requiredMinRep value {val}")
                fixed = True
            except ValueError:
                pass
        
        # Ensure we have at least 30 fields (pad with nil if needed)
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
    
    print(f'\n✅ Fixed {fixes_made} quests with remaining type errors')

if __name__ == "__main__":
    fix_remaining_errors()