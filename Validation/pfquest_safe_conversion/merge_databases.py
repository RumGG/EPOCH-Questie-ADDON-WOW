#!/usr/bin/env python3
"""
Safe database merger for adding pfQuest converted quests to Questie
Preserves all existing data and only adds new quests
"""

import re
import shutil
from datetime import datetime
from pathlib import Path

def backup_file(filepath):
    """Create timestamped backup of file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("BACKUPS") / f"pre_merge_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    backup_path = backup_dir / Path(filepath).name
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backed up {filepath} to {backup_path}")
    return backup_path

def load_database_entries(filepath):
    """Load all database entries preserving exact formatting"""
    entries = {}
    current_entry = []
    current_id = None
    in_entry = False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        # Check for quest/npc entry start
        match = re.match(r'(\s*)\[(\d+)\]\s*=\s*\{', line)
        if match:
            # Save previous entry if exists
            if current_id and current_entry:
                entries[current_id] = ''.join(current_entry)
            
            # Start new entry
            current_id = int(match.group(2))
            current_entry = [line]
            in_entry = True
        elif in_entry:
            current_entry.append(line)
            # Check if entry is complete (ends with },)
            if line.strip().endswith('},') or line.strip().endswith('},  -- Converted from pfQuest'):
                entries[current_id] = ''.join(current_entry)
                current_entry = []
                current_id = None
                in_entry = False
    
    # Save last entry if exists
    if current_id and current_entry:
        entries[current_id] = ''.join(current_entry)
    
    return entries

def merge_quest_databases(original_path, converted_path, output_path):
    """Merge converted quests into original database"""
    print("\n" + "="*70)
    print("MERGING QUEST DATABASES")
    print("="*70)
    
    # Load both databases
    print("\nLoading databases...")
    original_entries = load_database_entries(original_path)
    converted_entries = load_database_entries(converted_path)
    
    print(f"Original database: {len(original_entries)} quests")
    print(f"Converted database: {len(converted_entries)} quests")
    
    # Find new quests to add
    new_quests = {}
    skipped = []
    for quest_id, entry in converted_entries.items():
        if quest_id not in original_entries:
            new_quests[quest_id] = entry
        else:
            skipped.append(quest_id)
    
    print(f"\nNew quests to add: {len(new_quests)}")
    print(f"Skipped (already exist): {len(skipped)}")
    
    # Read original file structure
    with open(original_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find where to insert new quests (before the final closing brace)
    insert_index = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == '}':
            insert_index = i
            break
    
    if insert_index is None:
        print("❌ Could not find closing brace in original file")
        return False
    
    # Insert new quests
    print(f"\nInserting {len(new_quests)} new quests...")
    
    # Add separator comment
    separator = [
        "\n",
        "-- ==========================================\n",
        f"-- pfQuest Converted Quests - Added {datetime.now().strftime('%Y-%m-%d')}\n",
        f"-- {len(new_quests)} new quests from pfQuest database\n",
        "-- Note: These quests may lack objective details\n",
        "-- ==========================================\n",
        "\n"
    ]
    
    # Insert all new quests
    new_lines = []
    for quest_id in sorted(new_quests.keys()):
        new_lines.append(new_quests[quest_id])
        if not new_quests[quest_id].endswith('\n'):
            new_lines.append('\n')
    
    # Combine everything
    output_lines = lines[:insert_index] + separator + new_lines + lines[insert_index:]
    
    # Write merged database
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    print(f"✅ Merged database written to: {output_path}")
    
    # Verify the merge
    merged_entries = load_database_entries(output_path)
    expected_total = len(original_entries) + len(new_quests)
    
    if len(merged_entries) == expected_total:
        print(f"✅ Verification passed: {len(merged_entries)} total quests")
        return True
    else:
        print(f"❌ Verification failed: Expected {expected_total}, got {len(merged_entries)}")
        return False

def create_missing_npcs_file(converted_quest_path):
    """Extract list of missing NPCs that need to be added"""
    print("\n" + "="*70)
    print("ANALYZING MISSING NPCS")
    print("="*70)
    
    # Get NPC IDs from converted quests
    quest_npcs = set()
    with open(converted_quest_path, 'r', encoding='utf-8') as f:
        for line in f:
            # Look for NPC IDs in startedBy and finishedBy fields
            matches = re.findall(r'\{\{(\d+)\}', line)
            for match in matches:
                quest_npcs.add(int(match))
    
    # Check our NPC database
    our_npcs = set()
    with open('epochNpcDB.lua', 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'\s*\[(\d+)\]', line)
            if match:
                our_npcs.add(int(match.group(1)))
    
    missing_npcs = sorted(quest_npcs - our_npcs)
    
    # Write missing NPCs report
    with open('MISSING_NPCS.txt', 'w') as f:
        f.write("MISSING NPCS FOR CONVERTED QUESTS\n")
        f.write("="*50 + "\n\n")
        f.write(f"Total NPCs referenced: {len(quest_npcs)}\n")
        f.write(f"NPCs we have: {len(quest_npcs & our_npcs)}\n")
        f.write(f"NPCs missing: {len(missing_npcs)}\n\n")
        f.write("Missing NPC IDs:\n")
        for npc_id in missing_npcs:
            f.write(f"  {npc_id}\n")
        f.write("\n")
        f.write("These NPCs need to be added to epochNpcDB.lua\n")
        f.write("with at least basic data (name and zone) for\n")
        f.write("quest givers/turn-ins to show on the map.\n")
    
    print(f"Missing NPCs report written to: MISSING_NPCS.txt")
    print(f"Total missing: {len(missing_npcs)} NPCs")
    
    return missing_npcs

def main():
    print("\n🔧 QUESTIE DATABASE MERGER")
    print("="*70)
    
    # File paths
    original_quest_db = "epochQuestDB.lua"
    converted_quest_db = "pfquest_properly_converted_FIXED.lua"
    merged_quest_db = "epochQuestDB_MERGED.lua"
    
    # Safety checks
    if not Path(original_quest_db).exists():
        print(f"❌ Original database not found: {original_quest_db}")
        return
    
    if not Path(converted_quest_db).exists():
        print(f"❌ Converted database not found: {converted_quest_db}")
        return
    
    print("\n📋 This tool will:")
    print("1. Backup your original database")
    print("2. Merge 342 new quests from pfQuest")
    print("3. Create a list of missing NPCs")
    print("4. Validate the merged database")
    
    # Create backups
    print("\n📦 Creating backups...")
    backup_file(original_quest_db)
    
    # Merge databases
    success = merge_quest_databases(
        original_quest_db,
        converted_quest_db,
        merged_quest_db
    )
    
    if success:
        # Analyze missing NPCs
        create_missing_npcs_file(converted_quest_db)
        
        print("\n" + "="*70)
        print("✅ MERGE COMPLETE!")
        print("="*70)
        print(f"\nMerged database: {merged_quest_db}")
        print("\n📋 Next steps:")
        print("1. Review the merged database file")
        print("2. Check MISSING_NPCS.txt for NPCs that need adding")
        print("3. Copy epochQuestDB_MERGED.lua to main Questie folder")
        print("4. Rename it to epochQuestDB.lua (replacing original)")
        print("5. Restart WoW completely to test")
        print("\n⚠️ The quests will work but with limitations:")
        print("  - No objective tracking (mobs/items to kill/collect)")
        print("  - Missing NPCs won't show on map")
        print("  - Manual data collection needed to complete quest data")
    else:
        print("\n❌ Merge failed! Check the output above for errors.")

if __name__ == "__main__":
    main()