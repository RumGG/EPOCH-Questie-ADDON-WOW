#!/usr/bin/env python3

"""
Module 1: Fix quadruple-brace patterns
Pattern: {{{{...}} -> {{...}}
"""

import re
import os

def fix_quadruple_braces(input_file, output_file):
    """Fix quadruple-brace patterns in objectives"""
    
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
        
        if '{{{{' not in line:
            fixed_lines.append(line)
            continue
            
        # Get quest ID
        quest_match = re.search(r'\[(\d+)\]', line)
        quest_id = quest_match.group(1) if quest_match else f"line {line_num}"
        
        # Fix wrapped objectives: {{{{creatures}},nil,nil,nil,nil,nil},nil,nil}
        # Should be: {{{creatures}},nil,nil,nil,nil,nil}
        pattern1 = r'},nil,\{\{\{\{([^}]+(?:\}[^}]*)*?)\}\},nil,nil,nil,nil,nil\},nil,nil\}'
        match1 = re.search(pattern1, line)
        if match1:
            creatures = match1.group(1)
            old = '},nil,{{{{' + creatures + '}},nil,nil,nil,nil,nil},nil,nil}'
            new = '},nil,{{{' + creatures + '}},nil,nil,nil,nil,nil}'
            line = line.replace(old, new)
            fixes_made += 1
            quest_fixes.append(quest_id)
        else:
            # Fix other quadruple patterns
            # Simple replacement for standalone quadruple braces
            if line.count('{{{{') == line.count('}}}}'):
                line = line.replace('{{{{', '{{')
                line = line.replace('}}}}', '}}')
                fixes_made += 1
                quest_fixes.append(quest_id)
        
        fixed_lines.append(line)
    
    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    return fixes_made, quest_fixes

if __name__ == "__main__":
    input_file = "../Database/Epoch/epochQuestDB.lua"
    output_file = "../Database/Epoch/epochQuestDB_temp1.lua"
    
    fixes, quests = fix_quadruple_braces(input_file, output_file)
    print(f"Module 1: Fixed {fixes} quadruple-brace patterns in {len(quests)} quests")
    if quests:
        print(f"  Quests: {', '.join(quests[:10])}", end='')
        if len(quests) > 10:
            print(f" ... and {len(quests)-10} more")
        else:
            print()