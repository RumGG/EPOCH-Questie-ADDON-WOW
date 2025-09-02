#!/usr/bin/env python3

"""
Final fix for triple-nested objectives structures.
Targets remaining {{{ patterns and fixes them properly.
"""

import re

def fix_final_nesting():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        if '{{{' not in line:
            continue
            
        original = line
        quest_match = re.search(r'\[(\d+)\]', line)
        quest_id = quest_match.group(1) if quest_match else 'unknown'
        
        # Fix triple-nested structures
        # Pattern 1: {{{id,count},{id,count},...}} -> {{id,count},{id,count},...}
        # Pattern 2: {{{id,count,"text"},...}} -> {{id,count,"text"},...}
        
        fixed_line = line
        
        # Replace {{{ with {{ and }}} with }}
        # But be careful not to break properly nested structures
        
        # Count the occurrences and fix systematically
        while '{{{' in fixed_line:
            # Find the position of {{{
            start = fixed_line.find('{{{')
            if start == -1:
                break
                
            # Find the matching closing braces
            depth = 3  # We start with {{{
            pos = start + 3
            while pos < len(fixed_line) and depth > 0:
                if fixed_line[pos] == '{':
                    depth += 1
                elif fixed_line[pos] == '}':
                    depth -= 1
                pos += 1
            
            # Extract the content
            content = fixed_line[start:pos]
            
            # Fix it - remove one level of braces
            if content.startswith('{{{') and content.endswith('}}}'):
                fixed_content = '{{' + content[3:-3] + '}}'
            elif content.startswith('{{{') and content.endswith('}}'):
                fixed_content = '{{' + content[3:-2] + '}'
            else:
                # Can't fix this pattern safely
                break
            
            # Replace in the line
            fixed_line = fixed_line[:start] + fixed_content + fixed_line[pos:]
        
        if fixed_line != original:
            lines[i] = fixed_line
            fixes_made += 1
            print(f"Fixed quest {quest_id}: removed triple nesting")
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes_made} quests with triple-nested structures')

if __name__ == "__main__":
    fix_final_nesting()