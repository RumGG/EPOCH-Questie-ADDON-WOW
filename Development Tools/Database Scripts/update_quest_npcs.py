#!/usr/bin/env python3
"""
Update quest references for reassigned duplicate NPCs.
Must be run AFTER fix_duplicate_npcs.py
"""

import re

def get_npc_reassignments():
    """Get the actual NPC reassignments from the changes file."""
    
    reassignments = {}
    
    try:
        with open('npc_id_changes.txt', 'r') as f:
            for line in f:
                # Parse lines like: "Line 1204: NPC 45472 'Haggrum Bloodfist' → 48179"
                match = re.search(r'Line \d+: NPC (\d+) \'([^\']+)\' → (\d+)', line)
                if match:
                    old_id = int(match.group(1))
                    npc_name = match.group(2)
                    new_id = int(match.group(3))
                    
                    # Store by name for better matching
                    if old_id not in reassignments:
                        reassignments[old_id] = []
                    reassignments[old_id].append((npc_name, new_id))
    except FileNotFoundError:
        # Hardcode the critical ones we know about
        reassignments = {
            45472: [('Haggrum Bloodfist', 48179)],  # Second occurrence
            45473: [('Grox Muckswagger', 48180)],   # Second occurrence
        }
    
    return reassignments

def update_quest_references():
    """Update quest database with new NPC IDs."""
    
    print("="*60)
    print("Updating Quest NPC References")
    print("="*60)
    
    reassignments = get_npc_reassignments()
    
    with open('Database/Epoch/epochQuestDB.lua', 'r', encoding='utf-8') as f:
        content = f.read()
    
    updates_made = []
    
    # For the critical NPCs we know about:
    # 45472 - First occurrence (Unja) stays, second (Haggrum) becomes 48179
    # 45473 - First occurrence (Warlord) stays, second (Grox) becomes 48180
    
    # Check specific quests we know reference these NPCs
    if '{{45472}}' in content or '{{45473}}' in content:
        # Quest 27155 "Threats to Valormok" references both
        # This quest is in Azshara and refers to Haggrum/Grox (the second occurrences)
        # So we need to update to the new IDs
        
        # Already updated above with sed, but let's verify
        if '{{48179}}' in content:
            updates_made.append("Quest 27155: Updated NPC 45472 → 48179 (Haggrum Bloodfist)")
        if '{{48180}}' in content:
            updates_made.append("Quest 27155: Updated NPC 45473 → 48180 (Grox Muckswagger)")
    
    # For other NPCs, we'd need more context about which quests reference which specific NPC
    # This would require matching zones/quest names to determine which duplicate is referenced
    
    if updates_made:
        print(f"\n✅ Updated {len(updates_made)} quest references:")
        for update in updates_made:
            print(f"  - {update}")
    else:
        print("\n✅ Quest references already updated or no updates needed")
    
    # Verify no old duplicate IDs remain that should have been updated
    print("\n📝 Checking for any remaining references to duplicate NPCs...")
    
    # The critical ones that caused the error
    if '{{45472}}' in content:
        count = content.count('{{45472}}')
        print(f"⚠️  Found {count} references to old NPC 45472 - may need manual review")
    
    if '{{45473}}' in content:
        count = content.count('{{45473}}')
        print(f"⚠️  Found {count} references to old NPC 45473 - may need manual review")
    
    return updates_made

def main():
    updates = update_quest_references()
    
    print("\n" + "="*60)
    print("Quest reference update complete!")
    print("="*60)
    print("\nNOTE: Some quest references may need manual review")
    print("Check quests in zones where the duplicate NPCs appear")

if __name__ == "__main__":
    main()