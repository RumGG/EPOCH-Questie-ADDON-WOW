#!/usr/bin/env python3

"""
Fix requiredSourceItems field (position 21) - should be nil or {itemId,...}
When we see small numbers (0,1,2), they're likely flags that belong elsewhere
"""

import re

def fix_requiredsourceitems():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        if not line.strip().startswith('[') or '=' not in line:
            continue
            
        # Skip comments
        if line.strip().startswith('--'):
            continue
        
        # Look for pattern where position 21 has a small number (0,1,2)
        # These are 20 commas, then a number, then comma
        # Count commas to find position 21
        parts = line.split(',')
        
        # Need at least 21 fields
        if len(parts) < 21:
            continue
            
        # Find the quest data part (after the = {)
        quest_match = re.search(r'\[(\d+)\] = \{', line)
        if not quest_match:
            continue
            
        quest_id = quest_match.group(1)
        
        # Check if position 21 (20 commas from start of data) has a plain number
        # Pattern to find position 21 value
        # We need to count fields more carefully due to nested structures
        
        # Use a simpler approach - look for specific patterns
        # Position 21 comes after position 20 (requiredMaxRep)
        # Pattern: ,nil,nil,nil,NUMBER,nil,
        #           19   20        21   22
        
        pattern = r'(,nil,nil,nil,)(\d+)(,nil,)'
        match = re.search(pattern, line)
        
        if match:
            number = int(match.group(2))
            # If it's a small number (0,1,2), it's likely a flag
            if number <= 10:
                original = line
                # Move the number to position 24 (specialFlags) if that's 0
                # Pattern: NUMBER,nil,FLAGS,SPECIALFLAGS
                #           21    22   23      24
                
                # Replace the number in position 21 with nil
                new_pattern = match.group(1) + 'nil' + match.group(3)
                line = line.replace(match.group(0), new_pattern)
                
                # If position 24 is 0, replace it with our number
                if ',0,' in line or ',0}' in line:
                    # Find the 0 in position 24 (after position 23)
                    # Count from the pattern we just fixed
                    parts_after = line.split(new_pattern)[1]
                    if parts_after.startswith('nil,'):
                        # Position 22 is nil, next is 23, then 24
                        subparts = parts_after.split(',')
                        if len(subparts) >= 3:
                            # Check if position 24 (index 2) is 0
                            if subparts[2] == '0':
                                # Replace it
                                line = line.replace(new_pattern + 'nil,' + subparts[1] + ',0', 
                                                  new_pattern + 'nil,' + subparts[1] + ',' + str(number))
                
                if line != original:
                    lines[i] = line
                    fixes_made += 1
                    print(f"Fixed quest {quest_id}: moved {number} from requiredSourceItems to specialFlags")
            
            # If it's a large number (quest ID), move to position 22
            elif number > 10000:
                original = line
                # Move to position 22 (nextQuestInChain) if that's nil
                # Replace position 21 with nil, position 22 with the number
                new_pattern = match.group(1) + 'nil,' + str(number)
                line = line.replace(match.group(0), new_pattern + ',')
                
                if line != original:
                    lines[i] = line
                    fixes_made += 1
                    print(f"Fixed quest {quest_id}: moved {number} from requiredSourceItems to nextQuestInChain")
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes_made} quests with requiredSourceItems issues')

if __name__ == "__main__":
    fix_requiredsourceitems()