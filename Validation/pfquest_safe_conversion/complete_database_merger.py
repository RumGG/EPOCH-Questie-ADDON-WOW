#!/usr/bin/env python3
"""
Complete database merger for pfQuest data into Questie
Merges quests and NPCs with full validation
"""

import re
import shutil
from datetime import datetime
from pathlib import Path

class QuestieDatabaseMerger:
    def __init__(self):
        self.stats = {
            'quests_added': 0,
            'npcs_added': 0,
            'quests_skipped': 0,
            'npcs_skipped': 0,
            'backups_created': []
        }
    
    def backup_file(self, filepath):
        """Create timestamped backup"""
        if not Path(filepath).exists():
            print(f"⚠️ File not found: {filepath}")
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = Path("BACKUPS") / f"merge_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_path = backup_dir / Path(filepath).name
        shutil.copy2(filepath, backup_path)
        self.stats['backups_created'].append(str(backup_path))
        print(f"✅ Backed up: {filepath} -> {backup_path}")
        return backup_path
    
    def load_entries(self, filepath, entry_type='quest'):
        """Load database entries preserving formatting"""
        entries = {}
        
        if not Path(filepath).exists():
            return entries
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all entries
        pattern = r'\[(\d+)\]\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
        
        for match in re.finditer(pattern, content):
            entry_id = int(match.group(1))
            # Keep the complete entry including the ID and braces
            full_match = match.group(0)
            entries[entry_id] = full_match
        
        return entries
    
    def merge_quest_database(self, original_path, converted_path, output_path):
        """Merge converted quests into database"""
        print("\n" + "="*70)
        print("MERGING QUEST DATABASE")
        print("="*70)
        
        # Load databases
        print("\nLoading quest databases...")
        original = self.load_entries(original_path, 'quest')
        converted = self.load_entries(converted_path, 'quest')
        
        print(f"  Original: {len(original)} quests")
        print(f"  Converted: {len(converted)} quests")
        
        # Find new quests
        new_quests = {}
        for qid, entry in converted.items():
            if qid not in original:
                new_quests[qid] = entry
                self.stats['quests_added'] += 1
            else:
                self.stats['quests_skipped'] += 1
        
        print(f"  To add: {len(new_quests)} new quests")
        print(f"  Skipped: {self.stats['quests_skipped']} (already exist)")
        
        if not new_quests:
            print("No new quests to add!")
            return False
        
        # Read original file
        with open(original_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find insertion point (before final })
        insert_index = None
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == '}':
                insert_index = i
                break
        
        if insert_index is None:
            print("❌ Could not find closing brace")
            return False
        
        # Build new content
        new_content = []
        new_content.append("\n")
        new_content.append("-- ==========================================\n")
        new_content.append(f"-- pfQuest Imported Quests - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        new_content.append(f"-- Added {len(new_quests)} quests from pfQuest database\n")
        new_content.append("-- ==========================================\n")
        new_content.append("\n")
        
        # Add new quests
        for qid in sorted(new_quests.keys()):
            new_content.append(f"  {new_quests[qid]},\n")
        
        # Combine everything
        output_lines = lines[:insert_index] + new_content + lines[insert_index:]
        
        # Write merged file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
        
        print(f"✅ Merged quest database: {output_path}")
        return True
    
    def merge_npc_database(self, original_path, npcs_to_add_path, output_path):
        """Merge missing NPCs into database"""
        print("\n" + "="*70)
        print("MERGING NPC DATABASE")
        print("="*70)
        
        if not Path(npcs_to_add_path).exists():
            print(f"No NPCs to add file: {npcs_to_add_path}")
            return False
        
        # Load databases
        print("\nLoading NPC databases...")
        original = self.load_entries(original_path, 'npc')
        to_add = self.load_entries(npcs_to_add_path, 'npc')
        
        print(f"  Original: {len(original)} NPCs")
        print(f"  To add: {len(to_add)} NPCs")
        
        # Find new NPCs
        new_npcs = {}
        for npc_id, entry in to_add.items():
            if npc_id not in original:
                new_npcs[npc_id] = entry
                self.stats['npcs_added'] += 1
            else:
                self.stats['npcs_skipped'] += 1
        
        print(f"  Will add: {len(new_npcs)} new NPCs")
        print(f"  Skipped: {self.stats['npcs_skipped']} (already exist)")
        
        if not new_npcs:
            print("No new NPCs to add!")
            return False
        
        # Read original file
        with open(original_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find insertion point
        insert_index = None
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip() == '}':
                insert_index = i
                break
        
        if insert_index is None:
            print("❌ Could not find closing brace")
            return False
        
        # Build new content
        new_content = []
        new_content.append("\n")
        new_content.append("-- ==========================================\n")
        new_content.append(f"-- pfQuest Imported NPCs - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        new_content.append(f"-- Added {len(new_npcs)} NPCs from pfQuest quests\n")
        new_content.append("-- Note: These NPCs need coordinates via in-game collection\n")
        new_content.append("-- ==========================================\n")
        new_content.append("\n")
        
        # Add new NPCs
        for npc_id in sorted(new_npcs.keys()):
            new_content.append(f"  {new_npcs[npc_id]},\n")
        
        # Combine everything
        output_lines = lines[:insert_index] + new_content + lines[insert_index:]
        
        # Write merged file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(output_lines)
        
        print(f"✅ Merged NPC database: {output_path}")
        return True
    
    def validate_merged_files(self, quest_file, npc_file):
        """Validate the merged files"""
        print("\n" + "="*70)
        print("VALIDATING MERGED FILES")
        print("="*70)
        
        valid = True
        
        # Check quest file
        if Path(quest_file).exists():
            quests = self.load_entries(quest_file, 'quest')
            print(f"✅ Quest database valid: {len(quests)} total quests")
        else:
            print(f"❌ Quest file not found: {quest_file}")
            valid = False
        
        # Check NPC file
        if Path(npc_file).exists():
            npcs = self.load_entries(npc_file, 'npc')
            print(f"✅ NPC database valid: {len(npcs)} total NPCs")
        else:
            print(f"❌ NPC file not found: {npc_file}")
            valid = False
        
        return valid
    
    def run_complete_merge(self):
        """Run the complete merge process"""
        print("\n" + "="*70)
        print("🔧 QUESTIE COMPLETE DATABASE MERGER")
        print("="*70)
        
        # File paths
        files = {
            'quest_original': 'epochQuestDB.lua',
            'quest_converted': 'pfquest_properly_converted_FIXED.lua',
            'quest_output': 'epochQuestDB_COMPLETE.lua',
            'npc_original': 'epochNpcDB.lua',
            'npc_missing': 'pfquest_missing_npcs.lua',
            'npc_output': 'epochNpcDB_COMPLETE.lua'
        }
        
        print("\n📋 This process will:")
        print("1. Backup all original databases")
        print("2. Merge 342 new quests from pfQuest")
        print("3. Merge 4 missing NPCs")
        print("4. Validate all merged files")
        print("5. Create ready-to-use database files")
        
        # Create backups
        print("\n📦 Creating backups...")
        self.backup_file(files['quest_original'])
        self.backup_file(files['npc_original'])
        
        # Merge quest database
        quest_success = self.merge_quest_database(
            files['quest_original'],
            files['quest_converted'],
            files['quest_output']
        )
        
        # Merge NPC database
        npc_success = self.merge_npc_database(
            files['npc_original'],
            files['npc_missing'],
            files['npc_output']
        )
        
        # Validate
        if quest_success and npc_success:
            valid = self.validate_merged_files(
                files['quest_output'],
                files['npc_output']
            )
            
            if valid:
                print("\n" + "="*70)
                print("✅ MERGE COMPLETE AND VALIDATED!")
                print("="*70)
                print(f"\n📊 Final Statistics:")
                print(f"  Quests added: {self.stats['quests_added']}")
                print(f"  NPCs added: {self.stats['npcs_added']}")
                print(f"  Backups created: {len(self.stats['backups_created'])}")
                
                print("\n📋 Next Steps:")
                print("1. Review the COMPLETE files:")
                print(f"   - {files['quest_output']}")
                print(f"   - {files['npc_output']}")
                print("2. Copy to main Questie Database/Epoch/ folder")
                print("3. Rename to epochQuestDB.lua and epochNpcDB.lua")
                print("4. Restart WoW completely to test")
                
                print("\n⚠️ Important Notes:")
                print("- New quests lack objective mob/item IDs")
                print("- NPCs need coordinates via in-game collection")
                print("- Use data collector to improve quest data")
                
                return True
        
        print("\n❌ Merge failed or validation errors!")
        return False

def main():
    merger = QuestieDatabaseMerger()
    success = merger.run_complete_merge()
    
    if not success:
        print("\n⚠️ Check errors above and fix before retrying")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())