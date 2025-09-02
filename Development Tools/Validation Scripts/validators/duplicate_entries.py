#!/usr/bin/env python3
"""
Validator for duplicate quest/NPC IDs.
Detects when the same ID appears multiple times.
"""

import re
from validator_base import ValidatorBase

class DuplicateEntryValidator(ValidatorBase):
    """Detects duplicate quest or NPC IDs."""
    
    def __init__(self, auto_fix=False):
        super().__init__(auto_fix)
        self.seen_ids = set()
    
    def name(self):
        return "DuplicateIDs"
    
    def description(self):
        return "Checking for duplicate entry IDs"
    
    def validate_file(self, filepath, entry_type='quest'):
        """Override to track IDs across the file."""
        self.seen_ids = set()
        return super().validate_file(filepath, entry_type)
    
    def validate_line(self, line, line_num, entry_type='quest'):
        """Check if this ID has been seen before."""
        # Skip commented lines
        if line.strip().startswith('--'):
            return False, None, None
        
        # Extract ID
        id_match = re.match(r'^\[(\d+)\]', line.strip())
        if not id_match:
            return False, None, None
        
        entry_id = id_match.group(1)
        
        if entry_id in self.seen_ids:
            if self.auto_fix:
                # Comment out the duplicate
                fixed_line = f"-- DUPLICATE: {line}"
                return True, f"Duplicate {entry_type} ID {entry_id}", fixed_line
            else:
                return True, f"Duplicate {entry_type} ID {entry_id}", None
        
        self.seen_ids.add(entry_id)
        return False, None, None