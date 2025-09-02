#!/usr/bin/env python3

"""
Fix objectives field syntax errors where closing braces are misplaced
"""

import re

def fix_objectives_syntax():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        if not line.strip().startswith('[') or '=' not in line:
            continue
            
        # Look for the broken pattern where objectives field ends too early
        # Pattern: },nil,nil,nil,nil,nil},nil,nil,nil,
        # This indicates the objectives field is closing too early
        
        if '},nil,nil,nil,nil,nil},nil,nil,nil,' in line:
            original = line
            quest_match = re.search(r'\[(\d+)\]', line)
            quest_id = quest_match.group(1) if quest_match else 'unknown'
            
            # Fix by moving the closing brace to the right position
            # Replace },nil,nil,nil,nil,nil},nil with ,nil,nil,nil,nil,nil},nil
            line = line.replace('},nil,nil,nil,nil,nil},nil,nil,nil,', ',nil,nil,nil,nil,nil},nil,nil,nil,')
            
            if line != original:
                lines[i] = line
                fixes_made += 1
                print(f"Fixed quest {quest_id}: corrected objectives field closing brace")
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes_made} quests with objectives syntax errors')

if __name__ == "__main__":
    fix_objectives_syntax()