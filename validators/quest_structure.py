#!/usr/bin/env python3
"""
Validator for Quest database structure issues.
Ensures all fields have the correct data types according to the spec.
"""

import re
from validator_base import ValidatorBase

class QuestStructureValidator(ValidatorBase):
    """Validates Quest database entries against the defined structure."""
    
    def name(self):
        return "QuestStructure"
    
    def description(self):
        return "Checking Quest database structure and field types"
    
    def validate_line(self, line, line_num, entry_type='quest'):
        """Validate Quest entry structure."""
        if entry_type != 'quest':
            return False, None, None
        
        # Skip non-entry lines
        if not line.strip().startswith('['):
            return False, None, None
        
        issues_found = []
        fixed_line = line
        
        # Extract Quest ID
        id_match = re.match(r'^\[(\d+)\]', line)
        if not id_match:
            return False, None, None
        
        quest_id = id_match.group(1)
        
        # Extract the data part after the = sign
        data_match = re.search(r'= \{(.+)\}', line)
        if not data_match:
            return False, None, None
        
        data = data_match.group(1)
        
        # Split by commas but be careful with nested structures
        fields = self._split_fields(data)
        
        if len(fields) < 17:
            # Not enough fields for a valid quest entry
            return False, None, None
        
        # Validate key fields according to the structure:
        # [1] name - string
        # [2] startedBy - {{NPCs},{Objects},{Items}} or nil
        # [3] finishedBy - {{NPCs},{Objects}} or nil
        # [4] requiredLevel - int or nil
        # [5] questLevel - int
        # [6] requiredRaces - bitmask or nil
        # [7] requiredClasses - bitmask or nil
        # [8] objectivesText - {string,...} or nil
        # [9] triggerEnd - complex or nil
        # [10] objectives - complex or nil
        # ...
        # [17] zoneOrSort - int
        
        # Check field 4 (requiredLevel) - should be number or nil, not {{number}}
        if len(fields) >= 4:
            req_level = fields[3].strip()
            if req_level != 'nil' and re.match(r'^\{\{?\d+\}?\}$', req_level):
                issues_found.append(f"Quest {quest_id} has wrapped requiredLevel: {req_level}")
                if self.auto_fix:
                    # Extract just the number
                    num_match = re.search(r'\d+', req_level)
                    if num_match:
                        fields[3] = num_match.group()
        
        # Check field 5 (questLevel) - should be number, not {number} or {{number}}
        if len(fields) >= 5:
            quest_level = fields[4].strip()
            if quest_level != 'nil' and re.match(r'^\{\{?\d+\}?\}$', quest_level):
                issues_found.append(f"Quest {quest_id} has wrapped questLevel: {quest_level}")
                if self.auto_fix:
                    # Extract just the number
                    num_match = re.search(r'\d+', quest_level)
                    if num_match:
                        fields[4] = num_match.group()
        
        # Check field 17 (zoneOrSort) - should be number, not wrapped
        if len(fields) >= 17:
            zone_or_sort = fields[16].strip()
            if zone_or_sort != 'nil' and re.match(r'^\{\{?\d+\}?\}$', zone_or_sort):
                issues_found.append(f"Quest {quest_id} has wrapped zoneOrSort: {zone_or_sort}")
                if self.auto_fix:
                    # Extract just the number
                    num_match = re.search(r'\d+', zone_or_sort)
                    if num_match:
                        fields[16] = num_match.group()
        
        # Check field 2 (startedBy) structure - should be {{NPCs},{Objects},{Items}}
        if len(fields) >= 2:
            started_by = fields[1].strip()
            if started_by != 'nil':
                # Check for common mistake: {npcId} instead of {{npcId}}
                if re.match(r'^\{\d+\}$', started_by):
                    issues_found.append(f"Quest {quest_id} has incorrectly formatted startedBy (should be {{{{NPCs}},{{Objects}},{{Items}}}})")
                    if self.auto_fix:
                        # Wrap it correctly as NPC start
                        fields[1] = '{' + started_by + '}'
        
        # Check field 3 (finishedBy) structure - should be {{NPCs},{Objects}}
        if len(fields) >= 3:
            finished_by = fields[2].strip()
            if finished_by != 'nil':
                # Check for common mistake: {npcId} instead of {{npcId}}
                if re.match(r'^\{\d+\}$', finished_by):
                    issues_found.append(f"Quest {quest_id} has incorrectly formatted finishedBy (should be {{{{NPCs}},{{Objects}}}})")
                    if self.auto_fix:
                        # Wrap it correctly as NPC end
                        fields[2] = '{' + finished_by + '}'
        
        # Check objectives field (position 10) - common structure issues
        if len(fields) >= 10:
            objectives = fields[9].strip()
            if objectives != 'nil':
                # Check for double-wrapped kill objectives like {{{{{npcId,count}}}}
                if re.search(r'\{\{\{\{\{', objectives):
                    issues_found.append(f"Quest {quest_id} has excessively nested objectives")
                    # This is too complex to auto-fix safely
        
        # Check for invalid zone 85
        if len(fields) >= 17:
            zone_or_sort = fields[16].strip()
            if zone_or_sort == '85':
                issues_found.append(f"Quest {quest_id} uses invalid zone 85 (zone doesn't exist)")
                # Can't auto-fix without knowing the correct zone
        
        # If we made fixes, reconstruct the line
        if self.auto_fix and issues_found and any('has wrapped' in issue for issue in issues_found):
            # Reconstruct the data string
            fixed_data = ','.join(fields)
            fixed_line = f'[{quest_id}] = {{{fixed_data}}}'
            
            # Preserve any trailing comment
            comment_match = re.search(r'(,?\s*--.*?)$', line)
            if comment_match:
                fixed_line = fixed_line.rstrip() + comment_match.group(1)
            
            fixed_line += '\n' if line.endswith('\n') else ''
        
        if issues_found:
            if self.auto_fix and fixed_line != line:
                return True, ", ".join(issues_found), fixed_line
            else:
                return True, ", ".join(issues_found), None
        
        return False, None, None
    
    def _split_fields(self, data):
        """Split fields while respecting nested structures."""
        fields = []
        current_field = ""
        depth = 0
        in_string = False
        escape_next = False
        
        for char in data:
            if escape_next:
                current_field += char
                escape_next = False
                continue
            
            if char == '\\':
                escape_next = True
                current_field += char
                continue
            
            if char == '"' and not in_string:
                in_string = True
                current_field += char
            elif char == '"' and in_string:
                in_string = False
                current_field += char
            elif not in_string:
                if char == '{':
                    depth += 1
                    current_field += char
                elif char == '}':
                    depth -= 1
                    current_field += char
                elif char == ',' and depth == 0:
                    fields.append(current_field)
                    current_field = ""
                else:
                    current_field += char
            else:
                current_field += char
        
        # Add the last field
        if current_field:
            fields.append(current_field)
        
        return fields