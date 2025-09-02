#!/usr/bin/env python3

"""
Fix objectives structure issues where creatures lack proper triple-brace nesting
The objectives field should be: {creatures, objects, items, reputation, killCredit, spells}
Where creatures should be {{{id,count,"name"},...}} not {{id,count,"name"},...}
"""

import re

def fix_objectives_structure():
    """Fix objectives that have wrong nesting level"""
    
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        # Pattern to find: ,nil,{{number,number,"text"}
        # This indicates creatures field without proper triple braces
        # We need to wrap it with an extra set of braces
        
        # Match pattern like: ,nil,{{2523,8,"Twilight Thug"},{2525,8,"Twilight Disciple"}}
        # Should become: ,nil,{{{2523,8,"Twilight Thug"},{2525,8,"Twilight Disciple"}}}
        
        pattern = r',nil,({{[0-9]+,[0-9]+,"[^"]+"}(?:,{[0-9]+,[0-9]+,"[^"]+"})*),'
        match = re.search(pattern, line)
        
        if match:
            old_objectives = match.group(1)
            # Add extra braces around the creatures
            new_objectives = '{' + old_objectives + '}'
            
            quest_match = re.search(r'\[(\d+)\]', line)
            if quest_match:
                quest_id = quest_match.group(1)
                
                # Replace in the line
                lines[i] = line.replace(',nil,' + old_objectives + ',', ',nil,' + new_objectives + ',')
                fixes_made += 1
                print(f"Fixed quest {quest_id}")
    
    # Save the fixed file
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n✅ Fixed {fixes_made} quests with objectives structure issues")
    
    return fixes_made

if __name__ == "__main__":
    fix_objectives_structure()