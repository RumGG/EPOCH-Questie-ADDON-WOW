#!/usr/bin/env python3

"""
Automated Testing Framework for Quest Database
Ensures no nesting issues and validates structure
"""

import re
import json

class QuestValidator:
    """Validates individual quests for correct structure"""
    
    @staticmethod
    def validate_quest_structure(quest_line):
        """
        Validate a quest line for proper structure
        Returns: (is_valid, errors)
        """
        errors = []
        
        # Check for quest ID
        if not re.match(r'^\[\d+\]', quest_line.strip()):
            errors.append("Missing quest ID")
            return False, errors
        
        # Extract quest data
        match = re.search(r'=\s*\{(.*)\}', quest_line)
        if not match:
            errors.append("Invalid quest structure")
            return False, errors
        
        quest_data = match.group(1)
        
        # Check for nesting issues
        if '{{{{' in quest_data:
            errors.append("Quadruple braces detected")
        
        # Check for improper triple braces
        if '{{{' in quest_data:
            # Check if it's in proper 6-element objectives structure
            objectives_pattern = r'\{\{\{[^}]+\}\},nil,nil,nil,nil,nil\}'
            if not re.search(objectives_pattern, quest_data):
                # Check if there are triple braces NOT in proper structure
                triple_matches = re.findall(r'\{\{\{[^}]+\}\}\}', quest_data)
                for match in triple_matches:
                    if ',nil,nil,nil,nil,nil}' not in match:
                        errors.append(f"Improper triple braces: {match[:50]}...")
                        break
        
        # Check brace balance for this quest
        open_count = quest_data.count('{')
        close_count = quest_data.count('}')
        if open_count != close_count:
            errors.append(f"Brace imbalance: {open_count} open, {close_count} close")
        
        # Check field count (should have approximately 30 fields)
        # Count top-level commas
        comma_count = 0
        brace_depth = 0
        in_string = False
        
        for i, char in enumerate(quest_data):
            if char == '"' and (i == 0 or quest_data[i-1] != '\\'):
                in_string = not in_string
            elif not in_string:
                if char == '{':
                    brace_depth += 1
                elif char == '}':
                    brace_depth -= 1
                elif char == ',' and brace_depth == 0:
                    comma_count += 1
        
        # Should have 29 commas for 30 fields
        if comma_count < 25 or comma_count > 35:
            errors.append(f"Unexpected field count: {comma_count + 1} fields (expected ~30)")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_objectives(objectives_str):
        """
        Validate objectives field specifically
        Returns: (is_valid, structure_info)
        """
        if objectives_str == 'nil':
            return True, "No objectives"
        
        # Check for proper 6-element structure
        if not objectives_str.startswith('{'):
            return False, "Objectives not wrapped in braces"
        
        # Count nil elements
        nil_count = objectives_str.count(',nil')
        
        # Should have 5 commas between 6 elements
        if nil_count < 3:
            return False, f"Insufficient structure elements (found {nil_count} nils)"
        
        # Check for over-nesting
        if '{{{{' in objectives_str:
            return False, "Quadruple nesting in objectives"
        
        # Check for proper creature/item/object format
        # Should be {{id,count}} or {{id,count,"name"}}
        creature_pattern = r'\{\{(\d+),(\d+)(?:,"[^"]*")?\}\}'
        matches = re.findall(creature_pattern, objectives_str)
        
        return True, f"Valid objectives with {len(matches)} entries"


class DatabaseTester:
    """Test entire database files"""
    
    def __init__(self):
        self.total_quests = 0
        self.valid_quests = 0
        self.invalid_quests = []
        self.error_summary = {}
    
    def test_database(self, filename):
        """
        Test a complete database file
        Returns: (pass_rate, error_summary)
        """
        print(f"Testing {filename}...")
        
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            # Skip non-quest lines
            if not (line.strip().startswith('[') and '=' in line):
                continue
            
            self.total_quests += 1
            
            # Extract quest ID
            quest_match = re.search(r'\[(\d+)\]', line)
            quest_id = quest_match.group(1) if quest_match else f"line_{line_num}"
            
            # Validate quest
            is_valid, errors = QuestValidator.validate_quest_structure(line)
            
            if is_valid:
                self.valid_quests += 1
            else:
                self.invalid_quests.append({
                    'quest_id': quest_id,
                    'line_num': line_num,
                    'errors': errors
                })
                
                # Track error types
                for error in errors:
                    error_type = error.split(':')[0]
                    if error_type not in self.error_summary:
                        self.error_summary[error_type] = 0
                    self.error_summary[error_type] += 1
        
        # Calculate pass rate
        pass_rate = (self.valid_quests / self.total_quests * 100) if self.total_quests > 0 else 0
        
        return pass_rate, self.error_summary
    
    def print_report(self):
        """Print detailed test report"""
        print("\n" + "=" * 70)
        print("TEST REPORT")
        print("=" * 70)
        
        print(f"Total quests tested: {self.total_quests}")
        print(f"Valid quests: {self.valid_quests} ✅")
        print(f"Invalid quests: {len(self.invalid_quests)} ❌")
        
        if self.total_quests > 0:
            pass_rate = (self.valid_quests / self.total_quests * 100)
            print(f"Pass rate: {pass_rate:.1f}%")
        
        if self.error_summary:
            print("\nError Summary:")
            for error_type, count in sorted(self.error_summary.items(), key=lambda x: x[1], reverse=True):
                print(f"  {error_type}: {count}")
        
        if self.invalid_quests:
            print(f"\nFirst 10 invalid quests:")
            for quest in self.invalid_quests[:10]:
                print(f"  Quest {quest['quest_id']} (line {quest['line_num']}):")
                for error in quest['errors']:
                    print(f"    - {error}")
        
        print("=" * 70)
        
        # Return overall pass/fail
        return len(self.invalid_quests) == 0


def compare_databases(file1, file2):
    """
    Compare two database files
    """
    print("=" * 70)
    print("DATABASE COMPARISON")
    print("=" * 70)
    
    tester1 = DatabaseTester()
    pass_rate1, errors1 = tester1.test_database(file1)
    
    tester2 = DatabaseTester()
    pass_rate2, errors2 = tester2.test_database(file2)
    
    print(f"\n{file1}:")
    print(f"  Pass rate: {pass_rate1:.1f}%")
    print(f"  Errors: {sum(errors1.values()) if errors1 else 0}")
    
    print(f"\n{file2}:")
    print(f"  Pass rate: {pass_rate2:.1f}%")
    print(f"  Errors: {sum(errors2.values()) if errors2 else 0}")
    
    if pass_rate2 > pass_rate1:
        print(f"\n✅ {file2} is {pass_rate2 - pass_rate1:.1f}% better!")
    elif pass_rate1 > pass_rate2:
        print(f"\n❌ {file2} is {pass_rate1 - pass_rate2:.1f}% worse!")
    else:
        print("\n➖ Both files have the same pass rate")
    
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 2:
        # Test single file
        tester = DatabaseTester()
        tester.test_database(sys.argv[1])
        tester.print_report()
    elif len(sys.argv) == 3:
        # Compare two files
        compare_databases(sys.argv[1], sys.argv[2])
    else:
        print("Usage:")
        print("  Test single file: python test_framework.py <database.lua>")
        print("  Compare files: python test_framework.py <original.lua> <fixed.lua>")
        sys.exit(1)