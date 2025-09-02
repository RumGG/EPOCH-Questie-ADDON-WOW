#!/usr/bin/env python3

"""
Extract objective data from pfQuest-epoch database
Converts mob/item/object IDs to Questie format
"""

import re
from datetime import datetime
import json

def parse_lua_table(content, start_pos=0):
    """Parse a Lua table into Python dict/list"""
    content = content.strip()
    if not content.startswith('{'):
        return None, start_pos
    
    result = {}
    pos = 1  # Skip opening brace
    
    while pos < len(content):
        # Skip whitespace and comments
        while pos < len(content) and content[pos] in ' \t\n,':
            pos += 1
        
        if pos >= len(content):
            break
            
        if content[pos] == '}':
            return result, pos + 1
        
        # Parse key
        if content[pos] == '[':
            # Bracketed key
            end = content.find(']', pos)
            if end == -1:
                break
            key = content[pos+1:end].strip('"\'')
            pos = end + 1
        else:
            # Unbracketed key (shouldn't happen in our data)
            break
        
        # Skip = sign
        eq_pos = content.find('=', pos)
        if eq_pos == -1:
            break
        pos = eq_pos + 1
        
        # Skip whitespace
        while pos < len(content) and content[pos] in ' \t\n':
            pos += 1
        
        # Parse value
        if content[pos] == '{':
            # Nested table
            value, new_pos = parse_lua_table(content[pos:])
            if value is not None:
                result[key] = value
                pos += new_pos
        elif content[pos] == '"':
            # String value
            end = content.find('"', pos + 1)
            if end != -1:
                result[key] = content[pos+1:end]
                pos = end + 1
        else:
            # Number or simple value
            match = re.match(r'([^,}\s]+)', content[pos:])
            if match:
                value = match.group(1)
                try:
                    result[key] = int(value)
                except:
                    result[key] = value
                pos += len(value)
    
    return result, pos

def extract_quest_objectives(quest_data):
    """Extract objective IDs from quest data"""
    objectives = {
        'mobs': [],
        'items': [],
        'objects': [],
        'areas': []
    }
    
    if 'obj' not in quest_data:
        return objectives
    
    obj = quest_data['obj']
    
    # Extract mob IDs (U = Units)
    if 'U' in obj:
        if isinstance(obj['U'], dict):
            # Dictionary format: {mobId: count}
            for mob_id, count in obj['U'].items():
                if isinstance(mob_id, str) and mob_id.isdigit():
                    objectives['mobs'].append({
                        'id': int(mob_id),
                        'count': int(count) if count else 1
                    })
        elif isinstance(obj['U'], list):
            # List format
            for item in obj['U']:
                if isinstance(item, int):
                    objectives['mobs'].append({'id': item, 'count': 1})
    
    # Extract item IDs (I = Items)
    if 'I' in obj:
        if isinstance(obj['I'], dict):
            for item_id, count in obj['I'].items():
                if isinstance(item_id, str) and item_id.isdigit():
                    objectives['items'].append({
                        'id': int(item_id),
                        'count': int(count) if count else 1
                    })
        elif isinstance(obj['I'], list):
            for item in obj['I']:
                if isinstance(item, int):
                    objectives['items'].append({'id': item, 'count': 1})
    
    # Extract object IDs (O = Objects)
    if 'O' in obj:
        if isinstance(obj['O'], dict):
            for obj_id, count in obj['O'].items():
                if isinstance(obj_id, str) and obj_id.isdigit():
                    objectives['objects'].append({
                        'id': int(obj_id),
                        'count': int(count) if count else 1
                    })
        elif isinstance(obj['O'], list):
            for item in obj['O']:
                if isinstance(item, int):
                    objectives['objects'].append({'id': item, 'count': 1})
    
    return objectives

