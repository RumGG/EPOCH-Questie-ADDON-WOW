#!/usr/bin/env python3

"""
Fix ALL field type issues where numbers appear in fields that should be nil or arrays
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

def fix_field_types():
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
        
        # Fix each problematic field
        # Most of these numbers seem to be flags that belong in position 23 or 24
        # Or quest IDs that belong in position 22
        
        # Position 14 (childQuests) - should be nil or {questId,...}
        if len(new_fields) > 13 and new_fields[13] != 'nil' and not new_fields[13].startswith('{'):
            try:
                val = int(new_fields[13])
                # This looks like a zone ID that should be in position 17
                if val > 0 and val < 2000:
                    # Move to position 17 if that's nil
                    if len(new_fields) > 16 and new_fields[16] == 'nil':
                        new_fields[16] = new_fields[13]
                        new_fields[13] = 'nil'
                        fixed = True
            except ValueError:
                pass
        
        # Position 16 (exclusiveTo) - should be nil or {questId,...}
        if len(new_fields) > 15 and new_fields[15] != 'nil' and not new_fields[15].startswith('{'):
            try:
                val = int(new_fields[15])
                # Move to position 17 if that's nil
                if len(new_fields) > 16 and new_fields[16] == 'nil':
                    new_fields[16] = new_fields[15]
                    new_fields[15] = 'nil'
                    fixed = True
            except ValueError:
                pass
        
        # Position 18 (requiredSkill) - should be nil or {skillId, value}
        if len(new_fields) > 17 and new_fields[17] != 'nil' and not new_fields[17].startswith('{'):
            try:
                val = int(new_fields[17])
                # This is likely a zone ID that belongs in position 17
                if val < 2000 and len(new_fields) > 16 and new_fields[16] == 'nil':
                    new_fields[16] = new_fields[17]
                    new_fields[17] = 'nil'
                    fixed = True
            except ValueError:
                pass
        
        # Position 19 (requiredMinRep) - should be nil or {factionId, value}
        if len(new_fields) > 18 and new_fields[18] != 'nil' and not new_fields[18].startswith('{'):
            try:
                val = int(new_fields[18])
                # Large numbers might be quest IDs for position 22
                if val > 10000 and len(new_fields) > 21 and new_fields[21] == 'nil':
                    new_fields[21] = new_fields[18]
                    new_fields[18] = 'nil'
                    fixed = True
                else:
                    # Otherwise just clear it
                    new_fields[18] = 'nil'
                    fixed = True
            except ValueError:
                pass
        
        # Position 20 (requiredMaxRep) - should be nil or {factionId, value}
        if len(new_fields) > 19 and new_fields[19] != 'nil' and not new_fields[19].startswith('{'):
            try:
                val = int(new_fields[19])
                # Small numbers (0,1,2) are likely flags for position 23 or 24
                if val <= 10:
                    # Move to position 23 (questFlags) if it's nil
                    if len(new_fields) > 22 and new_fields[22] == 'nil':
                        new_fields[22] = new_fields[19]
                        new_fields[19] = 'nil'
                        fixed = True
                    else:
                        new_fields[19] = 'nil'
                        fixed = True
            except ValueError:
                pass
        
        # Position 21 (requiredSourceItems) - should be nil or {itemId,...}
        if len(new_fields) > 20 and new_fields[20] != 'nil' and not new_fields[20].startswith('{'):
            try:
                val = int(new_fields[20])
                # Large numbers might be quest IDs for position 22
                if val > 10000 and len(new_fields) > 21 and new_fields[21] == 'nil':
                    new_fields[21] = new_fields[20]
                    new_fields[20] = 'nil'
                    fixed = True
                elif val <= 10:
                    # Small numbers are likely flags - move to position 24 (specialFlags)
                    if len(new_fields) > 23 and new_fields[23] == 'nil':
                        new_fields[23] = new_fields[20]
                        new_fields[20] = 'nil'
                        fixed = True
                    else:
                        new_fields[20] = 'nil'
                        fixed = True
                else:
                    new_fields[20] = 'nil'
                    fixed = True
            except ValueError:
                pass
        
        # Position 26 (reputationReward) - should be nil or {{factionId, value},...}
        if len(new_fields) > 25 and new_fields[25] != 'nil' and not new_fields[25].startswith('{'):
            try:
                val = int(new_fields[25])
                # Large numbers might be quest IDs
                if val > 10000:
                    # This might be a parent quest for position 25
                    if len(new_fields) > 24 and new_fields[24] == 'nil':
                        new_fields[24] = new_fields[25]
                        new_fields[25] = 'nil'
                        fixed = True
                    else:
                        new_fields[25] = 'nil'
                        fixed = True
                else:
                    new_fields[25] = 'nil'
                    fixed = True
            except ValueError:
                pass
        
        # Position 27 (extraObjectives) - should be nil or {{spellId, text},...}
        if len(new_fields) > 26 and new_fields[26] != 'nil' and not new_fields[26].startswith('{'):
            new_fields[26] = 'nil'
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
                print(f"Fixed quest {quest_id}")
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes_made} quests with field type issues')

if __name__ == "__main__":
    fix_field_types()