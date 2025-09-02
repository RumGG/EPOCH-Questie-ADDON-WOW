#!/usr/bin/env python3
"""
Fix quests that have NPC data in field 4 (requiredSkill)
Field 4 should be nil or skill data, not {{npcId}}
"""

import re

def fix_quest_field4():
    """Fix all quests with wrong field 4."""
    
    print("="*60)
    print("Fixing Quest Field 4 (requiredSkill)")
    print("="*60)
    
    with open('Database/Epoch/epochQuestDB.lua', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes = 0
    for i, line in enumerate(lines):
        if re.match(r'^\[\d+\] = \{', line.strip()):
            # Parse the first few fields
            # Pattern: [id] = {"name",field2,field3,field4,field5,...
            parts = line.split(',', 5)
            
            if len(parts) > 4:
                # Check field 4 (index 3 after split)
                field4 = parts[3].strip()
                
                # If field 4 looks like {{npcId}}, replace with nil
                if field4.startswith('{{') and not field4.startswith('{['):
                    # Extract the quest ID for reporting
                    quest_match = re.match(r'^\[(\d+)\]', line)
                    quest_id = quest_match.group(1) if quest_match else '?'
                    
                    # Replace field 4 with nil
                    parts[3] = 'nil'
                    lines[i] = ','.join(parts)
                    
                    fixes += 1
                    if fixes <= 10:
                        print(f"  Fixed quest {quest_id} on line {i+1}")
    
    if fixes > 0:
        # Save the fixed file
        with open('Database/Epoch/epochQuestDB.lua', 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"\n✅ Fixed {fixes} quests with NPC data in field 4")
    else:
        print("✅ No quests need field 4 fixes")
    
    return fixes

def main():
    fixes = fix_quest_field4()
    
    if fixes > 0:
        print("\n" + "="*60)
        print("IMPORTANT: Restart WoW completely to load changes")
        print("="*60)

if __name__ == "__main__":
    main()