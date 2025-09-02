#!/usr/bin/env python3

"""
Fix all quests with numbers in the exclusiveTo field (position 16)
The number should be moved to position 17 (zoneOrSort)
"""

import re

def fix_all_exclusiveto():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        if not line.strip().startswith('[') or '=' not in line:
            continue
            
        # Skip comments and empty lines
        if line.strip().startswith('--'):
            continue
            
        # Look for pattern: ,nil,nil,nil,nil,nil,NUMBER,nil,
        # This indicates position 16 has a number instead of nil
        if re.search(r',nil,nil,nil,nil,nil,(\d+),nil,', line):
            original = line
            # Replace the pattern to move the number to position 17
            # From: ,nil,nil,nil,nil,nil,NUMBER,nil,
            # To:   ,nil,nil,nil,nil,nil,nil,NUMBER,
            line = re.sub(r'(,nil,nil,nil,nil,nil,)(\d+)(,nil,)', r'\1nil,\2', line)
            
            if line != original:
                lines[i] = line
                fixes_made += 1
                quest_match = re.search(r'\[(\d+)\]', line)
                if quest_match:
                    print(f"Fixed quest {quest_match.group(1)}")
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes_made} quests with exclusiveTo issues')

if __name__ == "__main__":
    fix_all_exclusiveto()