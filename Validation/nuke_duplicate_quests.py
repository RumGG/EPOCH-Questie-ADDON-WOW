#!/usr/bin/env python3

"""
Script to NUKE duplicate quests from the Questie database
This will remove all confirmed duplicate quest entries, keeping only the lowest ID
"""

import re
import os
import shutil
from datetime import datetime
from collections import defaultdict

# List of confirmed duplicates to remove (from our scan)
DUPLICATES_TO_NUKE = [
    26927,  # duplicate of 26926 - "A Box of Relics"
    28746,  # duplicate of 28726 - "A Refugee's Quandary"
    26974,  # duplicate of 26973 - "Advanced Alchemy"
    26929,  # duplicate of 26928 - "Arugal Ambush"
    26486,  # duplicate of 26485 - "Call of Fire"
    26487,  # duplicate of 26485 - "Call of Fire"
    28618,  # duplicate of 28535 - "Commission for Joakim Sparkroot"
    26971,  # duplicate of 26970 - "Cooking with Carrion"
    27327,  # duplicate of 27325 - "Dental Records"
    27328,  # duplicate of 27326 - "Dental Records"
    26176,  # duplicate of 26175 - "Falling Up To Grace"
    26525,  # duplicate of 26519 - "Felicity's Deciphering"
    26296,  # duplicate of 26294 - "Fit For A King"
    26698,  # duplicate of 26697 - "Hand of Azora"
    26703,  # duplicate of 26702 - "Hand of Azora"
    28904,  # duplicate of 26770 - "Just Desserts"
    26712,  # duplicate of 26711 - "Life In Death"
    26713,  # duplicate of 26711 - "Life In Death"
    27928,  # duplicate of 27927 - "Memories of Honor and Blood"
    26889,  # duplicate of 26888 - "My Friend, The Skullsplitter"
    27041,  # duplicate of 27040 - "Practical Science"
    26503,  # duplicate of 26502 - "Rare Books"
    27256,  # duplicate of 27254 - "Reagents For The Undercity"
    26707,  # duplicate of 26706 - "Riders In The Night"
    27049,  # duplicate of 27045 - "Rumbles Of The Earth"
    27051,  # duplicate of 27045 - "Rumbles Of The Earth"
    27046,  # duplicate of 27045 - "Rumbles Of The Earth"
    26968,  # duplicate of 26967 - "Scourge Botany"
    26969,  # duplicate of 26967 - "Scourge Botany"
    26980,  # duplicate of 26979 - "Senior Prank"
    26981,  # duplicate of 26979 - "Senior Prank"
    28901,  # duplicate of 28725 - "Shift into G.E.A.R."
    26530,  # duplicate of 26529 - "The Argus Wake"
    26531,  # duplicate of 26529 - "The Argus Wake"
    26533,  # duplicate of 26532 - "The Argus Wake"
    26996,  # duplicate of 26995 - "The Killing Fields"
    28367,  # duplicate of 28366 - "The Rite of the Medicant"
    27501,  # duplicate of 27500 - "The Sacred Flame"
    26541,  # duplicate of 26540 - "Threats from Abroad"
    26878,  # duplicate of 26877 - "Tomes of Interest"
    26589,  # duplicate of 26588 - "Trapped Miners"
    26590,  # duplicate of 26588 - "Trapped Miners"
    26909,  # duplicate of 26908 - "Wild Tulip"
]

