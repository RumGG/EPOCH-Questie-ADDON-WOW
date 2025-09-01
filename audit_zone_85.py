#!/usr/bin/env python3
"""
Audit script for zone 85 (Tirisfal Glades) contamination
Identifies quests and NPCs that likely don't belong in this starter zone
"""

import re
import os

# Zone 85 is Tirisfal Glades - Undead starting zone (levels 1-10)
ZONE_ID = 85
EXPECTED_MAX_LEVEL = 12  # Allow a bit over 10 for zone transition quests

def parse_quest_db(filepath):
    """Parse epochQuestDB.lua for quests in zone 85"""
    suspicious_quests = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match quest entries
    # Format: [questId] = {"name", ..., level, ..., zone, ...}
    pattern = r'\[(\d+)\]\s*=\s*\{([^}]+)\}'
    
    for match in re.finditer(pattern, content):
        quest_id = match.group(1)
        quest_data = match.group(2)
        
        # Check if this quest is in zone 85
        if f',{ZONE_ID},' in quest_data or f',{ZONE_ID}}}' in quest_data:
            # Extract quest name and level
            parts = quest_data.split(',')
            
            # Name is first field (in quotes)
            name_match = re.search(r'"([^"]+)"', quest_data)
            quest_name = name_match.group(1) if name_match else "Unknown"
            
            # Level is typically 5th field (after name, quest giver, turn-in, nil)
            # Format: "name",{{giver}},{{turnin}},nil,level,...
            level = None
            try:
                # Count positions after the name
                level_pos = quest_data.find('nil,') 
                if level_pos > 0:
                    after_nil = quest_data[level_pos+4:].split(',')
                    if after_nil and after_nil[0].strip().isdigit():
                        level = int(after_nil[0].strip())
            except:
                pass
            
            # Check for suspicious patterns
            suspicious = False
            reasons = []
            
            # High level quest in starter zone
            if level and level > EXPECTED_MAX_LEVEL:
                suspicious = True
                reasons.append(f"Level {level} too high for starter zone")
            
            # Non-undead themed names in undead zone
            suspicious_keywords = ['Troll', 'Orc', 'Tauren', 'Thunder', 'Orgrimmar', 'Durotar', 
                                  'Sen\'jin', 'Vol\'jin', 'Darkspear', 'Banana', 'Crab', 'Shell',
                                  'Molten Core', 'Blackrock', 'Attunement', 'Raid', 'Dungeon',
                                  'Dustwallow', 'Tanaris', 'Feralas', 'Stranglethorn']
            for keyword in suspicious_keywords:
                if keyword.lower() in quest_name.lower():
                    suspicious = True
                    reasons.append(f"Name contains '{keyword}'")
            
            if suspicious:
                suspicious_quests.append({
                    'id': quest_id,
                    'name': quest_name,
                    'level': level,
                    'reasons': reasons,
                    'line': quest_data[:100] + '...' if len(quest_data) > 100 else quest_data
                })
    
    return suspicious_quests

