#!/usr/bin/env python3

"""
CORRECT pfQuest to Questie Converter v2
This generates properly formatted Questie quest data without nesting issues
"""

import re
import json
from datetime import datetime

class QuestieQuestStructure:
    """
    Defines the exact Questie quest structure with 30 fields
    """
    @staticmethod
    def create_empty_quest():
        """Create an empty quest with all 30 fields as nil"""
        return [None] * 30
    
    @staticmethod
    def format_quest(quest_data):
        """
        Format quest data into proper Lua syntax
        quest_data should be a list of 30 elements
        """
        formatted = []
        
        for i, field in enumerate(quest_data):
            if field is None:
                formatted.append('nil')
            elif isinstance(field, str):
                # Escape quotes and format string
                escaped = field.replace('\\', '\\\\').replace('"', '\\"')
                formatted.append(f'"{escaped}"')
            elif isinstance(field, int):
                formatted.append(str(field))
            elif isinstance(field, list):
                if len(field) == 0:
                    formatted.append('nil')
                else:
                    # Format list/table
                    formatted.append(QuestieQuestStructure._format_table(field))
            elif isinstance(field, dict):
                # Format objectives (special handling)
                formatted.append(QuestieQuestStructure._format_objectives(field))
            else:
                formatted.append('nil')
        
        return '{' + ','.join(formatted) + '}'
    
    @staticmethod
    def _format_table(table):
        """Format a Lua table from a Python list"""
        if all(isinstance(x, int) for x in table):
            # Simple number array
            return '{' + ','.join(str(x) for x in table) + '}'
        elif all(isinstance(x, str) for x in table):
            # String array
            return '{' + ','.join(f'"{s}"' for s in table) + '}'
        else:
            # Complex table
            formatted_items = []
            for item in table:
                if isinstance(item, list):
                    formatted_items.append(QuestieQuestStructure._format_table(item))
                elif isinstance(item, int):
                    formatted_items.append(str(item))
                elif isinstance(item, str):
                    formatted_items.append(f'"{item}"')
                else:
                    formatted_items.append('nil')
            return '{' + ','.join(formatted_items) + '}'
    
    @staticmethod
    def _format_objectives(objectives):
        """
        Format objectives dict into proper Questie structure
        Objectives = {creatures, objects, items, reputation, killCredit, spells}
        """
        result = []
        
        # Creatures (position 1)
        if 'creatures' in objectives and objectives['creatures']:
            creatures = []
            for creature in objectives['creatures']:
                if isinstance(creature, dict):
                    # Format: {id, count, "name"}
                    parts = [str(creature.get('id', 0)), str(creature.get('count', 1))]
                    if 'name' in creature:
                        parts.append(f'"{creature["name"]}"')
                    creatures.append('{' + ','.join(parts) + '}')
            result.append('{' + ','.join(creatures) + '}')
        else:
            result.append('nil')
        
        # Objects (position 2)
        if 'objects' in objectives and objectives['objects']:
            objects = []
            for obj in objectives['objects']:
                if isinstance(obj, dict):
                    parts = [str(obj.get('id', 0)), str(obj.get('count', 1))]
                    if 'name' in obj:
                        parts.append(f'"{obj["name"]}"')
                    objects.append('{' + ','.join(parts) + '}')
            result.append('{' + ','.join(objects) + '}')
        else:
            result.append('nil')
        
        # Items (position 3)
        if 'items' in objectives and objectives['items']:
            items = []
            for item in objectives['items']:
                if isinstance(item, dict):
                    parts = [str(item.get('id', 0)), str(item.get('count', 1))]
                    if 'name' in item:
                        parts.append(f'"{item["name"]}"')
                    items.append('{' + ','.join(parts) + '}')
            result.append('{' + ','.join(items) + '}')
        else:
            result.append('nil')
        
        # Reputation (position 4)
        result.append('nil')
        
        # Kill credit (position 5)
        result.append('nil')
        
        # Spells (position 6)
        if 'spells' in objectives and objectives['spells']:
            spells = []
            for spell in objectives['spells']:
                if isinstance(spell, dict):
                    parts = [str(spell.get('id', 0))]
                    if 'name' in spell:
                        parts.append(f'"{spell["name"]}"')
                    spells.append('{' + ','.join(parts) + '}')
            result.append('{' + ','.join(spells) + '}')
        else:
            result.append('nil')
        
        return '{' + ','.join(result) + '}'


class PfQuestParser:
    """Parse pfQuest data files"""
    
    @staticmethod
    def parse_objectives(obj_content):
        """
        Parse pfQuest objectives into structured format
        Returns dict with creatures, objects, items keys
        """
        objectives = {}
        
        # Extract mob kills (U = Unit/NPC)
        mob_matches = re.findall(r'\["U"\]\s*=\s*\{([^}]*)\}', obj_content)
        for mob_match in mob_matches:
            # Parse mob ID and count
            mob_data = re.findall(r'(\d+)\s*,\s*(\d+)', mob_match)
            for mob_id, count in mob_data:
                if 'creatures' not in objectives:
                    objectives['creatures'] = []
                objectives['creatures'].append({
                    'id': int(mob_id),
                    'count': int(count)
                })
        
        # Extract items (I = Item)
        item_matches = re.findall(r'\["I"\]\s*=\s*\{([^}]*)\}', obj_content)
        for item_match in item_matches:
            # Parse item ID and count
            item_data = re.findall(r'(\d+)\s*,\s*(\d+)', item_match)
            for item_id, count in item_data:
                if 'items' not in objectives:
                    objectives['items'] = []
                objectives['items'].append({
                    'id': int(item_id),
                    'count': int(count)
                })
        
        # Extract objects (O = Object)
        obj_matches = re.findall(r'\["O"\]\s*=\s*\{([^}]*)\}', obj_content)
        for obj_match in obj_matches:
            # Parse object ID and count
            obj_data = re.findall(r'(\d+)\s*,\s*(\d+)', obj_match)
            for obj_id, count in obj_data:
                if 'objects' not in objectives:
                    objectives['objects'] = []
                objectives['objects'].append({
                    'id': int(obj_id),
                    'count': int(count)
                })
        
        return objectives


