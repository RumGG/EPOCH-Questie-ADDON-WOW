#!/usr/bin/env python3

"""
Fix the final 6 quests with improper objectives structure
"""

import re
import shutil
from datetime import datetime

def fix_final_quests():
    """Fix the 6 problematic quests"""
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/epochQuestDB_before_final_6_fix_{timestamp}.lua"
    shutil.copy("../Database/Epoch/epochQuestDB.lua", backup_file)
    print(f"✅ Created backup: {backup_file}")
    
    # Read the database
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    # Quest 27208 - Line 468
    # Has: {{{63084,"Defias Key"}}}
    # Should be in items position: {nil,nil,{{63084,1,"Defias Key"}},nil,nil,nil}
    for i, line in enumerate(lines):
        if '[27208]' in line:
            old_obj = '{{{63084,"Defias Key"}}}'
            new_obj = '{nil,nil,{{63084,1,"Defias Key"}},nil,nil,nil}'
            if old_obj in line:
                lines[i] = line.replace(old_obj, new_obj)
                fixes_made += 1
                print(f"✅ Fixed quest 27208 (line {i+1})")
    
    # Quest 26892 - Line 510
    # Has: {{{62749,1,"Requisition Orders"}}}
    # Should be: {nil,nil,{{62749,1,"Requisition Orders"}},nil,nil,nil}
    for i, line in enumerate(lines):
        if '[26892]' in line:
            old_obj = '{{{62749,1,"Requisition Orders"}}}'
            new_obj = '{nil,nil,{{62749,1,"Requisition Orders"}},nil,nil,nil}'
            if old_obj in line:
                lines[i] = line.replace(old_obj, new_obj)
                fixes_made += 1
                print(f"✅ Fixed quest 26892 (line {i+1})")
    
    # Quest 27354 - Line 598
    # Has: {{{63218,1,"Head of Jasone"}}}
    # Should be: {nil,nil,{{63218,1,"Head of Jasone"}},nil,nil,nil}
    for i, line in enumerate(lines):
        if '[27354]' in line:
            old_obj = '{{{63218,1,"Head of Jasone"}}}'
            new_obj = '{nil,nil,{{63218,1,"Head of Jasone"}},nil,nil,nil}'
            if old_obj in line:
                lines[i] = line.replace(old_obj, new_obj)
                fixes_made += 1
                print(f"✅ Fixed quest 27354 (line {i+1})")
    
    # Quest 26647 - Line 663 (has additional issues)
    # Has: {{{4001047,1}}}
    # Should be: {nil,nil,{{4001047,1}},nil,nil,nil}
    for i, line in enumerate(lines):
        if '[26647]' in line:
            # This quest has malformed data, let's check its structure
            if '{{{4001047,1}}}' in line:
                old_obj = '{{{4001047,1}}}'
                new_obj = '{nil,nil,{{4001047,1}},nil,nil,nil}'
                lines[i] = line.replace(old_obj, new_obj)
                fixes_made += 1
                print(f"✅ Fixed quest 26647 (line {i+1})")
    
    # Quest 26812 - Line 708
    # Has complex structure with both objects and items
    # {nil,{{{4000038,1},{4000039,1}}},{{{60456,1}}}}
    # The items part needs fixing: {{{60456,1}}} -> {{60456,1}}
    for i, line in enumerate(lines):
        if '[26812]' in line:
            # Fix the triple-braced item
            if '{{{60456,1}}}' in line:
                old_obj = '{{{60456,1}}}'
                new_obj = '{{60456,1}}'
                lines[i] = line.replace(old_obj, new_obj)
                fixes_made += 1
                print(f"✅ Fixed quest 26812 (line {i+1})")
    
    # Write the fixed file
    if fixes_made > 0:
        with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"\n✅ Successfully fixed {fixes_made} quests")
    else:
        print("\n⚠️ No fixes were needed")
    
    return fixes_made

if __name__ == "__main__":
    fix_final_quests()