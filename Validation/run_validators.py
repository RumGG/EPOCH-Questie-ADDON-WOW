#!/usr/bin/env python3

"""
Run all validators from the validators_module
Checks for common database issues
"""

import sys
import os
sys.path.append('validators_module')

from validators_module.double_dash import DoubleDashValidator
from validators_module.duplicate_entries import DuplicateEntryValidator
from validators_module.duplicate_zones import DuplicateZoneValidator
from validators_module.nil_objectives import NilObjectiveValidator
from validators_module.npc_structure import NpcStructureValidator
from validators_module.quest_structure import QuestStructureValidator
from validators_module.wrong_types import WrongTypeValidator

def run_all_validators(quest_file="../Database/Epoch/epochQuestDB.lua", 
                       npc_file="../Database/Epoch/epochNpcDB.lua",
                       auto_fix=False):
    """Run all validators on the database files"""
    
    validators = [
        DoubleDashValidator(auto_fix),
        DuplicateEntryValidator(auto_fix),
        DuplicateZoneValidator(auto_fix),
        NilObjectiveValidator(auto_fix),
        NpcStructureValidator(auto_fix),
        QuestStructureValidator(auto_fix),
        WrongTypeValidator(auto_fix)
    ]
    
    total_issues = 0
    
    print("="*70)
    print("RUNNING DATABASE VALIDATORS")
    print("="*70)
    
    # Process quest database
    if os.path.exists(quest_file):
        print(f"\n📋 Checking Quest Database: {quest_file}")
        with open(quest_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for validator in validators:
            if hasattr(validator, 'validate_line'):
                print(f"\n  Running {validator.name()}: {validator.description()}")
                issues = 0
                for line_num, line in enumerate(lines, 1):
                    has_issue, issue_desc, fixed = validator.validate_line(line, line_num, 'quest')
                    if has_issue:
                        issues += 1
                        if issues <= 5:  # Show first 5 issues
                            print(f"    Line {line_num}: {issue_desc}")
                
                if issues > 0:
                    print(f"    Found {issues} issues")
                    total_issues += issues
                else:
                    print(f"    ✅ No issues found")
    
    # Process NPC database
    if os.path.exists(npc_file):
        print(f"\n📋 Checking NPC Database: {npc_file}")
        with open(npc_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for validator in validators:
            if hasattr(validator, 'validate_line'):
                print(f"\n  Running {validator.name()}: {validator.description()}")
                issues = 0
                for line_num, line in enumerate(lines, 1):
                    has_issue, issue_desc, fixed = validator.validate_line(line, line_num, 'npc')
                    if has_issue:
                        issues += 1
                        if issues <= 5:  # Show first 5 issues
                            print(f"    Line {line_num}: {issue_desc}")
                
                if issues > 0:
                    print(f"    Found {issues} issues")
                    total_issues += issues
                else:
                    print(f"    ✅ No issues found")
    
    print("\n" + "="*70)
    print(f"VALIDATION COMPLETE: {total_issues} total issues found")
    print("="*70)
    
    if auto_fix and total_issues > 0:
        print("\n⚠️  Auto-fix was enabled but not implemented yet")
        print("   Review the issues and fix manually if needed")
    
    return total_issues


if __name__ == "__main__":
    # Parse arguments
    auto_fix = False
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        auto_fix = True
        print("⚠️  Auto-fix mode enabled")
    
    # Run validators
    issues = run_all_validators(auto_fix=auto_fix)
    
    # Exit with error code if issues found
    sys.exit(1 if issues > 0 else 0)