def parse_npc_db(filepath):
    """Parse epochNpcDB.lua for NPCs in zone 85"""
    suspicious_npcs = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match NPC entries
    # Format: [npcId] = {"name", nil, nil, minLevel, maxLevel, ..., {[85] = {{coords}}}, ...}
    pattern = r'\[(\d+)\]\s*=\s*\{([^}]+\{[^}]*\[85\][^}]+\}[^}]*)\}'
    
    for match in re.finditer(pattern, content):
        npc_id = match.group(1)
        npc_data = match.group(2)
        
        # Extract NPC name
        name_match = re.search(r'"([^"]+)"', npc_data)
        npc_name = name_match.group(1) if name_match else "Unknown"
        
        # Extract level (4th and 5th fields after name and two nils)
        level_match = re.search(r'nil,\s*nil,\s*(\d+),\s*(\d+)', npc_data)
        min_level = None
        max_level = None
        if level_match:
            min_level = int(level_match.group(1))
            max_level = int(level_match.group(2))
        
        # Check for suspicious patterns
        suspicious = False
        reasons = []
        
        # High level NPC in starter zone
        if min_level and min_level > EXPECTED_MAX_LEVEL:
            suspicious = True
            reasons.append(f"Level {min_level}-{max_level} too high for starter zone")
        
        # Known NPCs that don't belong
        known_wrong = {
            'Lothos Riftwaker': 'Should be in Blackrock Mountain',
            'Vol\'jin': 'Should be in Orgrimmar',
            'Thrall': 'Should be in Orgrimmar',
            'Hemet Nesingwary': 'Should be in Stranglethorn Vale',
            'Scooty': 'Should be in Booty Bay',
            'Overlord Mok\'Morokk': 'Should be in Dustwallow Marsh',
            'Master Gadrin': 'Should be in Sen\'jin Village',
        }
        
        for wrong_npc, correct_location in known_wrong.items():
            if wrong_npc.lower() in npc_name.lower():
                suspicious = True
                reasons.append(correct_location)
        
        # Non-undead themed NPCs
        suspicious_keywords = ['Troll', 'Orc', 'Tauren', 'Gadrin', 'Sen\'jin', 'Vol\'jin',
                              'Darkspear', 'Orgrimmar', 'Thunder Bluff', 'Booty Bay',
                              'Dustwallow', 'Tanaris', 'Blackrock', 'Molten', 'Stranglethorn']
        for keyword in suspicious_keywords:
            if keyword.lower() in npc_name.lower():
                suspicious = True
                reasons.append(f"Name contains '{keyword}'")
        
        if suspicious:
            suspicious_npcs.append({
                'id': npc_id,
                'name': npc_name,
                'level': f"{min_level}-{max_level}" if min_level else "Unknown",
                'reasons': reasons
            })
    
    return suspicious_npcs

def main():
    base_path = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/Questie/Database/Epoch"
    
    print("=" * 80)
    print("ZONE 85 (TIRISFAL GLADES) CONTAMINATION AUDIT")
    print("=" * 80)
    print("\nTirisfal Glades is the Undead starting zone (levels 1-10)")
    print("Looking for quests and NPCs that don't belong...\n")
    
    # Audit Quests
    quest_db_path = os.path.join(base_path, "epochQuestDB.lua")
    if os.path.exists(quest_db_path):
        print("SUSPICIOUS QUESTS IN ZONE 85:")
        print("-" * 40)
        suspicious_quests = parse_quest_db(quest_db_path)
        
        if suspicious_quests:
            for quest in suspicious_quests:
                print(f"\nQuest {quest['id']}: {quest['name']}")
                print(f"  Level: {quest['level'] if quest['level'] else 'Unknown'}")
                print(f"  Issues: {', '.join(quest['reasons'])}")
        else:
            print("No obviously suspicious quests found")
    
    print("\n" + "=" * 40)
    
    # Audit NPCs
    npc_db_path = os.path.join(base_path, "epochNpcDB.lua")
    if os.path.exists(npc_db_path):
        print("SUSPICIOUS NPCs IN ZONE 85:")
        print("-" * 40)
        suspicious_npcs = parse_npc_db(npc_db_path)
        
        if suspicious_npcs:
            for npc in suspicious_npcs:
                print(f"\nNPC {npc['id']}: {npc['name']}")
                print(f"  Level: {npc['level']}")
                print(f"  Issues: {', '.join(npc['reasons'])}")
        else:
            print("No obviously suspicious NPCs found")
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print(f"Found {len(suspicious_quests) if 'suspicious_quests' in locals() else 0} suspicious quests")
    print(f"Found {len(suspicious_npcs) if 'suspicious_npcs' in locals() else 0} suspicious NPCs")
    print("\nThese items should be reviewed to determine their correct zone.")
    print("Common correct zones:")
    print("  - Durotar (14) for Orc/Troll quests")
    print("  - Orgrimmar (1637)")
    print("  - Thunder Bluff (1638)")
    print("  - Stranglethorn Vale (33)")
    print("  - Dustwallow Marsh (15)")
    print("  - Tanaris (440)")
    print("  - Blackrock Mountain (25)")

if __name__ == "__main__":
    main()