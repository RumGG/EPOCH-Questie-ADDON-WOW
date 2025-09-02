#!/usr/bin/env python3

"""
Fix ONLY the creature objectives that have multiple creatures without proper individual bracing
Pattern to fix: {{creature1,count,"name"},{creature2,count,"name"}}
Should become: {{{creature1,count,"name"}},{{creature2,count,"name"}}}
"""

import re

def fix_creature_objectives():
    """Fix creature objectives that need individual bracing"""
    
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        # Skip quests we already fixed
        if '[26202]' in line or '[26204]' in line:
            continue
            
        # Look for pattern: ,nil,{{number,number,"text"},{number,number,"text"}...}
        # This is creatures without proper individual bracing
        
        # Find the objectives field with multiple creatures
        match = re.search(r',nil,({{(?:\d+,\d+,"[^"]+"),(?:{?\d+,\d+,"[^"]+")}*}),', line)
        
        if match:
            old_objectives = match.group(1)
            
            # Parse out individual creatures
            creature_pattern = r'{(\d+,\d+,"[^"]+")}'
            creatures = re.findall(creature_pattern, old_objectives)
            
            if len(creatures) > 1:
                # Build the fixed version with each creature in its own braces
                fixed_creatures = ','.join([f'{{{creature}}}' for creature in creatures])
                new_objectives = f'{{{fixed_creatures}}}'
                
                # Replace in the line
                lines[i] = line.replace(f',nil,{old_objectives},', f',nil,{new_objectives},')
                
                quest_match = re.search(r'\[(\d+)\]', line)
                if quest_match:
                    fixes_made += 1
                    print(f"Fixed quest {quest_match.group(1)}")
    
    # Save the fixed file
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n✅ Fixed {fixes_made} quests with creature objectives issues")
    
    return fixes_made

if __name__ == "__main__":
    fix_creature_objectives()