def parse_pfquest_database():
    """Parse the pfQuest database files"""
    
    # Read quest data
    quest_file = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/pfQuest-epoch/db/quests-epoch.lua"
    with open(quest_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Read quest text
    text_file = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/pfQuest-epoch/db/enUS/quests-epoch.lua"
    with open(text_file, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    quests = {}
    
    # Parse quest data using regex (simpler than full Lua parser)
    # Pattern to match quest entries
    pattern = r'\[(\d+)\]\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    
    for match in re.finditer(pattern, content):
        quest_id = int(match.group(1))
        quest_content = match.group(2)
        
        quest = {
            'id': quest_id,
            'start_npcs': [],
            'end_npcs': [],
            'objectives': {
                'mobs': [],
                'items': [],
                'objects': []
            }
        }
        
        # Extract start NPCs
        start_match = re.search(r'\["start"\]\s*=\s*\{([^}]*)\}', quest_content)
        if start_match:
            npc_match = re.search(r'\["U"\]\s*=\s*\{([^}]*)\}', start_match.group(1))
            if npc_match:
                npcs = re.findall(r'\d+', npc_match.group(1))
                quest['start_npcs'] = [int(n) for n in npcs]
        
        # Extract end NPCs
        end_match = re.search(r'\["end"\]\s*=\s*\{([^}]*)\}', quest_content)
        if end_match:
            npc_match = re.search(r'\["U"\]\s*=\s*\{([^}]*)\}', end_match.group(1))
            if npc_match:
                npcs = re.findall(r'\d+', npc_match.group(1))
                quest['end_npcs'] = [int(n) for n in npcs]
        
        # Extract objectives
        obj_match = re.search(r'\["obj"\]\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', quest_content)
        if obj_match:
            obj_content = obj_match.group(1)
            
            # Extract mob objectives (U = Units)
            mob_match = re.search(r'\["U"\]\s*=\s*\{([^}]*)\}', obj_content)
            if mob_match:
                # Parse mob IDs - they're just comma-separated IDs without counts
                mob_str = mob_match.group(1)
                mob_ids = re.findall(r'\d+', mob_str)
                for mob_id in mob_ids:
                    # Default count to 1 - we don't have exact counts in pfQuest
                    quest['objectives']['mobs'].append({'id': int(mob_id), 'count': 1})
            
            # Extract item objectives (I = Items)
            item_match = re.search(r'\["I"\]\s*=\s*\{([^}]*)\}', obj_content)
            if item_match:
                item_str = item_match.group(1)
                # Items usually don't have counts in pfQuest, just IDs
                items = re.findall(r'\d+', item_str)
                for item_id in items:
                    quest['objectives']['items'].append({'id': int(item_id), 'count': 1})
            
            # Extract object objectives (O = Objects)
            object_match = re.search(r'\["O"\]\s*=\s*\{([^}]*)\}', obj_content)
            if object_match:
                obj_str = object_match.group(1)
                objects = re.findall(r'\d+', obj_str)
                for obj_id in objects:
                    quest['objectives']['objects'].append({'id': int(obj_id), 'count': 1})
        
        # Extract level
        level_match = re.search(r'\["lvl"\]\s*=\s*(\d+)', quest_content)
        if level_match:
            quest['level'] = int(level_match.group(1))
        
        # Extract prerequisites
        pre_match = re.search(r'\["pre"\]\s*=\s*(\d+)', quest_content)
        if pre_match:
            quest['prerequisite'] = int(pre_match.group(1))
        elif pre_match := re.search(r'\["pre"\]\s*=\s*\{([^}]*)\}', quest_content):
            prereqs = re.findall(r'\d+', pre_match.group(1))
            if prereqs:
                quest['prerequisite'] = int(prereqs[0])  # Take first prereq
        
        # Extract next quest
        next_match = re.search(r'\["next"\]\s*=\s*(\d+)', quest_content)
        if next_match:
            quest['next_quest'] = int(next_match.group(1))
        
        # Extract race (faction)
        race_match = re.search(r'\["race"\]\s*=\s*(\d+)', quest_content)
        if race_match:
            quest['race'] = int(race_match.group(1))
        
        quests[quest_id] = quest
    
    # Parse quest text
    texts = {}
    text_pattern = r'\[(\d+)\]\s*=\s*\{([^}]+(?:\[[^\]]*\][^}]*)*)\}'
    
    for match in re.finditer(text_pattern, text_content):
        quest_id = int(match.group(1))
        text_data = match.group(2)
        
        texts[quest_id] = {}
        
        # Extract title
        title_match = re.search(r'\["T"\]\s*=\s*"([^"]*)"', text_data)
        if title_match:
            texts[quest_id]['title'] = title_match.group(1)
        
        # Extract objectives text
        obj_match = re.search(r'\["O"\]\s*=\s*"([^"]*)"', text_data)
        if obj_match:
            texts[quest_id]['objectives'] = obj_match.group(1)
    
    return quests, texts

def convert_to_questie_format(quests, texts):
    """Convert to Questie format with full objective data"""
    
    output = []
    output.append("-- pfQuest-epoch conversion with FULL objective data")
    output.append(f"-- Generated on {datetime.now()}")
    output.append("-- Includes mob/item/object IDs for map markers")
    output.append("")
    output.append("pfQuestObjectiveData = {")
    
    converted = 0
    with_objectives = 0
    
    for quest_id in sorted(quests.keys()):
        quest = quests[quest_id]
        text = texts.get(quest_id, {})
        
        if not text.get('title'):
            continue
        
        title = text['title'].replace('"', '\\"')
        level = quest.get('level', 1)
        
        # Convert race to faction
        race = quest.get('race', 0)
        if race in [77, 1, 3, 4, 5, 7, 8, 64, 65, 68, 69, 71, 72, 73, 76]:
            faction = '"A"'  # Alliance
        elif race in [178, 2, 10, 16, 18, 32, 128, 130, 138, 146, 154, 162, 170]:
            faction = '"H"'  # Horde
        else:
            faction = '"AH"'  # Both
        
        # Build quest entry
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
        
        # Required level, quest level, races, classes
        line += f'nil,{level},nil,nil,'
        
        # Objectives text
        if text.get('objectives'):
            obj_text = text['objectives'].replace('"', '\\"').replace('$B', ' ').replace('$N', 'Hero')
            line += f'{{"{obj_text}"}},nil,'
        else:
            line += 'nil,nil,'
        
        # OBJECTIVES DATA (field 10) - THE KEY PART!
        has_objectives = False
        if quest['objectives']['mobs'] or quest['objectives']['items'] or quest['objectives']['objects']:
            has_objectives = True
            with_objectives += 1
            
            # Mobs
            if quest['objectives']['mobs']:
                mob_list = []
                for mob in quest['objectives']['mobs']:
                    mob_list.append(f'{{{mob["id"]},{mob["count"]}}}')
                mobs_str = '{{' + ','.join(mob_list) + '}}'
            else:
                mobs_str = 'nil'
            
            # Objects
            if quest['objectives']['objects']:
                obj_list = []
                for obj in quest['objectives']['objects']:
                    obj_list.append(f'{{{obj["id"]},{obj["count"]}}}')
                objs_str = '{{' + ','.join(obj_list) + '}}'
            else:
                objs_str = 'nil'
            
            # Items
            if quest['objectives']['items']:
                item_list = []
                for item in quest['objectives']['items']:
                    item_list.append(f'{{{item["id"]},{item["count"]}}}')
                items_str = '{{' + ','.join(item_list) + '}}'
            else:
                items_str = 'nil'
            
            line += f'{{{mobs_str},{objs_str},{items_str}}},'
        else:
            line += 'nil,'
        
        # Source item, preQuestGroup, preQuestSingle
        line += 'nil,nil,'
        if quest.get('prerequisite'):
            line += f'{{{quest["prerequisite"]}}},'
        else:
            line += 'nil,'
        
        # childQuests, inGroupWith, exclusiveTo, zoneOrSort
        line += 'nil,nil,nil,nil,'
        
        # requiredSkill, requiredMinRep, requiredMaxRep, requiredSourceItems
        line += 'nil,nil,nil,nil,'
        
        # nextQuestInChain
        if quest.get('next_quest'):
            line += f'{quest["next_quest"]},'
        else:
            line += 'nil,'
        
        # questFlags (2 = normal)
        line += '2,'
        
        # specialFlags
        line += '0,'
        
        # parentQuest
        if quest.get('prerequisite'):
            line += f'{quest["prerequisite"]},'
        else:
            line += 'nil,'
        
        # Fill remaining fields
        line += 'nil,nil,nil,nil,'
        
        # friendlyToFaction (field 13 for NPCs, but we'll add it as comment)
        line += f'nil,nil}}, -- pfQuest {faction}'
        
        output.append(line)
        converted += 1
    
    output.append('}')
    output.append('')
    output.append(f'-- Converted: {converted} quests')
    output.append(f'-- With objectives: {with_objectives}')
    
    return '\n'.join(output), converted, with_objectives

def main():
    print("Extracting pfQuest-epoch objective data...")
    print("=" * 50)
    
    quests, texts = parse_pfquest_database()
    print(f"Parsed {len(quests)} quests from pfQuest")
    
    # Count quests with objectives
    with_obj = sum(1 for q in quests.values() 
                   if q['objectives']['mobs'] or 
                      q['objectives']['items'] or 
                      q['objectives']['objects'])
    print(f"Quests with objective data: {with_obj}")
    
    # Convert to Questie format
    output, converted, with_objectives = convert_to_questie_format(quests, texts)
    
    # Save output
    output_file = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/Questie/pfquest_full_objectives.lua"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"\nSaved to: pfquest_full_objectives.lua")
    print(f"Total converted: {converted}")
    print(f"With objectives: {with_objectives}")
    
    # Show some examples
    print("\nSample quests with objectives:")
    count = 0
    for qid, quest in sorted(quests.items()):
        if quest['objectives']['mobs']:
            title = texts.get(qid, {}).get('title', 'Unknown')
            print(f"  Quest {qid}: {title}")
            print(f"    Kill: {quest['objectives']['mobs']}")
            count += 1
            if count >= 3:
                break

if __name__ == "__main__":
    main()