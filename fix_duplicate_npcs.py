#!/usr/bin/env python3
"""
Fix duplicate NPC IDs in epochNpcDB.lua
Reassigns duplicate NPCs to new IDs starting from 48168
"""

import re
from collections import defaultdict

def fix_duplicate_npcs():
    """Fix all duplicate NPC IDs."""
    
    print("="*60)
    print("Fixing Duplicate NPCs in epochNpcDB.lua")
    print("="*60)
    
    with open('Database/Epoch/epochNpcDB.lua', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Track NPCs and find duplicates
    npcs = {}
    duplicates = defaultdict(list)
    
    for i, line in enumerate(lines):
        match = re.match(r'^\[(\d+)\] = \{', line.strip())
        if match:
            npc_id = int(match.group(1))
            if npc_id in npcs:
                duplicates[npc_id].append(i)
            else:
                npcs[npc_id] = i
    
    # Assign new IDs starting from 48168
    next_id = 48168
    id_mappings = {}  # old_id -> new_id for quest updates
    fixes_made = []
    
    for npc_id in sorted(duplicates.keys()):
        dup_lines = duplicates[npc_id]
        
        # Keep first occurrence, reassign others
        for line_idx in dup_lines:
            old_line = lines[line_idx]
            new_line = re.sub(f'^\[{npc_id}\]', f'[{next_id}]', old_line)
            lines[line_idx] = new_line
            
            # Extract NPC name for reporting
            name_match = re.search(r'\{"([^"]+)"', old_line)
            npc_name = name_match.group(1) if name_match else "Unknown"
            
            fixes_made.append(f"Line {line_idx+1}: NPC {npc_id} '{npc_name}' → {next_id}")
            id_mappings[f"{npc_id}_{line_idx}"] = next_id
            next_id += 1
    
    # Save fixed NPC database
    with open('Database/Epoch/epochNpcDB.lua', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n✅ Fixed {len(fixes_made)} duplicate NPCs:")
    for fix in fixes_made[:10]:
        print(f"  - {fix}")
    if len(fixes_made) > 10:
        print(f"  ... and {len(fixes_made) - 10} more")
    
    return id_mappings, fixes_made

def update_quest_references(id_mappings):
    """Update quest database to reference new NPC IDs."""
    
    print("\n" + "="*60)
    print("Updating Quest References")
    print("="*60)
    
    with open('Database/Epoch/epochQuestDB.lua', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    updates_made = []
    
    # This would need more complex logic to match NPCs to quests
    # For now, we'll just report what might need updating
    
    print("⚠️  Manual quest reference updates may be needed")
    print("   Check quests that reference the reassigned NPCs")
    
    return updates_made

def main():
    # Fix duplicate NPCs
    id_mappings, fixes = fix_duplicate_npcs()
    
    # Update quest references if needed
    # update_quest_references(id_mappings)
    
    print("\n" + "="*60)
    print("✅ Duplicate NPC fixes complete!")
    print("="*60)
    print("\nIMPORTANT:")
    print("1. Restart WoW completely to load changes")
    print("2. Test NPCs that were reassigned")
    print("3. Check quest givers/turn-ins still work")
    
    # Save mappings for reference
    with open('npc_id_changes.txt', 'w') as f:
        f.write("NPC ID Changes\n")
        f.write("="*40 + "\n")
        for fix in fixes:
            f.write(fix + "\n")

if __name__ == "__main__":
    main()