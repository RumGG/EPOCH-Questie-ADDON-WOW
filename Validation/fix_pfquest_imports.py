#!/usr/bin/env python3

"""
Fix pfQuest imported quests that have malformed objectives
"""

import re

def fix_pfquest_imports():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        if '-- From pfQuest' not in line:
            continue
            
        original = line
        
        # Fix pattern where objectives has wrong nesting
        # Example: {{{40,1},{476,1},nil,nil},nil,nil,nil,nil,nil,nil
        # Should be: {{{40,1,"creature1"},{476,1,"creature2"}},nil,nil,nil,nil,nil}
        
        # Pattern 1: Creatures with missing count/name
        line = re.sub(r'\{\{\{(\d+),(\d+)\},\{(\d+),(\d+)\},nil,nil\}', 
                     r'{{{{\1,\2,"creature"}},{{\3,\4,"creature"}}},nil,nil,nil,nil,nil}', line)
        
        # Pattern 2: Single creature with missing name
        line = re.sub(r'\{\{\{(\d+),(\d+),nil,nil\}', 
                     r'{{{\1,\2,"creature"},nil,nil,nil,nil,nil}', line)
        
        # Pattern 3: Items missing description - single item
        line = re.sub(r'\{nil,nil,\{\{(\d+),(\d+)\}\}', 
                     r'{nil,nil,{{\1,\2,"item"}}', line)
        
        # Pattern 4: Multiple items missing descriptions
        line = re.sub(r'\{\{(\d+),(\d+)\},\{(\d+),(\d+)\},\{(\d+),(\d+)\},\{(\d+),(\d+)\}\}', 
                     r'{{\1,\2,"item1"},{{\3,\4,"item2"},{{\5,\6,"item3"},{{\7,\8,"item4"}}', line)
        
        # Pattern 5: Two items
        line = re.sub(r'\{\{(\d+),(\d+)\},\{(\d+),(\d+)\}\}', 
                     r'{{\1,\2,"item1"},{{\3,\4,"item2"}}', line)
                     
        # Pattern 6: Three items
        line = re.sub(r'\{\{(\d+),(\d+)\},\{(\d+),(\d+)\},\{(\d+),(\d+)\}\}', 
                     r'{{\1,\2,"item1"},{{\3,\4,"item2"},{{\5,\6,"item3"}}', line)
        
        # Fix excessive nils after objectives that break the 30-field structure
        # Pattern: },nil,nil,nil,nil,nil,nil,nil,nil (too many fields)
        # Should end with just the right number of fields
        if re.search(r'},nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,\d+,', line):
            # This has way too many nils in objectives field
            line = re.sub(r'(}\),nil,)nil,nil,nil,nil,nil,nil,nil,(nil,nil,nil,nil,nil,\d+)', r'\1\2', line)
            
        if line != original:
            lines[i] = line
            fixes_made += 1
            quest_id = re.search(r'\[(\d+)\]', line)
            if quest_id:
                print(f"Fixed quest {quest_id.group(1)}")
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes_made} pfQuest imports')

if __name__ == "__main__":
    fix_pfquest_imports()