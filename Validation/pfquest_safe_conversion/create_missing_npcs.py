#!/usr/bin/env python3
"""
Create NPC stub entries for NPCs referenced in pfQuest but missing from our database
"""

import re
from typing import Dict, Set, List

def get_quest_npc_relationships(quest_file: str):
    """Extract which NPCs start/end which quests"""
    
    npc_data = {}
    
    with open(quest_file, 'r', encoding='utf-8') as f:
        for line in f:
            # Match quest entry
            match = re.match(r'\s*\[(\d+)\]\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', line)
            if not match:
                continue
            
            quest_id = int(match.group(1))
            quest_data = match.group(2)
            
            # Parse fields
            fields = []
            current = ""
            depth = 0
            in_string = False
            
            for char in quest_data:
                if char == '"' and (not current or current[-1] != '\\'):
                    in_string = not in_string
                
                if not in_string:
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                    elif char == ',' and depth == 0:
                        fields.append(current.strip())
                        current = ""
                        continue
                
                current += char
            
            if current.strip():
                fields.append(current.strip())
            
            # Get quest name
            quest_name = fields[0].strip('"') if fields else f"Quest {quest_id}"
            
            # Extract start NPCs (field 2)
            if len(fields) > 1 and fields[1] != 'nil':
                npc_matches = re.findall(r'\{(\d+)\}', fields[1])
                for npc_id_str in npc_matches:
                    npc_id = int(npc_id_str)
                    if npc_id not in npc_data:
                        npc_data[npc_id] = {
                            'starts': [],
                            'ends': [],
                            'quest_names': {}
                        }
                    npc_data[npc_id]['starts'].append(quest_id)
                    npc_data[npc_id]['quest_names'][quest_id] = quest_name
            
            # Extract end NPCs (field 3)
            if len(fields) > 2:
                # Handle both {{npc}} and just npc formats
                if '{{' in fields[2]:
                    npc_matches = re.findall(r'\{(\d+)\}', fields[2])
                else:
                    # Single NPC ID without braces
                    npc_match = re.match(r'^(\d+)$', fields[2])
                    if npc_match:
                        npc_matches = [npc_match.group(1)]
                    else:
                        npc_matches = []
                
                for npc_id_str in npc_matches:
                    npc_id = int(npc_id_str)
                    if npc_id not in npc_data:
                        npc_data[npc_id] = {
                            'starts': [],
                            'ends': [],
                            'quest_names': {}
                        }
                    npc_data[npc_id]['ends'].append(quest_id)
                    npc_data[npc_id]['quest_names'][quest_id] = quest_name
    
    return npc_data

def create_npc_entries(npc_data: Dict, existing_npc_file: str):
    """Create NPC entries for missing NPCs"""
    
    # Load existing NPCs
    existing_npcs = set()
    with open(existing_npc_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r'\s*\[(\d+)\]', line)
            if match:
                existing_npcs.add(int(match.group(1)))
    
    # Generate entries for missing NPCs
    npc_entries = []
    missing_npcs = []
    
    for npc_id in sorted(npc_data.keys()):
        if npc_id in existing_npcs:
            continue
        
        missing_npcs.append(npc_id)
        data = npc_data[npc_id]
        
        # Determine NPC role and name
        if data['starts'] and data['ends']:
            npc_name = f"Quest NPC {npc_id}"
            npc_role = "Quest Giver & Turn-in"
        elif data['starts']:
            # Use quest name to infer NPC name
            sample_quest = list(data['quest_names'].values())[0]
            npc_name = f"Quest Giver {npc_id}"
            npc_role = "Quest Giver"
        else:
            npc_name = f"Quest Turn-in {npc_id}"
            npc_role = "Quest Turn-in"
        
        # Build NPC entry (15 fields required)
        entry_parts = [
            f'[{npc_id}]',
            ' = {',
            f'"{npc_name}",',  # 1. name
            'nil,',             # 2. minLevelHealth
            'nil,',             # 3. maxLevelHealth
            '1,',               # 4. minLevel
            '60,',              # 5. maxLevel
            '0,',               # 6. rank (0=normal)
            'nil,',             # 7. spawns (no coords yet)
            'nil,',             # 8. waypoints
            '0,',               # 9. zoneID (unknown)
        ]
        
        # 10. questStarts
        if data['starts']:
            entry_parts.append('{' + ','.join(str(q) for q in sorted(data['starts'])) + '},')
        else:
            entry_parts.append('nil,')
        
        # 11. questEnds
        if data['ends']:
            entry_parts.append('{' + ','.join(str(q) for q in sorted(data['ends'])) + '},')
        else:
            entry_parts.append('nil,')
        
        # 12-15: remaining fields
        entry_parts.extend([
            'nil,',      # 12. factionID
            '"AH",',     # 13. friendlyToFaction (both)
            f'"{npc_role}",',  # 14. subName
            '2'          # 15. npcFlags (2=questgiver)
        ])
        
        entry_parts.append(f'}}, -- pfQuest NPC ({npc_role})')
        
        npc_entries.append(''.join(entry_parts))
    
    return npc_entries, missing_npcs

def main():
    print("="*70)
    print("CREATING MISSING NPC ENTRIES")
    print("="*70)
    
    # Get NPC quest relationships
    print("\nAnalyzing quest-NPC relationships...")
    npc_data = get_quest_npc_relationships('pfquest_properly_converted_FIXED.lua')
    print(f"Found {len(npc_data)} unique NPCs in quests")
    
    # Create NPC entries
    print("\nCreating NPC entries for missing NPCs...")
    npc_entries, missing_npcs = create_npc_entries(npc_data, 'epochNpcDB.lua')
    
    print(f"Created {len(npc_entries)} NPC stub entries")
    
    # Write to file
    output_file = 'pfquest_missing_npcs.lua'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('-- Missing NPCs from pfQuest converted quests\n')
        f.write('-- These stub entries need coordinates added via in-game collection\n')
        f.write(f'-- Total: {len(npc_entries)} NPCs\n\n')
        f.write('pfQuestMissingNPCs = {\n')
        
        for entry in npc_entries:
            f.write(f'  {entry}\n')
        
        f.write('}\n\n')
        f.write('-- Missing NPC IDs for reference:\n')
        f.write(f'-- {missing_npcs}\n')
    
    print(f"\n✅ Wrote {len(npc_entries)} NPC entries to: {output_file}")
    
    # Show summary
    print("\n" + "="*70)
    print("NPC SUMMARY")
    print("="*70)
    
    quest_givers = sum(1 for d in npc_data.values() if d['starts'])
    quest_enders = sum(1 for d in npc_data.values() if d['ends'])
    both = sum(1 for d in npc_data.values() if d['starts'] and d['ends'])
    
    print(f"Quest Givers: {quest_givers}")
    print(f"Quest Turn-ins: {quest_enders}")
    print(f"Both Giver & Turn-in: {both}")
    
    print("\nSample NPCs created:")
    for i, npc_id in enumerate(missing_npcs[:5]):
        data = npc_data[npc_id]
        print(f"\nNPC {npc_id}:")
        if data['starts']:
            print(f"  Starts quests: {data['starts'][:3]}")
        if data['ends']:
            print(f"  Ends quests: {data['ends'][:3]}")
        sample_quest = list(data['quest_names'].values())[0] if data['quest_names'] else "Unknown"
        print(f"  Sample quest: {sample_quest}")

if __name__ == "__main__":
    main()