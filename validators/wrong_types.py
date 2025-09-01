#!/usr/bin/env python3
"""
Validator for wrong data types in quest fields.
Detects fields that should be numbers but are tables.
"""

import re
from validator_base import ValidatorBase

class WrongTypeValidator(ValidatorBase):
    """Detects and fixes wrong data types in quest fields."""
    
    def name(self):
        return "WrongTypes"
    
    def description(self):
        return "Checking for wrong data types (e.g., {{number}} instead of number)"
    
    def validate_line(self, line, line_num, entry_type='quest'):
        """Check if quest has wrong data types."""
        if entry_type != 'quest':
            return False, None, None
        
        issues_found = []
        fixed_line = line
        
        # Extract quest ID
        id_match = re.match(r'^\[(\d+)\]', line)
        quest_id = id_match.group(1) if id_match else "unknown"
        
        # Check for common wrong type patterns
        # Pattern: {{number}} or {number} where a plain number is expected
        
        # Split into fields (careful with nested structures)
        # Look for specific field positions that should be numbers
        
        # requiredLevel (field 4) and questLevel (field 5) patterns
        # These appear after the finishedBy field
        
        # Look for specific problematic patterns
        # We need to be careful - startedBy and finishedBy fields SHOULD have {{npcId}}
        # Only fix when we see patterns like ,{{45845}}, or ,{46324}, in wrong positions
        
        # Check for requiredLevel/questLevel position errors
        # These come after finishedBy (position 3) and before requiredRaces (position 6)
        # Pattern: }},{{number}}, or }},{number},
        patterns_to_fix = []
        
        # Check if it looks like requiredLevel or questLevel is a table
        if re.search(r'\}\},\{\{(\d+)\}\},\d+,', line):
            # Looks like requiredLevel is {{number}} - should be just number
            patterns_to_fix.append((r'\}\},\{\{(\d+)\}\},', r'}},\1,'))
        
        if re.search(r',\{\{(\d+)\}\},nil,\d+,', line):
            # Another pattern for wrong requiredLevel
            patterns_to_fix.append((r',\{\{(\d+)\}\},nil,', r',\1,nil,'))
        
        for pattern, replacement in patterns_to_fix:
            if re.search(pattern, fixed_line):
                issues_found.append(f"Quest {quest_id} has wrong data type")
                if self.auto_fix:
                    fixed_line = re.sub(pattern, replacement, fixed_line)
        
        if issues_found:
            if self.auto_fix and fixed_line != line:
                return True, ", ".join(issues_found), fixed_line
            else:
                return True, ", ".join(issues_found), None
        
        return False, None, None