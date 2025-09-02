#!/usr/bin/env python3

"""
Module 3: Fix double-brace objectives that need 6-element structure
Pattern: },nil,{{creatures}},nil,nil,nil,nil,nil,nil
Should be: },nil,{{{creatures}},nil,nil,nil,nil,nil},nil,nil,nil,nil,nil,nil
"""

import re

def fix_double_brace_objectives(input_file, output_file):
    """Fix double-brace objectives that need proper structure"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    fixes_made = 0
    quest_fixes = []
    
    for line_num, line in enumerate(lines, 1):
        # Only process quest lines
        if not (line.strip().startswith('[') and '=' in line):
            fixed_lines.append(line)
            continue
            
        # Get quest ID
        quest_match = re.search(r'\[(\d+)\]', line)
        quest_id = quest_match.group(1) if quest_match else f"line {line_num}"
        
        line_fixed = False
        
        # Pattern 1: Double-brace creatures/mobs at objectives position without structure
        # },nil,{{id,count}},nil,nil,nil,nil,nil,nil
        pattern1 = r'},nil,(\{\{[0-9]+,[^}]+(?:\}[^}]*)*?\}\}),nil,nil,nil,nil,nil,nil'
        match1 = re.search(pattern1, line)
        if match1:
            creatures = match1.group(1)
            old = '},nil,' + creatures + ',nil,nil,nil,nil,nil,nil'
            new = '},nil,{' + creatures + ',nil,nil,nil,nil,nil},nil,nil,nil,nil,nil,nil'
            line = line.replace(old, new)
            line_fixed = True
        
        # Pattern 2: Double-brace with items too
        # },nil,{{creatures}},nil,{{items}},nil,nil,nil,nil,nil
        if not line_fixed:
            pattern2 = r'},nil,(\{\{[^}]+(?:\}[^}]*)*?\}\}),nil,(\{\{[^}]+(?:\}[^}]*)*?\}\}),nil,nil,nil,nil,nil'
            match2 = re.search(pattern2, line)
            if match2:
                creatures = match2.group(1)
                items = match2.group(2)
                old = '},nil,' + creatures + ',nil,' + items + ',nil,nil,nil,nil,nil'
                new = '},nil,{' + creatures + ',nil,' + items + ',nil,nil,nil},nil,nil,nil,nil,nil,nil'
                line = line.replace(old, new)
                line_fixed = True
        
        if line_fixed:
            fixes_made += 1
            quest_fixes.append(quest_id)
        
        fixed_lines.append(line)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    return fixes_made, quest_fixes

if __name__ == "__main__":
    # Can be run standalone or use temp file from previous module
    import sys
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "../Database/Epoch/epochQuestDB_temp2.lua"
    
    output_file = "../Database/Epoch/epochQuestDB_temp3.lua"
    
    fixes, quests = fix_double_brace_objectives(input_file, output_file)
    print(f"Module 3: Fixed {fixes} double-brace objectives in {len(quests)} quests")
    if quests:
        print(f"  Quests: {', '.join(quests[:10])}", end='')
        if len(quests) > 10:
            print(f" ... and {len(quests)-10} more")
        else:
            print()