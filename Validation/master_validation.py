#!/usr/bin/env python3

"""
Master Validation Pipeline for pfQuest to Questie Conversion
Runs the complete validation and merge process with safety checks
"""

import os
import sys
import subprocess
from datetime import datetime
import shutil

class MasterValidator:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = f"backups/session_{self.timestamp}"
        self.reports = []
        
    def run_command(self, cmd, description):
        """Run a command and capture output"""
        print(f"\n{'='*70}")
        print(f"Running: {description}")
        print(f"Command: {cmd}")
        print('='*70)
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Success")
                if result.stdout:
                    print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
                return True, result.stdout
            else:
                print(f"❌ Failed with return code {result.returncode}")
                if result.stderr:
                    print(result.stderr)
                return False, result.stderr
        except Exception as e:
            print(f"❌ Exception: {e}")
            return False, str(e)
    
    def create_backup(self):
        """Create backup of current database"""
        print(f"\n📁 Creating backup in {self.backup_dir}/")
        os.makedirs("backups", exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Backup the main database
        if os.path.exists("../Database/Epoch/epochQuestDB.lua"):
            shutil.copy("../Database/Epoch/epochQuestDB.lua", 
                       f"{self.backup_dir}/epochQuestDB_backup.lua")
            print("✅ Backed up epochQuestDB.lua")
            return True
        else:
            print("❌ Database file not found!")
            return False
    
    def test_current_database(self):
        """Test the current database state"""
        success, output = self.run_command(
            "python3 test_framework.py ../Database/Epoch/epochQuestDB.lua",
            "Testing current database"
        )
        
        # Extract pass rate from output
        if success and "Pass rate:" in output:
            for line in output.split('\n'):
                if "Pass rate:" in line:
                    self.reports.append(f"Current database: {line.strip()}")
                    pass_rate = float(line.split(':')[1].strip().rstrip('%'))
                    return pass_rate
        return 0.0
    
    def convert_pfquest_data(self, pfquest_data, pfquest_text, output_file):
        """Convert pfQuest data to Questie format"""
        if not os.path.exists(pfquest_data) or not os.path.exists(pfquest_text):
            print(f"❌ pfQuest files not found: {pfquest_data} or {pfquest_text}")
            return False
            
        success, output = self.run_command(
            f"python3 correct_converter.py {pfquest_data} {pfquest_text} {output_file}",
            "Converting pfQuest data"
        )
        return success
    
    def test_converted_data(self, converted_file):
        """Test the converted data"""
        success, output = self.run_command(
            f"python3 test_framework.py {converted_file}",
            "Testing converted data"
        )
        
        if success and "Pass rate:" in output:
            for line in output.split('\n'):
                if "Pass rate:" in line:
                    self.reports.append(f"Converted data: {line.strip()}")
                    pass_rate = float(line.split(':')[1].strip().rstrip('%'))
                    return pass_rate
        return 0.0
    
    def merge_with_existing(self):
        """Run smart merge to combine with existing database"""
        success, output = self.run_command(
            "python3 smart_merge_pfquest.py",
            "Smart merging with existing database"
        )
        
        if success:
            # Check if merge report was created
            if os.path.exists("smart_merge_report.txt"):
                with open("smart_merge_report.txt", 'r') as f:
                    report = f.read()
                    print("\n📊 Merge Report Summary:")
                    for line in report.split('\n')[:20]:  # First 20 lines
                        print(f"  {line}")
            return True
        return False
    
    def apply_fixes(self, input_file, output_file):
        """Apply comprehensive fixes to database"""
        success, output = self.run_command(
            f"python3 comprehensive_fixer.py {input_file} {output_file}",
            "Applying comprehensive fixes"
        )
        
        if not success:
            # Try edge case fixers
            print("Trying edge case fixers...")
            shutil.copy(input_file, "temp_fix.lua")
            
            # Run edge case fixer v2
            success2, _ = self.run_command(
                "python3 fix_edge_cases_v2.py",
                "Applying edge case fixes"
            )
            
            if success2 and os.path.exists("../Database/Epoch/epochQuestDB_EDGE_FIXED_V2.lua"):
                shutil.copy("../Database/Epoch/epochQuestDB_EDGE_FIXED_V2.lua", output_file)
                return True
                
        return success
    
    def validate_and_apply(self, candidate_file, threshold=99.0):
        """Validate a candidate file and apply if it passes threshold"""
        pass_rate = self.test_converted_data(candidate_file)
        
        if pass_rate >= threshold:
            print(f"\n✅ Validation passed with {pass_rate:.1f}% (threshold: {threshold}%)")
            
            # Ask for confirmation
            response = input("\nApply this to the main database? (yes/no): ").lower().strip()
            if response == 'yes':
                shutil.copy(candidate_file, "../Database/Epoch/epochQuestDB.lua")
                print("✅ Database updated successfully!")
                print("⚠️  Remember to restart WoW completely to test in-game")
                return True
            else:
                print("ℹ️  Database update cancelled")
                return False
        else:
            print(f"\n❌ Validation failed: {pass_rate:.1f}% < {threshold}% threshold")
            return False
    
    def print_final_report(self):
        """Print final summary report"""
        print("\n" + "="*70)
        print("FINAL VALIDATION REPORT")
        print("="*70)
        
        for report in self.reports:
            print(f"  • {report}")
        
        print("\n" + "="*70)
        print("Backup location: " + self.backup_dir)
        print("="*70)


def main():
    """Main validation pipeline"""
    print("="*70)
    print("MASTER VALIDATION PIPELINE")
    print("="*70)
    
    validator = MasterValidator()
    
    # Step 1: Backup
    if not validator.create_backup():
        print("❌ Failed to create backup, aborting")
        return 1
    
    # Step 2: Test current state
    current_pass_rate = validator.test_current_database()
    print(f"\n📊 Current database pass rate: {current_pass_rate:.1f}%")
    
    # Step 3: Check what operation to perform
    print("\nSelect operation:")
    print("1. Convert new pfQuest data and merge")
    print("2. Fix existing database issues")
    print("3. Test and validate only")
    print("4. Merge already converted data")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        # Convert and merge new data
        pfquest_data = input("Enter path to pfquest data file: ").strip()
        pfquest_text = input("Enter path to pfquest text file: ").strip()
        
        if validator.convert_pfquest_data(pfquest_data, pfquest_text, "converted_temp.lua"):
            conv_pass_rate = validator.test_converted_data("converted_temp.lua")
            
            if conv_pass_rate > 95:
                print(f"✅ Converted data is {conv_pass_rate:.1f}% valid")
                
                if validator.merge_with_existing():
                    if os.path.exists("epochQuestDB_MERGED_SMART.lua"):
                        validator.validate_and_apply("epochQuestDB_MERGED_SMART.lua")
            else:
                print(f"❌ Converted data has issues ({conv_pass_rate:.1f}% valid)")
                if validator.apply_fixes("converted_temp.lua", "converted_fixed.lua"):
                    validator.validate_and_apply("converted_fixed.lua")
    
    elif choice == '2':
        # Fix existing database
        if current_pass_rate < 99:
            print(f"Database needs fixing (current: {current_pass_rate:.1f}%)")
            if validator.apply_fixes("../Database/Epoch/epochQuestDB.lua", "fixed_temp.lua"):
                validator.validate_and_apply("fixed_temp.lua")
        else:
            print(f"Database is already at {current_pass_rate:.1f}% validity")
    
    elif choice == '3':
        # Test only
        print("\nTest complete. No changes made.")
    
    elif choice == '4':
        # Merge existing converted data
        if validator.merge_with_existing():
            if os.path.exists("epochQuestDB_MERGED_SMART.lua"):
                validator.validate_and_apply("epochQuestDB_MERGED_SMART.lua")
    
    # Print final report
    validator.print_final_report()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())