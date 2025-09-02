#!/usr/bin/env python3

"""
Balance braces in each quest line to ensure proper syntax
"""

import re

def balance_braces():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        if not line.strip().startswith('[') or '=' not in line:
            continue
            
        # Count braces in this line
        opens = line.count('{')
        closes = line.count('}')
        
        if opens != closes:
            quest_match = re.search(r'\[(\d+)\]', line)
            quest_id = quest_match.group(1) if quest_match else 'unknown'
            
            # If more opens than closes, add closing braces before the final comma
            if opens > closes:
                diff = opens - closes
                # Find the last comma or comment
                if line.rstrip().endswith(','):
                    line = line.rstrip()[:-1] + '}' * diff + ',\n'
                elif ' -- ' in line:
                    parts = line.split(' -- ', 1)
                    parts[0] = parts[0].rstrip()
                    if parts[0].endswith(','):
                        parts[0] = parts[0][:-1] + '}' * diff + ','
                    else:
                        parts[0] = parts[0] + '}' * diff
                    line = parts[0] + ' -- ' + parts[1]
                else:
                    line = line.rstrip() + '}' * diff + ',\n'
                
                lines[i] = line
                fixes_made += 1
                print(f"Fixed quest {quest_id}: added {diff} closing braces")
            
            # If more closes than opens, remove extra closing braces
            elif closes > opens:
                diff = closes - opens
                # Remove extra closing braces
                for _ in range(diff):
                    line = line.replace('}}', '}', 1)
                
                lines[i] = line
                fixes_made += 1
                print(f"Fixed quest {quest_id}: removed {diff} extra closing braces")
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes_made} quests with unbalanced braces')

if __name__ == "__main__":
    balance_braces()