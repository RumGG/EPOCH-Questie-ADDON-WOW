#!/usr/bin/env python3

"""
Fix quests with zone IDs in requiredSkill field (position 18)
The zone ID should be in position 17 (zoneOrSort), not 18 (requiredSkill)
"""

import re

def fix_requiredskill():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        if not line.strip().startswith('[') or '=' not in line:
            continue
            
        # Skip comments
        if line.strip().startswith('--'):
            continue
        
        # Look for pattern where position 17 is nil and position 18 has a number
        # Pattern: ,nil,nil,nil,nil,nil,nil,nil,NUMBER,
        # This indicates zoneOrSort (17) is nil and requiredSkill (18) has a zone ID
        match = re.search(r'(,nil,nil,nil,nil,nil,nil,nil,)(\d+)(,)', line)
        if match:
            original = line
            zone_id = match.group(2)
            
            # Only fix if the number looks like a zone ID (not a skill requirement)
            # Zone IDs are typically 1-2000, skill requirements would be paired {skillId, value}
            zone_num = int(zone_id)
            if zone_num < 3000:  # Likely a zone ID, not a skill
                # Replace to move the number from position 18 to position 17
                # From: ,nil,nil,nil,nil,nil,nil,nil,NUMBER,
                # To:   ,nil,nil,nil,nil,nil,nil,NUMBER,nil,
                line = line.replace(f'{match.group(1)}{zone_id},', f'{match.group(1)[:-4]}{zone_id},nil,')
                
                if line != original:
                    lines[i] = line
                    fixes_made += 1
                    quest_match = re.search(r'\[(\d+)\]', line)
                    if quest_match:
                        print(f"Fixed quest {quest_match.group(1)}: moved zone {zone_id} from requiredSkill to zoneOrSort")
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes_made} quests with requiredSkill issues')

if __name__ == "__main__":
    fix_requiredskill()