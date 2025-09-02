#!/usr/bin/env python3
"""
Master validation script for Questie databases.
Runs all targeted validators in sequence.
"""

import sys
import os
import argparse
from pathlib import Path

# Add validators directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'validators'))

# Import all validators
from duplicate_zones import DuplicateZoneValidator
from nil_objectives import NilObjectiveValidator
from double_dash import DoubleDashValidator
from wrong_types import WrongTypeValidator
from duplicate_entries import DuplicateEntryValidator
from npc_structure import NpcStructureValidator
from quest_structure import QuestStructureValidator

class DatabaseValidator:
    """Master validator that runs all targeted validators."""
    
    def __init__(self, auto_fix=False):
        self.auto_fix = auto_fix
        
        # Define which validators to run for each database type
        self.quest_validators = [
            DuplicateEntryValidator(auto_fix),
            DoubleDashValidator(auto_fix),
            NilObjectiveValidator(auto_fix),
            WrongTypeValidator(auto_fix),
            QuestStructureValidator(auto_fix),
        ]
        
        self.npc_validators = [
            DuplicateEntryValidator(auto_fix),
            DoubleDashValidator(auto_fix),
            DuplicateZoneValidator(auto_fix),
            NpcStructureValidator(auto_fix),
        ]
    
    def validate_quest_db(self, filepath):
        """Run all quest validators."""
        print("\n" + "=" * 60)
        print("VALIDATING QUEST DATABASE")
        print("=" * 60)
        
        all_issues = []
        
        for validator in self.quest_validators:
            success = validator.run(filepath, entry_type='quest')
            if not success:
                all_issues.extend(validator.issues)
        
        return len(all_issues) == 0
    
    def validate_npc_db(self, filepath):
        """Run all NPC validators."""
        print("\n" + "=" * 60)
        print("VALIDATING NPC DATABASE")
        print("=" * 60)
        
        all_issues = []
        
        for validator in self.npc_validators:
            success = validator.run(filepath, entry_type='npc')
            if not success:
                all_issues.extend(validator.issues)
        
        return len(all_issues) == 0
    
    def merge_fixed_files(self, original_path, db_type='quest'):
        """Merge all validator fixes into a single file."""
        if not self.auto_fix:
            return
        
        print("\n" + "=" * 60)
        print(f"MERGING FIXES FOR {db_type.upper()} DATABASE")
        print("=" * 60)
        
        # Read original file
        with open(original_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Apply fixes from each validator in sequence
        validators = self.quest_validators if db_type == 'quest' else self.npc_validators
        
        for validator in validators:
            fixed_file = original_path.replace('.lua', f'_{validator.name()}_FIXED.lua')
            if os.path.exists(fixed_file):
                print(f"Applying fixes from {validator.name()}...")
                with open(fixed_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                # Clean up intermediate file
                os.remove(fixed_file)
        
        # Save final merged file
        output_path = original_path.replace('.lua', '_FIXED.lua')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"✅ All fixes merged into: {output_path}")
        
        # Instructions
        print("\n📋 Next steps:")
        print("1. Review the _FIXED.lua file")
        print("2. Back up your original file")
        print("3. Replace the original with the fixed version")
        print("4. Restart WoW completely to load changes")

def main():
    parser = argparse.ArgumentParser(description='Validate Questie Epoch database files')
    parser.add_argument('--fix', action='store_true', help='Apply fixes automatically')
    parser.add_argument('--quest-db', default='Database/Epoch/epochQuestDB.lua', 
                        help='Path to quest database')
    parser.add_argument('--npc-db', default='Database/Epoch/epochNpcDB.lua', 
                        help='Path to NPC database')
    parser.add_argument('--quest-only', action='store_true', help='Only validate quest database')
    parser.add_argument('--npc-only', action='store_true', help='Only validate NPC database')
    
    args = parser.parse_args()
    
    print("\n🔍 QUESTIE DATABASE VALIDATOR (Modular System)")
    print("=" * 60)
    
    # Check if files exist
    if not args.npc_only and not os.path.exists(args.quest_db):
        print(f"❌ Quest database not found: {args.quest_db}")
        sys.exit(1)
    if not args.quest_only and not os.path.exists(args.npc_db):
        print(f"❌ NPC database not found: {args.npc_db}")
        sys.exit(1)
    
    validator = DatabaseValidator(auto_fix=args.fix)
    quest_success = True
    npc_success = True
    
    # Validate quest database
    if not args.npc_only:
        quest_success = validator.validate_quest_db(args.quest_db)
        if args.fix:
            validator.merge_fixed_files(args.quest_db, 'quest')
    
    # Validate NPC database
    if not args.quest_only:
        npc_success = validator.validate_npc_db(args.npc_db)
        if args.fix:
            validator.merge_fixed_files(args.npc_db, 'npc')
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    if not args.npc_only:
        status = "✅ PASSED" if quest_success else "❌ FAILED"
        print(f"Quest Database: {status}")
    
    if not args.quest_only:
        status = "✅ PASSED" if npc_success else "❌ FAILED"
        print(f"NPC Database: {status}")
    
    if not args.fix and (not quest_success or not npc_success):
        print("\n💡 Tip: Run with --fix to automatically fix these issues")
    
    sys.exit(0 if (quest_success and npc_success) else 1)

if __name__ == '__main__':
    main()