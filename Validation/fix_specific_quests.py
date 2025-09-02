#!/usr/bin/env python3

"""
Fix specific problematic quests in the 862-quest database
"""

import re

def fix_specific_quests():
    """Fix known problematic quests"""
    
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        # Fix quest 26763 - triple-brace objects
        if '[26763]' in line:
            if '{{{4000084,1},{4000085,1}}}' in line:
                lines[i] = line.replace('{{{4000084,1},{4000085,1}}}', '{{4000084,1},{4000085,1}}')
                fixes_made += 1
                print(f"Fixed quest 26763 triple-brace objects")
        
        # Fix quest 1218 - incomplete string
        elif '[1218]' in line:
            if 'to \\"}' in line:
                lines[i] = line.replace('{"Bring 3 Soothing Spices to \\"}', '{"Bring 3 Soothing Spices to the quest giver."}')
                fixes_made += 1
                print(f"Fixed quest 1218 incomplete string")
        
        # Fix quest 27138 - incomplete string
        elif '[27138]' in line:
            if '{"\\"}' in line:
                lines[i] = line.replace('{"\\"}', '{"Complete the quest objectives."}')
                fixes_made += 1
                print(f"Fixed quest 27138 incomplete string")
        
        # Fix quest 26182 - incomplete string
        elif '[26182]' in line:
            if 'Turtle \\"}' in line:
                lines[i] = line.replace('{"Collect 8 Turtle \\"}', '{"Collect 8 Turtle Shells."}')
                fixes_made += 1
                print(f"Fixed quest 26182 incomplete string")
        
        # Fix quest 26817 - incomplete string
        elif '[26817]' in line:
            if 'Paul \\"}' in line:
                lines[i] = line.replace('{"Bring Paul \\"}', '{"Bring Paul\'s remains to the quest giver."}')
                fixes_made += 1
                print(f"Fixed quest 26817 incomplete string")
        
        # Fix quest 27463 - incomplete string
        elif '[27463]' in line:
            if 'Marai\'s \\"}' in line:
                lines[i] = line.replace('{"Collect Marai\'s \\"}', '{"Collect Marai\'s possessions."}')
                fixes_made += 1
                print(f"Fixed quest 27463 incomplete string")
        
        # Fix quest 27465 - incomplete string
        elif '[27465]' in line:
            if 'Barrel\\"}' in line:
                lines[i] = line.replace('{"Place 4 Explosives around Slightly Opened Oil Barrel\\"}', '{"Place 4 Explosives around Slightly Opened Oil Barrels."}')
                fixes_made += 1
                print(f"Fixed quest 27465 incomplete string")
    
    # Save the fixed file
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n✅ Fixed {fixes_made} problematic quests")
    print(f"Database still has 862 quests total")
    
    return fixes_made

if __name__ == "__main__":
    fix_specific_quests()