#!/usr/bin/env python3

"""
Master script to run all fix modules in sequence
Creates backups and validates at each step
"""

import os
import sys
import shutil
from datetime import datetime

# Import our modules
import fix_module_1_quadruple_braces as mod1
import fix_module_2_triple_braces as mod2
import fix_module_3_double_braces as mod3
import fix_module_4_validate as mod4

def create_backup(source_file, iteration):
    """Create a backup with timestamp"""
    backup_dir = "../Database/Epoch/ITERATIVE_BACKUPS"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{backup_dir}/backup_{timestamp}_step{iteration}.lua"
    shutil.copy(source_file, backup_file)
    print(f"📁 Created backup: {backup_file}")
    return backup_file

def main():
    """Run all fix modules in sequence"""
    
    print("=" * 70)
    print("QUESTIE DATABASE FIX - MASTER SCRIPT")
    print("=" * 70)
    print("This will fix all nesting issues from pfQuest import\n")
    
    # Check if input file exists
    input_file = "../Database/Epoch/epochQuestDB.lua"
    if not os.path.exists(input_file):
        print(f"❌ Error: {input_file} not found!")
        return 1
    
    # Create initial backup
    print("Step 0: Creating initial backup...")
    initial_backup = create_backup(input_file, 0)
    
    # Temporary files for each stage
    temp1 = "../Database/Epoch/epochQuestDB_temp1.lua"
    temp2 = "../Database/Epoch/epochQuestDB_temp2.lua"
    temp3 = "../Database/Epoch/epochQuestDB_temp3.lua"
    final_output = "../Database/Epoch/epochQuestDB_FIXED.lua"
    
    total_fixes = 0
    all_quest_fixes = set()
    
    # Step 1: Fix quadruple braces
    print("\n" + "=" * 70)
    print("Step 1: Fixing quadruple-brace patterns...")
    print("-" * 70)
    fixes1, quests1 = mod1.fix_quadruple_braces(input_file, temp1)
    total_fixes += fixes1
    all_quest_fixes.update(quests1)
    print(f"✅ Fixed {fixes1} issues")
    
    # Validate after step 1
    print("\nValidating after Step 1...")
    mod4.validate_database(temp1)
    create_backup(temp1, 1)
    
    # Step 2: Fix triple braces
    print("\n" + "=" * 70)
    print("Step 2: Fixing triple-brace patterns...")
    print("-" * 70)
    fixes2, quests2 = mod2.fix_triple_brace_items(temp1, temp2)
    total_fixes += fixes2
    all_quest_fixes.update(quests2)
    print(f"✅ Fixed {fixes2} issues")
    
    # Validate after step 2
    print("\nValidating after Step 2...")
    mod4.validate_database(temp2)
    create_backup(temp2, 2)
    
    # Step 3: Fix double braces
    print("\n" + "=" * 70)
    print("Step 3: Fixing double-brace objectives...")
    print("-" * 70)
    fixes3, quests3 = mod3.fix_double_brace_objectives(temp2, temp3)
    total_fixes += fixes3
    all_quest_fixes.update(quests3)
    print(f"✅ Fixed {fixes3} issues")
    
    # Validate after step 3
    print("\nValidating after Step 3...")
    mod4.validate_database(temp3)
    create_backup(temp3, 3)
    
    # Final validation
    print("\n" + "=" * 70)
    print("FINAL VALIDATION")
    print("=" * 70)
    is_valid = mod4.validate_database(temp3)
    
    if is_valid:
        # Copy to final output
        shutil.copy(temp3, final_output)
        print(f"\n✅ SUCCESS! Fixed {total_fixes} issues in {len(all_quest_fixes)} quests")
        print(f"📁 Fixed database saved to: {final_output}")
        print("\nTo use the fixed database:")
        print(f"  1. Backup current: cp {input_file} {input_file}.backup")
        print(f"  2. Apply fix: cp {final_output} {input_file}")
        print("  3. Restart WoW completely (not just /reload)")
    else:
        print(f"\n⚠️  Fixed {total_fixes} issues but validation still shows problems")
        print("Manual intervention may be required for remaining issues")
        print(f"Partially fixed file: {temp3}")
    
    # Clean up temp files
    print("\nCleaning up temporary files...")
    for temp_file in [temp1, temp2, temp3]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
    
    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)
    
    return 0 if is_valid else 1

if __name__ == "__main__":
    sys.exit(main())