#!/usr/bin/env python3

"""
Fix objectives field issues:
1. Objectives must have exactly 6 elements
2. Creatures missing count values need them added
3. Remove extra nils from objectives fields
"""

import re

def fix_objectives_fields():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        if not line.strip().startswith('[') or '=' not in line:
            continue
            
        # Skip comments and empty lines
        if line.strip().startswith('--'):
            continue
            
        original = line
        
        # Find objectives field (position 10)
        # Pattern to find the objectives field - it comes after 9 other fields
        objectives_match = re.search(r'(,nil,)(\{[^}]*(?:\{[^}]*\}[^}]*)*\})([,\}])', line)
        
        if objectives_match:
            objectives_str = objectives_match.group(2)
            
            # Count the number of top-level elements in objectives
            # Should be exactly 6: creatures, objects, items, reputation, killCredit, spells
            
            # Check if objectives has too many nil elements
            if ',nil,nil,nil,nil,nil,nil' in objectives_str:
                # Has 7 nils, should be 6
                line = line.replace(',nil,nil,nil,nil,nil,nil}', ',nil,nil,nil,nil,nil}')
                fixes_made += 1
                quest_id = re.search(r'\[(\d+)\]', line)
                if quest_id:
                    print(f"Fixed quest {quest_id.group(1)} - removed extra nil from objectives")
            
            # Check for creatures missing count values
            # Pattern: {{id,"name"}} should be {{id,count,"name"}}
            creature_pattern = r'\{\{(\d+),"([^"]+)"\}\}'
            if re.search(creature_pattern, objectives_str):
                def add_count(m):
                    return f'{{{{{m.group(1)},1,"{m.group(2)}"}}}}'
                objectives_str = re.sub(creature_pattern, add_count, objectives_str)
                line = line[:objectives_match.start(2)] + objectives_str + line[objectives_match.end(2):]
                fixes_made += 1
                quest_id = re.search(r'\[(\d+)\]', line)
                if quest_id:
                    print(f"Fixed quest {quest_id.group(1)} - added count to creatures")
            
            # Check for triple-nested items (common mistake)
            # {{{item,count,"name"}}} should be {{item,count,"name"}}
            if re.search(r'\{\{\{\d+,\d+,"[^"]+"\}\}(?:,|$)', objectives_str):
                objectives_str = re.sub(r'\{\{\{(\d+,\d+,"[^"]+")\}\}', r'{{\1}}', objectives_str)
                line = line[:objectives_match.start(2)] + objectives_str + line[objectives_match.end(2):]
                fixes_made += 1
                quest_id = re.search(r'\[(\d+)\]', line)
                if quest_id:
                    print(f"Fixed quest {quest_id.group(1)} - fixed triple-nested items")
        
        if line != original:
            lines[i] = line
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes_made} objectives field issues')

if __name__ == "__main__":
    fix_objectives_fields()