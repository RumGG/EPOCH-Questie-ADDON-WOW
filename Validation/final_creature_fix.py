#!/usr/bin/env python3

"""
Final fix for the 18 remaining quests with creature objectives issues
"""

import re

def fix_final_creatures():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes = 0
    
    for i, line in enumerate(lines):
        # Pattern: {{{creature1},{creature2}}} needs to be {{{creature1}},{{creature2}}}
        if re.search(r'\{\{\{[0-9]+,[0-9]+,\"[^\"]+\"\},\{[0-9]+,[0-9]+,\"[^\"]+\"\}', line):
            original = line
            
            # Find and replace each occurrence
            # Match: {{{num,num,"text"},{num,num,"text"}...}}
            def fix_match(m):
                content = m.group(0)
                # Extract just the creatures part
                inner = content[3:-2]  # Remove {{{ and }}
                
                # Split by },{ to get individual creatures
                creatures = inner.split('},{')
                
                # Rebuild with proper bracing
                fixed_creatures = []
                for c in creatures:
                    c = c.strip('{}')  # Remove any extra braces
                    fixed_creatures.append(f'{{{c}}}')
                
                return '{' + ','.join(fixed_creatures) + '}'
            
            # Apply the fix
            line = re.sub(
                r'\{\{\{[0-9]+,[0-9]+,\"[^\"]+\"\}(?:,\{[0-9]+,[0-9]+,\"[^\"]+\"\})+\}\}',
                fix_match,
                line
            )
            
            if line != original:
                lines[i] = line
                quest_id = re.search(r'\[(\d+)\]', line)
                if quest_id:
                    print(f'Fixed quest {quest_id.group(1)}')
                    fixes += 1
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes} quests')

if __name__ == "__main__":
    fix_final_creatures()