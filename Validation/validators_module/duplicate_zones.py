#!/usr/bin/env python3
"""
Validator for duplicate zone spawns in NPC entries.
Detects and fixes NPCs that have the same zone listed multiple times.
"""

import re
from validator_base import ValidatorBase

class DuplicateZoneValidator(ValidatorBase):
    """Detects and fixes duplicate zone spawns in NPC entries."""
    
    def name(self):
        return "DuplicateZones"
    
    def description(self):
        return "Checking for duplicate zone spawns in NPC entries"
    
    def validate_line(self, line, line_num, entry_type='npc'):
        """Check if an NPC has duplicate zone entries."""
        if entry_type != 'npc':
            return False, None, None
        
        # Look for zone IDs in the spawns field
        zones = re.findall(r'\[(\d+)\]=\{', line)
        
        if len(zones) != len(set(zones)):
            # Found duplicates
            duplicate_zones = [z for z in zones if zones.count(z) > 1]
            unique_dupes = list(set(duplicate_zones))
            
            if self.auto_fix:
                # Remove duplicate zone entries
                fixed_line = self._remove_duplicate_zones(line)
                return True, f"NPC has duplicate zones: {unique_dupes}", fixed_line
            else:
                return True, f"NPC has duplicate zones: {unique_dupes}", None
        
        return False, None, None
    
    def _remove_duplicate_zones(self, line):
        """Remove duplicate zone entries from an NPC line."""
        # Extract NPC ID for reference
        npc_match = re.match(r'^\[(\d+)\]', line)
        if not npc_match:
            return line
        
        # Find the spawns field (typically field 7, index 6)
        # Pattern: {[zone1]={{coords}}, [zone2]={{coords}}}
        
        # Split the line into parts
        parts = []
        current = ""
        depth = 0
        in_string = False
        
        for char in line:
            if char == '"' and (len(current) == 0 or current[-1] != '\\'):
                in_string = not in_string
            elif not in_string:
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                elif char == ',' and depth == 1:
                    parts.append(current)
                    current = ""
                    continue
            current += char
        
        if current:
            parts.append(current)
        
        # Find and fix the spawns field
        for i, part in enumerate(parts):
            if '{[' in part and '={{' in part:
                # This looks like the spawns field
                # Extract unique zones
                zone_data = {}
                
                # Find all [zoneId]={{coordinates}} patterns
                zone_matches = re.finditer(r'\[(\d+)\]=\{\{([^}]+(?:\}[^}]+)?)\}\}', part)
                
                for match in zone_matches:
                    zone_id = match.group(1)
                    coords = match.group(2)
                    
                    # Only keep first occurrence of each zone
                    if zone_id not in zone_data:
                        zone_data[zone_id] = coords
                
                if zone_data:
                    # Rebuild the spawns field
                    # Find the prefix (everything before the first [)
                    prefix = part[:part.index('[')]
                    
                    # Build new spawns
                    new_spawns = []
                    for zone_id, coords in zone_data.items():
                        new_spawns.append(f"[{zone_id}]={{{{{coords}}}}}")
                    
                    parts[i] = prefix + "{" + ",".join(new_spawns) + "}"
                    break
        
        # Reconstruct the line
        return ','.join(parts)