#!/usr/bin/env python3
"""
Validator for double dashes in quest/NPC names.
Double dashes (--) break Lua comments and must be escaped.
"""

import re
from validator_base import ValidatorBase

class DoubleDashValidator(ValidatorBase):
    """Detects and fixes double dashes in names that break Lua comments."""
    
    def name(self):
        return "DoubleDash"
    
    def description(self):
        return "Checking for double dashes (--) in names"
    
    def validate_line(self, line, line_num, entry_type='quest'):
        """Check if entry has double dash in name field."""
        # Extract the name field (first quoted string after the ID)
        name_pattern = r'^\[\d+\]\s*=\s*\{\s*"([^"]*)"'
        name_match = re.match(name_pattern, line)
        
        if name_match:
            name = name_match.group(1)
            if '--' in name:
                # Extract ID for reference
                id_match = re.match(r'^\[(\d+)\]', line)
                entry_id = id_match.group(1) if id_match else "unknown"
                
                if self.auto_fix:
                    fixed_line = self._fix_double_dash(line, name)
                    return True, f"{entry_type.capitalize()} {entry_id} name contains '--'", fixed_line
                else:
                    return True, f"{entry_type.capitalize()} {entry_id} name contains '--'", None
        
        return False, None, None
    
    def _fix_double_dash(self, line, name):
        """Replace double dash with single dash in name."""
        fixed_name = name.replace('--', '-')
        # Use exact replacement to avoid changing other parts
        old_pattern = f'"{name}"'
        new_pattern = f'"{fixed_name}"'
        # Only replace the first occurrence (the name field)
        return line.replace(old_pattern, new_pattern, 1)