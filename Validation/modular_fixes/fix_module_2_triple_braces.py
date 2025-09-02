#!/usr/bin/env python3

"""
Module 2: Fix triple-brace patterns in items/objects
Pattern: ,{{{itemId,count}}} -> ,{{itemId,count}}
"""

import re

def fix_triple_brace_items(input_file, output_file):
    """Fix triple-brace patterns in items and objects"""
    
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
        
        if '{{{' not in line:
            fixed_lines.append(line)
            continue
            
        # Get quest ID
        quest_match = re.search(r'\[(\d+)\]', line)
        quest_id = quest_match.group(1) if quest_match else f"line {line_num}"
        
        line_fixed = False
        
        # Pattern 1: Triple-braced items in objectives (not part of 6-element structure)
        # ,{{{itemId,count}}} or ,{{{itemId,count,"name"}}}
        pattern1 = r',\{\{\{(\d+,\d+(?:,"[^"]*")?)\}\}\}'
        matches = re.findall(pattern1, line)
        for match in matches:
            old = ',{{{' + match + '}}}'
            new = ',{{' + match + '}}'
            if old in line:
                line = line.replace(old, new)
                line_fixed = True
        
        # Pattern 2: Triple-braced with nil counts
        # {{{id,nil}}} -> {{id,nil}}
        pattern2 = r'\{\{\{(\d+,nil)\}\}\}'
        matches = re.findall(pattern2, line)
        for match in matches:
            old = '{{{' + match + '}}}'
            new = '{{' + match + '}}'
            if old in line:
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
        input_file = "../Database/Epoch/epochQuestDB_temp1.lua"
    
    output_file = "../Database/Epoch/epochQuestDB_temp2.lua"
    
    fixes, quests = fix_triple_brace_items(input_file, output_file)
    print(f"Module 2: Fixed {fixes} triple-brace patterns in {len(quests)} quests")
    if quests:
        print(f"  Quests: {', '.join(quests[:10])}", end='')
        if len(quests) > 10:
            print(f" ... and {len(quests)-10} more")
        else:
            print()