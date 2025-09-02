#!/usr/bin/env python3

"""
Enhanced pfQuest to Questie converter that properly extracts objective data
Including mob IDs, item IDs, and object IDs from the 'obj' field
"""

import re
from datetime import datetime

def parse_pfquest_database(data_file, text_file):
    """Parse pfQuest database files"""
    
    # Read data file
    with open(data_file, 'r', encoding='utf-8') as f:
        data_content = f.read()
    
    # Read text file
    with open(text_file, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    # Parse quest data
    quests = {}
    quest_pattern = r'\[(\d+)\]\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    
    for match in re.finditer(quest_pattern, data_content):
        quest_id = int(match.group(1))
        quest_data = match.group(2)
        
        quest = {
            'id': quest_id,
            'start_npcs': [],
            'end_npcs': [],
            'level': None,
            'race': None,
            'objectives': {},
            'prerequisite': None,
            'next_quest': None
        }
        
        # Extract starts
        start_match = re.search(r'"start"\s*=\s*\{([^}]*)\}', quest_data)
        if start_match:
            start_content = start_match.group(1)
            # Extract NPCs
            npc_matches = re.findall(r'\["U"\]\s*=\s*(\d+)', start_content)
            quest['start_npcs'] = [int(npc) for npc in npc_matches]
        
        # Extract ends
        end_match = re.search(r'"end"\s*=\s*\{([^}]*)\}', quest_data)
        if end_match:
            end_content = end_match.group(1)
            # Extract NPCs
            npc_matches = re.findall(r'\["U"\]\s*=\s*(\d+)', end_content)
            quest['end_npcs'] = [int(npc) for npc in npc_matches]
        
        # Extract level and race
        level_match = re.search(r'"level"\s*=\s*(\d+)', quest_data)
        if level_match:
            quest['level'] = int(level_match.group(1))
        
        race_match = re.search(r'"race"\s*=\s*(\d+)', quest_data)
        if race_match:
            quest['race'] = int(race_match.group(1))
        
        # Extract objectives - THIS IS THE KEY PART
        obj_match = re.search(r'"obj"\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', quest_data)
        if obj_match:
            obj_content = obj_match.group(1)
            
            # Extract mob kills (U = Unit/NPC)
            mob_matches = re.findall(r'\["U"\]\s*=\s*\{([^}]*)\}', obj_content)
            for mob_match in mob_matches:
                # Parse mob ID and count
                mob_data = re.findall(r'(\d+)\s*,\s*(\d+)', mob_match)
                for mob_id, count in mob_data:
                    if 'mobs' not in quest['objectives']:
                        quest['objectives']['mobs'] = []
                    quest['objectives']['mobs'].append({
                        'id': int(mob_id),
                        'count': int(count)
                    })
            
            # Extract items (I = Item)
            item_matches = re.findall(r'\["I"\]\s*=\s*\{([^}]*)\}', obj_content)
            for item_match in item_matches:
                # Parse item ID and count
                item_data = re.findall(r'(\d+)\s*,\s*(\d+)', item_match)
                for item_id, count in item_data:
                    if 'items' not in quest['objectives']:
                        quest['objectives']['items'] = []
                    quest['objectives']['items'].append({
                        'id': int(item_id),
                        'count': int(count)
                    })
            
            # Extract objects (O = Object)
            obj_matches = re.findall(r'\["O"\]\s*=\s*\{([^}]*)\}', obj_content)
            for obj_match in obj_matches:
                # Parse object ID and count
                obj_data = re.findall(r'(\d+)\s*,\s*(\d+)', obj_match)
                for obj_id, count in obj_data:
                    if 'objects' not in quest['objectives']:
                        quest['objectives']['objects'] = []
                    quest['objectives']['objects'].append({
                        'id': int(obj_id),
                        'count': int(count)
                    })
        
        # Extract prerequisites
        prereq_match = re.search(r'"pre"\s*=\s*(\d+)', quest_data)
        if prereq_match:
            quest['prerequisite'] = int(prereq_match.group(1))
        
        # Extract next quest
        next_match = re.search(r'"next"\s*=\s*(\d+)', quest_data)
        if next_match:
            quest['next_quest'] = int(next_match.group(1))
        
        quests[quest_id] = quest
    
    # Parse quest text
    texts = {}
    text_pattern = r'\[(\d+)\]\s*=\s*\{([^}]+(?:\[[^\]]*\][^}]*)*)\}'
    
    for match in re.finditer(text_pattern, text_content):
        quest_id = int(match.group(1))
        text_data = match.group(2)
        
        texts[quest_id] = {}
        
        # Extract title
        title_match = re.search(r'\["T"\]\s*=\s*"([^"]+)"', text_data)
        if title_match:
            texts[quest_id]['title'] = title_match.group(1)
        
        # Extract objectives text
        obj_match = re.search(r'\["O"\]\s*=\s*"([^"]+)"', text_data)
        if obj_match:
            texts[quest_id]['objectives'] = obj_match.group(1)
    
    return quests, texts

def convert_to_questie_format(quests, texts):
    """Convert to Questie database format with proper objective data"""
    
    output = []
    output.append("-- Enhanced pfQuest conversion with objective data")
    output.append(f"-- Generated on {datetime.now()}")
    output.append("-- This includes mob/item/object IDs for proper map markers")
    output.append("")
    output.append("pfQuestEnhancedData = {")
    
    converted_count = 0
    quests_with_objectives = 0
    
    for quest_id in sorted(quests.keys()):
        quest = quests[quest_id]
        text = texts.get(quest_id, {})
        
        # Skip quests without titles
        if not text.get('title'):
            continue
        
        title = text['title'].replace('"', '\\"')
        level = quest['level'] or 1
        
        # Convert faction
        if quest['race']:
            # Alliance races have lower bits, Horde has higher
            if quest['race'] in [1, 3, 4, 5, 7, 8, 64, 65, 68, 69, 71, 72, 73, 76, 77]:
                faction = 2  # Alliance
            elif quest['race'] in [2, 10, 16, 18, 32, 128, 130, 138, 146, 154, 162, 170, 178]:
                faction = 1  # Horde
            else:
                faction = 3  # Both
        else:
            faction = 3  # Both
        
        # Build the quest entry
        line = f'  [{quest_id}] = {{"{title}",'
        
        # Start NPCs
        if quest['start_npcs']:
            line += '{{' + ','.join(map(str, quest['start_npcs'])) + '}},'
        else:
            line += 'nil,'
        
        # End NPCs
        if quest['end_npcs']:
            line += '{{' + ','.join(map(str, quest['end_npcs'])) + '}},'
        else:
            line += 'nil,'
        
        # Required level, quest level, required races, required classes
        line += f'nil,{level},nil,nil,'
        
        # Objectives text (field 8)
        if text.get('objectives'):
            objectives = text['objectives'].replace('"', '\\"').replace('$B', ' ').replace('$N', 'Hero')
            line += f'{{"{objectives}"}},nil,'
        else:
            line += 'nil,nil,'
        
        # OBJECTIVES DATA (field 10) - THE CRITICAL PART
        if quest['objectives']:
            obj_parts = []
            
            # Mobs to kill
            if 'mobs' in quest['objectives']:
                mob_list = []
                for mob in quest['objectives']['mobs']:
                    # Format: {mobId, count, "name"} - we don't have names yet
                    mob_list.append(f'{{{mob["id"]},{mob["count"]}}}')
                if mob_list:
                    obj_parts.append('{{' + ','.join(mob_list) + '}}')
                else:
                    obj_parts.append('nil')
            else:
                obj_parts.append('nil')
            
            # Objects to interact with
            if 'objects' in quest['objectives']:
                obj_list = []
                for obj in quest['objectives']['objects']:
                    obj_list.append(f'{{{obj["id"]},{obj["count"]}}}')
                if obj_list:
                    obj_parts.append('{{' + ','.join(obj_list) + '}}')
                else:
                    obj_parts.append('nil')
            else:
                obj_parts.append('nil')
            
            # Items to collect
            if 'items' in quest['objectives']:
                item_list = []
                for item in quest['objectives']['items']:
                    item_list.append(f'{{{item["id"]},{item["count"]}}}')
                if item_list:
                    obj_parts.append('{{' + ','.join(item_list) + '}}')
                else:
                    obj_parts.append('nil')
            else:
                obj_parts.append('nil')
            
            line += '{{' + ','.join(obj_parts) + '}},'
            quests_with_objectives += 1
        else:
            line += 'nil,'
        
        # Source item, preQuestGroup, preQuestSingle
        line += 'nil,nil,'
        if quest['prerequisite']:
            line += f'{{{quest["prerequisite"]}}},'
        else:
            line += 'nil,'
        
        # childQuests, inGroupWith, exclusiveTo, zoneOrSort
        line += 'nil,nil,nil,nil,'
        
        # requiredSkill, requiredMinRep, requiredMaxRep, requiredSourceItems
        line += 'nil,nil,nil,nil,'
        
        # nextQuestInChain
        if quest['next_quest']:
            line += f'{quest["next_quest"]},'
        else:
            line += 'nil,'
        
        # questFlags (use 2 for normal quest)
        line += '2,'
        
        # specialFlags (use 0)
        line += '0,'
        
        # parentQuest
        if quest['prerequisite']:
            line += f'{quest["prerequisite"]},'
        else:
            line += 'nil,'
        
        # Fill remaining fields with nil
        line += 'nil,nil,nil,nil}, -- pfQuest enhanced'
        
        output.append(line)
        converted_count += 1
    
    output.append('}')
    output.append('')
    output.append(f'-- Total converted: {converted_count} quests')
    output.append(f'-- Quests with objective data: {quests_with_objectives}')
    
    return '\n'.join(output)

def main():
    """Main conversion function"""
    
    print("Enhanced pfQuest to Questie Converter")
    print("=" * 50)
    
    # You'll need to provide the actual pfQuest database files
    data_file = input("Enter path to pfQuest quest data file (e.g., quests.lua): ").strip()
    text_file = input("Enter path to pfQuest quest text file (e.g., quests-enUS.lua): ").strip()
    
    print("\nParsing pfQuest database...")
    quests, texts = parse_pfquest_database(data_file, text_file)
    
    print(f"Found {len(quests)} quests in pfQuest database")
    
    # Count quests with objectives
    with_objectives = sum(1 for q in quests.values() if q['objectives'])
    print(f"Quests with objective data: {with_objectives}")
    
    print("\nConverting to Questie format...")
    output = convert_to_questie_format(quests, texts)
    
    # Save output
    output_file = "pfquest_enhanced_conversion.lua"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"\nConversion complete! Saved to {output_file}")
    
    # Show sample of quests with objectives
    print("\nSample quests with objective data:")
    sample_count = 0
    for quest_id, quest in sorted(quests.items())[:100]:
        if quest['objectives']:
            text = texts.get(quest_id, {})
            print(f"  Quest {quest_id}: {text.get('title', 'Unknown')}")
            if 'mobs' in quest['objectives']:
                print(f"    Mobs: {quest['objectives']['mobs']}")
            if 'items' in quest['objectives']:
                print(f"    Items: {quest['objectives']['items']}")
            if 'objects' in quest['objectives']:
                print(f"    Objects: {quest['objectives']['objects']}")
            sample_count += 1
            if sample_count >= 5:
                break

if __name__ == "__main__":
    main()