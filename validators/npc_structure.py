#!/usr/bin/env python3
"""
Validator for NPC database structure issues.
Ensures all fields have the correct data types according to the spec.
"""

import re
from validator_base import ValidatorBase

class NpcStructureValidator(ValidatorBase):
    """Validates NPC database entries against the defined structure."""
    
    def name(self):
        return "NpcStructure"
    
    def description(self):
        return "Checking NPC database structure and field types"
    
    def validate_line(self, line, line_num, entry_type='npc'):
        """Validate NPC entry structure."""
        if entry_type != 'npc':
            return False, None, None
        
        # Skip non-entry lines
        if not line.strip().startswith('['):
            return False, None, None
        
        issues_found = []
        fixed_line = line
        
        # Extract NPC ID
        id_match = re.match(r'^\[(\d+)\]', line)
        if not id_match:
            return False, None, None
        
        npc_id = id_match.group(1)
        
        # Extract the data part after the = sign
        data_match = re.search(r'= \{(.+)\}', line)
        if not data_match:
            return False, None, None
        
        data = data_match.group(1)
        
        # Split by commas but be careful with nested structures
        # This is a simplified parser - for complex cases we'd need a proper Lua parser
        fields = self._split_fields(data)
        
        if len(fields) < 15:
            # Not enough fields, probably a partial entry
            return False, None, None
        
        # Validate each field according to the structure:
        # [1] name - string
        # [2] minLevelHealth - int or nil
        # [3] maxLevelHealth - int or nil  
        # [4] minLevel - int
        # [5] maxLevel - int
        # [6] rank - int
        # [7] spawns - table {[zoneId]={{x,y},...}}
        # [8] waypoints - table or nil
        # [9] zoneID - int
        # [10] questStarts - table {questId,...}
        # [11] questEnds - table {questId,...}
        # [12] factionID - int or nil
        # [13] friendlyToFaction - string or nil
        # [14] subName - string or nil
        # [15] npcFlags - int
        
        # Check field 10 (questStarts) - should be {id,id} or nil, not {{id}}
        if len(fields) >= 10:
            quest_starts = fields[9].strip()
            if quest_starts != 'nil' and re.match(r'^\{\{.*\}\}$', quest_starts):
                issues_found.append(f"NPC {npc_id} has double-wrapped questStarts: {quest_starts}")
                if self.auto_fix:
                    # Remove outer braces
                    fixed_starts = quest_starts[1:-1]
                    fields[9] = fixed_starts
        
        # Check field 11 (questEnds) - should be {id,id} or nil, not {{id}}
        if len(fields) >= 11:
            quest_ends = fields[10].strip()
            if quest_ends != 'nil' and re.match(r'^\{\{.*\}\}$', quest_ends):
                issues_found.append(f"NPC {npc_id} has double-wrapped questEnds: {quest_ends}")
                if self.auto_fix:
                    # Remove outer braces
                    fixed_ends = quest_ends[1:-1]
                    fields[10] = fixed_ends
        
        # Check field 7 (spawns) - should be {[zoneId]={{x,y},...}}
        if len(fields) >= 7:
            spawns = fields[6].strip()
            if spawns != 'nil':
                # Check for common mistakes like {[85]={{x,y}}} where 85 is invalid
                if re.search(r'\{\[85\]\s*=', spawns):
                    issues_found.append(f"NPC {npc_id} uses invalid zone 85 in spawns")
                    # Note: Auto-fix would need context about the correct zone
        
        # Check field 9 (zoneID) - should be a valid zone, not 85
        if len(fields) >= 9:
            zone_id = fields[8].strip()
            if zone_id == '85':
                issues_found.append(f"NPC {npc_id} has invalid zoneID 85")
                # Note: Auto-fix would need context about the correct zone
        
        # Check field 12 (factionID) - this is commonly confused with zoneID
        # factionID can be 85 (this is valid), but if it looks like coordinates follow, it's wrong
        if len(fields) >= 12:
            faction_id = fields[11].strip()
            # This field is often mistakenly used as a zone - no auto-fix without context
        
        # If we made fixes, reconstruct the line
        if self.auto_fix and issues_found:
            # Reconstruct the data string
            fixed_data = ','.join(fields)
            fixed_line = f'[{npc_id}] = {{{fixed_data}}}'
            
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