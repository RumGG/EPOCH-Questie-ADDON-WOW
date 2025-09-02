#!/usr/bin/env python3
"""
Validator for nil objective IDs in quest entries.
Detects and fixes quests with {{{nil, in objectives field.
"""

import re
from validator_base import ValidatorBase

class NilObjectiveValidator(ValidatorBase):
    """Detects and fixes nil objective IDs that cause parsing errors."""
    
    def name(self):
        return "NilObjectives"
    
    def description(self):
        return "Checking for nil objective IDs in quest entries"
    
    def validate_line(self, line, line_num, entry_type='quest'):
        """Check if a quest has nil objective IDs."""
        if entry_type != 'quest':
            return False, None, None
        
        # Look for {{{nil, pattern in objectives field
        if '{{{nil,' in line:
            # Extract quest ID
            quest_match = re.match(r'^\[(\d+)\]', line)
            quest_id = quest_match.group(1) if quest_match else "unknown"
            
            if self.auto_fix:
                fixed_line = self._fix_nil_objectives(line)
                return True, f"Quest {quest_id} has nil objective ID", fixed_line
            else:
                return True, f"Quest {quest_id} has nil objective ID", None
        
        return False, None, None
    
    def _fix_nil_objectives(self, line):
        """Convert nil objectives to spell objectives."""
        # Two common patterns:
        # 1. {{{nil,"text",count}}} 
        # 2. {{{nil,count,"text"}}}
        
        # Try pattern 1: text before count
        pattern1 = r'\{\{\{nil,(".*?"),(\d+)\}\}\}'
        match = re.search(pattern1, line)
        
        if match:
            text = match.group(1)
            count = match.group(2)
            # Replace with spell objective (position 6)
            replacement = f"{{nil,nil,nil,nil,nil,{{{{1,{text},{count}}}}}}}"
            return re.sub(pattern1, replacement, line)
        
        # Try pattern 2: count before text
        pattern2 = r'\{\{\{nil,(\d+),(".*?")\}\}\}'
        match = re.search(pattern2, line)
        
        if match:
            count = match.group(1)
            text = match.group(2)
            # Replace with spell objective (position 6)
            # Note: spell objectives are {spellId, "text", count}
            replacement = f"{{nil,nil,nil,nil,nil,{{{{1,{text},{count}}}}}}}"
            return re.sub(pattern2, replacement, line)
        
        return line