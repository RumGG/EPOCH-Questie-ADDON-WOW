#!/usr/bin/env python3

"""
Fix double-nested creature objectives like {{40,10},{{476,5}}}
Should be {{40,10},{476,5}}
"""

import re

def fix_double_nested_creatures():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        if not line.strip().startswith('[') or '=' not in line:
            continue
        
        original = line
        quest_match = re.search(r'\[(\d+)\]', line)
        quest_id = quest_match.group(1) if quest_match else 'unknown'
        
        # Pattern: {{num,num,optional},{{num,num,optional}}
        # This catches double-nested entries in objectives
        # We need to remove the extra braces from subsequent entries
        
        # Fix pattern: },{{ -> },{
        if '},{{' in line:
            # But only in the objectives field area
            # Check if this is likely in the objectives field by looking at context
            # Objectives come after position 9, so after the 9th comma
            
            # Count commas to find where objectives likely are
            parts = line.split(',')
            if len(parts) > 10:
                # Find and fix the pattern
                fixed = line
                
                # Pattern 1: creature objectives like {{40,10},{{476,5}}}
                pattern = r'(\{\{[0-9]+,[0-9]+[^}]*\}),\{\{([0-9]+,[0-9]+[^}]*\}\})'
                replacement = r'\1,{\2'
                fixed = re.sub(pattern, replacement, fixed)
                
                # Pattern 2: with quoted text {{40,10,"Name"},{{476,5,"Name"}}}
                pattern = r'(\{\{[0-9]+,[0-9]+,"[^"]*"\}),\{\{([0-9]+,[0-9]+,"[^"]*"\}\})'
                replacement = r'\1,{\2'
                fixed = re.sub(pattern, replacement, fixed)
                
                # Pattern 3: simpler number pairs
                pattern = r'(\{[0-9]+,[0-9]+\}),\{\{([0-9]+,[0-9]+\})'
                replacement = r'\1,{\2'
                fixed = re.sub(pattern, replacement, fixed)
                
                if fixed != original:
                    lines[i] = fixed
                    fixes_made += 1
                    print(f"Fixed quest {quest_id}: removed double-nesting in objectives")
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes_made} quests with double-nested creature objectives')

if __name__ == "__main__":
    fix_double_nested_creatures()