def convert_pfquest_to_questie(pfquest_data_file, pfquest_text_file, output_file):
    """
    Main conversion function
    """
    print("=" * 70)
    print("PFQUEST TO QUESTIE CONVERTER V2")
    print("=" * 70)
    
    # Read pfQuest files
    print(f"Reading {pfquest_data_file}...")
    with open(pfquest_data_file, 'r', encoding='utf-8') as f:
        data_content = f.read()
    
    print(f"Reading {pfquest_text_file}...")
    with open(pfquest_text_file, 'r', encoding='utf-8') as f:
        text_content = f.read()
    
    # Parse quests
    quests = {}
    quest_pattern = r'\[(\d+)\]\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    
    print("Parsing quest data...")
    for match in re.finditer(quest_pattern, data_content):
        quest_id = int(match.group(1))
        quest_data = match.group(2)
        
        quest = QuestieQuestStructure.create_empty_quest()
        
        # Field 1: Name (will be filled from text file)
        
        # Field 2: Started by (NPCs, Objects, Items)
        start_match = re.search(r'"start"\s*=\s*\{([^}]*)\}', quest_data)
        if start_match:
            start_content = start_match.group(1)
            npcs = re.findall(r'\["U"\]\s*=\s*(\d+)', start_content)
            if npcs:
                quest[1] = [[int(npc) for npc in npcs], None, None]
        
        # Field 3: Finished by (NPCs, Objects)
        end_match = re.search(r'"end"\s*=\s*\{([^}]*)\}', quest_data)
        if end_match:
            end_content = end_match.group(1)
            npcs = re.findall(r'\["U"\]\s*=\s*(\d+)', end_content)
            if npcs:
                quest[2] = [[int(npc) for npc in npcs], None]
        
        # Field 5: Quest level
        level_match = re.search(r'"level"\s*=\s*(\d+)', quest_data)
        if level_match:
            quest[4] = int(level_match.group(1))
        
        # Field 10: Objectives
        obj_match = re.search(r'"obj"\s*=\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', quest_data)
        if obj_match:
            objectives = PfQuestParser.parse_objectives(obj_match.group(1))
            if objectives:
                quest[9] = objectives
        
        # Field 17: Zone (for now, leave as nil)
        # Field 23: Quest flags (default to 2 for normal quest)
        quest[22] = 2
        
        # Field 24: Special flags (default to 0)
        quest[23] = 0
        
        quests[quest_id] = quest
    
    # Parse quest text
    print("Parsing quest text...")
    text_pattern = r'\[(\d+)\]\s*=\s*\{([^}]+)\}'
    texts = {}
    
    for match in re.finditer(text_pattern, text_content):
        quest_id = int(match.group(1))
        text_data = match.group(2)
        
        texts[quest_id] = {}
        
        # Extract title
        title_match = re.search(r'\["T"\]\s*=\s*"([^"]*)"', text_data)
        if title_match:
            texts[quest_id]['title'] = title_match.group(1)
        
        # Extract objectives
        obj_match = re.search(r'\["O"\]\s*=\s*"([^"]*)"', text_data)
        if obj_match:
            texts[quest_id]['objectives'] = obj_match.group(1)
    
    # Merge text into quest data
    for quest_id in quests:
        if quest_id in texts:
            # Field 1: Quest name
            if 'title' in texts[quest_id]:
                quests[quest_id][0] = texts[quest_id]['title']
            
            # Field 8: Objectives text
            if 'objectives' in texts[quest_id]:
                quests[quest_id][7] = [texts[quest_id]['objectives']]
    
    # Write output
    print(f"Writing {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- Converted from pfQuest data using correct converter v2\n")
        f.write(f"-- Generated: {datetime.now()}\n")
        f.write("-- This should have NO nesting issues\n\n")
        f.write("local questData = {\n")
        
        for quest_id in sorted(quests.keys()):
            quest = quests[quest_id]
            # Skip quests without names
            if not quest[0]:
                continue
            
            formatted = QuestieQuestStructure.format_quest(quest)
            f.write(f"  [{quest_id}] = {formatted},\n")
        
        f.write("}\n")
    
    print(f"✅ Converted {len(quests)} quests")
    print(f"📁 Output: {output_file}")
    
    return len(quests)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python correct_converter.py <pfquest_data.lua> <pfquest_text.lua> <output.lua>")
        sys.exit(1)
    
    convert_pfquest_to_questie(sys.argv[1], sys.argv[2], sys.argv[3])