def create_backup(filepath):
    """Create a timestamped backup of the file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "BACKUPS/duplicate_purge"
    
    # Create backup directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    
    # Create backup filename
    filename = os.path.basename(filepath)
    backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.backup")
    
    # Copy file to backup
    shutil.copy2(filepath, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def nuke_quests_from_file(filepath, quest_ids_to_remove):
    """Remove specified quest IDs from a database file."""
    
    print(f"\n🎯 Processing: {filepath}")
    
    # Create backup first
    backup_path = create_backup(filepath)
    
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Track what we remove
    removed_quests = []
    new_lines = []
    skip_next = False
    
    for i, line in enumerate(lines):
        if skip_next:
            # Check if this line is a continuation (doesn't start with [)
            if not line.strip().startswith('[') and not line.strip().startswith('--') and not line.strip().startswith('epochQuestData'):
                continue  # Skip continuation lines
            else:
                skip_next = False  # Reset flag, this is a new entry
        
        # Check if this line contains a quest to remove
        quest_found = False
        for quest_id in quest_ids_to_remove:
            # Match patterns like [28901] = or epochQuestData[28901] =
            pattern = rf'^\s*(?:epochQuestData\s*)?\[{quest_id}\]\s*='
            if re.match(pattern, line):
                quest_found = True
                removed_quests.append(quest_id)
                
                # Extract quest name for logging
                name_match = re.search(r'"([^"]*)"', line)
                quest_name = name_match.group(1) if name_match else f"Quest {quest_id}"
                print(f"  💥 NUKED: Quest {quest_id} - {quest_name}")
                
                # Check if the quest data continues on the next line
                if not line.rstrip().endswith(','):
                    # Quest might continue on next lines
                    skip_next = True
                break
        
        if not quest_found:
            new_lines.append(line)
    
    # Write the cleaned file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    return removed_quests

def nuke_npcs_with_removed_quests(filepath, removed_quest_ids):
    """Remove references to nuked quests from NPC database."""
    
    print(f"\n🎯 Cleaning NPC references: {filepath}")
    
    # Create backup first
    backup_path = create_backup(filepath)
    
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track changes
    changes_made = 0
    
    # Process each removed quest ID
    for quest_id in removed_quest_ids:
        # Pattern to find quest ID in NPC quest lists
        # Matches: {quest_id, or ,quest_id, or ,quest_id}
        patterns = [
            (rf'\{{({quest_id}),', r'{'),  # First in list
            (rf',({quest_id}),', r','),     # Middle of list
            (rf',({quest_id})\}}', r'}'),   # Last in list
            (rf'\{{({quest_id})\}}', r'{}'), # Only item in list
        ]
        
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                changes_made += 1
                print(f"  🔧 Removed quest {quest_id} from NPC quest lists")
                content = new_content
    
    # Clean up any double commas or empty braces
    content = re.sub(r',,+', ',', content)  # Remove double commas
    content = re.sub(r'\{,', '{', content)  # Remove leading commas
    content = re.sub(r',\}', '}', content)  # Remove trailing commas
    
    # Write the cleaned file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ Cleaned {changes_made} NPC quest references")
    return changes_made

def main():
    """Main function to nuke all duplicate quests."""
    
    print("=" * 80)
    print("🚀 DUPLICATE QUEST NUCLEAR STRIKE SYSTEM ACTIVATED 🚀")
    print("=" * 80)
    print(f"Target: {len(DUPLICATES_TO_NUKE)} duplicate quests for termination")
    print("=" * 80)
    
    # Confirm with user
    print("\n⚠️  WARNING: This will permanently remove duplicate quests from the database!")
    print("Backups will be created in BACKUPS/duplicate_purge/")
    response = input("\nType 'NUKE' to proceed with extreme prejudice: ")
    
    if response != "NUKE":
        print("\n❌ Nuclear launch aborted. Database remains intact.")
        return
    
    print("\n🔥 INITIATING NUCLEAR STRIKE... 🔥")
    
    # Process quest database
    quest_db = "Database/Epoch/epochQuestDB.lua"
    if os.path.exists(quest_db):
        removed_quests = nuke_quests_from_file(quest_db, DUPLICATES_TO_NUKE)
        print(f"\n✅ Successfully NUKED {len(removed_quests)} duplicate quests from quest database")
        
        # Clean up NPC references
        npc_db = "Database/Epoch/epochNpcDB.lua"
        if os.path.exists(npc_db):
            nuke_npcs_with_removed_quests(npc_db, removed_quests)
    else:
        print(f"❌ Quest database not found: {quest_db}")
        return
    
    # Final report
    print("\n" + "=" * 80)
    print("💥 NUCLEAR STRIKE COMPLETE 💥")
    print("=" * 80)
    print(f"Quests eliminated: {len(removed_quests)}")
    print(f"Database optimized and cleaned")
    print("\nNext steps:")
    print("1. Exit WoW completely")
    print("2. Restart WoW")
    print("3. Run /qdc recompile (if available)")
    print("\n✅ The duplicate menace has been eliminated, Captain!")
    
    # Save a report
    report_path = f"BACKUPS/duplicate_purge/purge_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_path, 'w') as f:
        f.write("DUPLICATE QUEST PURGE REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Date: {datetime.now()}\n")
        f.write(f"Quests Removed: {len(removed_quests)}\n\n")
        f.write("Removed Quest IDs:\n")
        for quest_id in sorted(removed_quests):
            f.write(f"  - {quest_id}\n")
    
    print(f"\n📄 Report saved: {report_path}")

if __name__ == "__main__":
    main()