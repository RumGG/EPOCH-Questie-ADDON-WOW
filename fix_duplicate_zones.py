#!/usr/bin/env python3
"""
Quick fix for duplicate zone spawns in NPC database.
Removes duplicate zone entries where the same zone appears twice.
"""

import re
import sys

def fix_duplicate_zones(filepath):
    """Remove duplicate zone spawns from NPC entries."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    fixes_made = 0
    
    for line in lines:
        if not line.strip().startswith('[') or not '},{[' in line:
            fixed_lines.append(line)
            continue
        
        # Check if this NPC has duplicate zones
        # Pattern: {[12]={{...}}},{[12]={{...}}}
        # The duplicates have the same zone ID and often identical coords
        
        # Extract the NPC ID
        npc_match = re.match(r'^\[(\d+)\]', line)
        if not npc_match:
            fixed_lines.append(line)
            continue
            
        npc_id = npc_match.group(1)
        
        # Look for duplicate zone patterns
        # Find all zone entries like [12]={{coords}}
        zone_pattern = r'\[(\d+)\]\=\{\{([^}]+(?:\}\}[^}]*)?)\}\}'
        zones_found = {}
        
        # Find all zones in the spawns field
        spawns_match = re.search(r',\{([^}]*(?:\{[^}]*\}[^}]*)*)\},', line)
        if spawns_match:
            spawns_content = spawns_match.group(1)
            
            # Extract each zone
            for zone_match in re.finditer(zone_pattern, spawns_content):
                zone_id = zone_match.group(1)
                coords = zone_match.group(2)
                
                # Only keep first occurrence of each zone
                if zone_id not in zones_found:
                    zones_found[zone_id] = coords
            
            # If we found duplicate zones, rebuild the line
            if len(zones_found) > 0:
                # Check if there were actually duplicates
                all_zones = re.findall(r'\[(\d+)\]\=', spawns_content)
                if len(all_zones) > len(zones_found):
                    print(f"NPC {npc_id}: Found {len(all_zones)} zone entries, keeping {len(zones_found)} unique zones")
                    
                    # Rebuild the spawns field
                    new_spawns = []
                    for zone_id, coords in zones_found.items():
                        new_spawns.append(f"[{zone_id}]={{{{{coords}}}}}")
                    
                    new_spawns_str = "{" + ",".join(new_spawns) + "}"
                    
                    # Replace the old spawns field with the new one
                    # Find the position of the spawns field (it's the 7th field, index 6)
                    parts = line.split(',')
                    
                    # Find which part contains the spawns
                    for i, part in enumerate(parts):
                        if '{[' in part and '={{' in part:
                            # Found the spawns field start
                            # Count braces to find the end
                            depth = 0
                            end_index = i
                            for j in range(i, len(parts)):
                                depth += parts[j].count('{') - parts[j].count('}')
                                if depth == 0:
                                    end_index = j
                                    break
                            
                            # Replace the spawns field
                            if end_index > i:
                                # Multiple parts
                                parts[i:end_index+1] = [new_spawns_str]
                            else:
                                # Single part - extract the beginning
                                before_spawns = part[:part.index('{')]
                                parts[i] = before_spawns + new_spawns_str
                            
                            line = ','.join(parts)
                            fixes_made += 1
                            break
        
        fixed_lines.append(line)
    
    # Write the fixed file
    output_path = filepath.replace('.lua', '_FIXED.lua')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed {fixes_made} NPCs with duplicate zone spawns")
    print(f"Output saved to: {output_path}")
    
    return fixes_made

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = 'Database/Epoch/epochNpcDB.lua'
    
    fix_duplicate_zones(filepath)