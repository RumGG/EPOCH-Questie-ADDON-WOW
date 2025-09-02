#!/usr/bin/env python3
"""
Quest Data Parser for Project Epoch Questie Database
Parses batch quest submission data and outputs Lua database entries
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# Zone name to ID mapping for WoW 3.3.5a
ZONE_MAP = {
    'The Hinterlands': 85,
    'Feralas': 69,
    'Stranglethorn Vale': 689,
    'Dustwallow Marsh': 141,
    'Alterac Mountains': 91,
    'Unknown': None
}

@dataclass
class QuestNPC:
    name: str
    npc_id: int
    coordinates: Tuple[float, float]
    zone: str
    zone_id: Optional[int] = None
    
    def __post_init__(self):
        self.zone_id = ZONE_MAP.get(self.zone)

@dataclass
class QuestObjective:
    description: str
    obj_type: str = "item"  # item, kill, etc
    item_id: Optional[int] = None
    count: int = 1

@dataclass
class QuestItem:
    name: str
    item_id: int
    source_npc_id: Optional[int] = None
    source_npc_name: Optional[str] = None

@dataclass
class QuestData:
    quest_id: int
    name: str
    level: int
    zone: str
    faction: str
    quest_giver: Optional[QuestNPC] = None
    turn_in_npc: Optional[QuestNPC] = None
    objectives: List[QuestObjective] = field(default_factory=list)
    quest_items: List[QuestItem] = field(default_factory=list)
    is_incomplete: bool = False
    zone_id: Optional[int] = None
    
    def __post_init__(self):
        self.zone_id = ZONE_MAP.get(self.zone)

class QuestDataParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.quests: List[QuestData] = []
        
    def parse_file(self) -> List[QuestData]:
        """Parse the entire quest data file"""
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split content into quest sections
        quest_sections = re.split(r'-{40,}', content)
        
        for section in quest_sections:
            if '=== QUEST DATA ===' in section and 'Quest ID:' in section:
                quest = self._parse_quest_section(section)
                if quest:
                    self.quests.append(quest)
        
        return self.quests
    
    def _parse_quest_section(self, section: str) -> Optional[QuestData]:
        """Parse a single quest data section"""
        lines = section.strip().split('\n')
        
        # Extract basic quest info
        quest_id = self._extract_quest_id(section)
        if not quest_id:
            return None
            
        quest_name = self._extract_quest_name(section)
        level = self._extract_level(section)
        zone = self._extract_zone(section)
        faction = self._extract_faction(section)
        
        # Check if incomplete
        is_incomplete = any(warning in section for warning in [
            'WARNING: INCOMPLETE DATA',
            'NOTE: QUEST NOT YET COMPLETED',
            'was already in the quest log'
        ])
        
        # Create quest data object
        quest = QuestData(
            quest_id=quest_id,
            name=quest_name,
            level=level,
            zone=zone,
            faction=faction,
            is_incomplete=is_incomplete
        )
        
        # Parse quest giver
        quest.quest_giver = self._extract_quest_giver(section)
        
        # Parse turn-in NPC
        quest.turn_in_npc = self._extract_turn_in_npc(section)
        
        # Parse objectives
        quest.objectives = self._extract_objectives(section)
        
        # Parse quest items
        quest.quest_items = self._extract_quest_items(section)
        
        return quest
    
    def _extract_quest_id(self, section: str) -> Optional[int]:
        """Extract quest ID from section"""
        match = re.search(r'Quest ID:\s*(\d+)', section)
        return int(match.group(1)) if match else None
    
    def _extract_quest_name(self, section: str) -> str:
        """Extract quest name from section"""
        match = re.search(r'Quest Name:\s*(.+)', section)
        return match.group(1).strip() if match else "Unknown Quest"
    
    def _extract_level(self, section: str) -> int:
        """Extract quest level from section"""
        match = re.search(r'Level:\s*(\d+)', section)
        return int(match.group(1)) if match else 1
    
    def _extract_zone(self, section: str) -> str:
        """Extract zone from section"""
        match = re.search(r'Zone:\s*(.+)', section)
        return match.group(1).strip() if match else "Unknown"
    
    def _extract_faction(self, section: str) -> str:
        """Extract faction from section"""
        match = re.search(r'Faction:\s*(.+)', section)
        return match.group(1).strip() if match else "Both"
    
    def _extract_quest_giver(self, section: str) -> Optional[QuestNPC]:
        """Extract quest giver NPC info"""
        quest_giver_match = re.search(
            r'QUEST GIVER:\s*\n\s*NPC:\s*(.+?)\s*\(ID:\s*(\d+)\)\s*\n\s*Location:\s*\[([^,]+),\s*([^\]]+)\]\s*\n\s*Zone:\s*(.+?)(?:\n|$)',
            section, re.MULTILINE
        )
        
        if quest_giver_match:
            name = quest_giver_match.group(1).strip()
            npc_id = int(quest_giver_match.group(2))
            x_coord = float(quest_giver_match.group(3))
            y_coord = float(quest_giver_match.group(4))
            zone = quest_giver_match.group(5).strip()
            
            return QuestNPC(
                name=name,
                npc_id=npc_id,
                coordinates=(x_coord, y_coord),
                zone=zone
            )
        
        return None
    
    def _extract_turn_in_npc(self, section: str) -> Optional[QuestNPC]:
        """Extract turn-in NPC info"""
        turn_in_match = re.search(
            r'TURN-IN NPC:\s*\n\s*NPC:\s*(.+?)\s*\(ID:\s*(\d+)\)\s*\n\s*Location:\s*\[([^,]+),\s*([^\]]+)\]\s*\n\s*Zone:\s*(.+?)(?:\n|$)',
            section, re.MULTILINE
        )
        
        if turn_in_match:
            name = turn_in_match.group(1).strip()
            npc_id = int(turn_in_match.group(2))
            x_coord = float(turn_in_match.group(3))
            y_coord = float(turn_in_match.group(4))
            zone = turn_in_match.group(5).strip()
            
            return QuestNPC(
                name=name,
                npc_id=npc_id,
                coordinates=(x_coord, y_coord),
                zone=zone
            )
        
        return None
    
    def _extract_objectives(self, section: str) -> List[QuestObjective]:
        """Extract quest objectives"""
        objectives = []
        
        # Look for objectives section
        obj_match = re.search(r'OBJECTIVES:(.*?)(?=QUEST ITEMS:|GROUND OBJECTS|TURN-IN NPC:|DATABASE ENTRIES:|$)', section, re.DOTALL)
        if not obj_match:
            return objectives
        
        obj_section = obj_match.group(1)
        
        # Parse individual objectives
        obj_lines = re.findall(r'\d+\.\s*([^:]+):\s*\d+/(\d+)\s*\(([^)]+)\)', obj_section)
        
        for obj_match in obj_lines:
            description = obj_match[0].strip()
            count = int(obj_match[1])
            obj_type = obj_match[2].strip()
            
            objectives.append(QuestObjective(
                description=description,
                count=count,
                obj_type=obj_type
            ))
        
        return objectives
    
    def _extract_quest_items(self, section: str) -> List[QuestItem]:
        """Extract quest items"""
        items = []
        
        # Look for quest items section
        items_match = re.search(r'QUEST ITEMS:(.*?)(?=GROUND OBJECTS|TURN-IN NPC:|DATABASE ENTRIES:|$)', section, re.DOTALL)
        if not items_match:
            return items
        
        items_section = items_match.group(1)
        
        # Parse individual items
        item_matches = re.findall(r'(.+?)\s*\(ID:\s*(\d+)\)', items_section)
        
        for item_match in item_matches:
            name = item_match[0].strip()
            item_id = int(item_match[1])
            
            # Look for source NPC info
            source_match = re.search(rf'{re.escape(name)}.*?Drops from:\s*(.+?)\s*\(ID:\s*(\d+)\)', section, re.DOTALL)
            source_npc_name = source_match.group(1).strip() if source_match else None
            source_npc_id = int(source_match.group(2)) if source_match else None
            
            items.append(QuestItem(
                name=name,
                item_id=item_id,
                source_npc_name=source_npc_name,
                source_npc_id=source_npc_id
            ))
        
        return items

class QuestDatabaseGenerator:
    def __init__(self, quests: List[QuestData]):
        self.quests = quests
    
    def generate_quest_db_entries(self) -> str:
        """Generate Lua entries for epochQuestDB.lua"""
        entries = []
        entries.append("-- Generated Quest Entries for epochQuestDB.lua")
        entries.append("-- Add these to the local epochQuestDB table")
        entries.append("")
        
        for quest in self.quests:
            # Skip incomplete quests without essential data
            if quest.is_incomplete and not quest.quest_giver:
                entries.append(f"-- SKIPPED (incomplete): [{quest.quest_id}] = {{\"{quest.name}\", incomplete quest data}},")
                continue
            
            # Build quest entry
            quest_giver_ids = quest.quest_giver.npc_id if quest.quest_giver else "nil"
            turn_in_ids = quest.turn_in_npc.npc_id if quest.turn_in_npc else quest_giver_ids
            zone_id = quest.zone_id if quest.zone_id else 85  # Default to Hinterlands
            
            # Build the Lua entry string manually to avoid f-string complexity
            quest_giver_table = f"{{{quest_giver_ids}}}" if quest_giver_ids != "nil" else "nil"
            turn_in_table = f"{{{turn_in_ids}}}" if turn_in_ids != "nil" else quest_giver_table
            
            lua_entry = f"[{quest.quest_id}] = {{\"{quest.name}\",{quest_giver_table},{turn_in_table},nil,{quest.level},nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,{zone_id},nil,nil,nil,nil,nil,nil,0,nil,nil,nil,nil,nil,nil}};"
            entries.append(lua_entry)
        
        return "\n".join(entries)
    
    def generate_npc_db_entries(self) -> str:
        """Generate Lua entries for epochNpcDB.lua"""
        entries = []
        entries.append("-- Generated NPC Entries for epochNpcDB.lua")
        entries.append("-- Add these to the local epochNpcDB table")
        entries.append("")
        
        # Collect unique NPCs
        npcs = {}
        
        for quest in self.quests:
            if quest.quest_giver:
                npc = quest.quest_giver
                if npc.npc_id not in npcs:
                    npcs[npc.npc_id] = {
                        'npc': npc,
                        'quests': [quest.quest_id]
                    }
                else:
                    npcs[npc.npc_id]['quests'].append(quest.quest_id)
            
            if quest.turn_in_npc and quest.turn_in_npc.npc_id not in npcs:
                npc = quest.turn_in_npc
                npcs[npc.npc_id] = {
                    'npc': npc,
                    'quests': [quest.quest_id]
                }
        
        # Generate NPC entries
        for npc_id, npc_data in sorted(npcs.items()):
            npc = npc_data['npc']
            quest_list = ",".join(map(str, npc_data['quests']))
            zone_id = npc.zone_id if npc.zone_id else 85
            x, y = npc.coordinates
            
            # Build NPC entry manually to avoid f-string complexity
            coordinates_table = f"{{[{zone_id}]={{{{{x},{y}}}}}}}"
            quests_table = f"{{{quest_list}}}"
            # Use a default level since NPCs don't have levels in our data
            npc_level = 60  # Default level for epoch NPCs
            
            lua_entry = f"[{npc_id}] = {{\"{npc.name}\",nil,nil,{npc_level},{npc_level},0,{coordinates_table},nil,{zone_id},{quests_table},nil,nil,nil,nil,0}};"
            entries.append(lua_entry)
        
        return "\n".join(entries)
    
    def generate_summary(self) -> str:
        """Generate summary of parsed data"""
        complete_quests = [q for q in self.quests if not q.is_incomplete and q.quest_giver]
        incomplete_quests = [q for q in self.quests if q.is_incomplete or not q.quest_giver]
        
        summary = []
        summary.append("=== QUEST DATA PARSING SUMMARY ===")
        summary.append(f"Total quests parsed: {len(self.quests)}")
        summary.append(f"Complete quests (with quest giver): {len(complete_quests)}")
        summary.append(f"Incomplete quests: {len(incomplete_quests)}")
        summary.append("")
        
        if complete_quests:
            summary.append("COMPLETE QUESTS:")
            for quest in complete_quests:
                summary.append(f"  {quest.quest_id}: {quest.name} (Level {quest.level}, {quest.zone})")
        
        if incomplete_quests:
            summary.append("")
            summary.append("INCOMPLETE QUESTS (need more data):")
            for quest in incomplete_quests:
                reason = "Missing quest giver" if not quest.quest_giver else "Marked as incomplete"
                summary.append(f"  {quest.quest_id}: {quest.name} ({reason})")
        
        return "\n".join(summary)

def main():
    """Main function to parse quest data and generate database entries"""
    input_file = "/Users/travisheryford/Downloads/BATCH.QUEST.DATA.SUBMISSION.txt"
    
    try:
        # Parse quest data
        parser = QuestDataParser(input_file)
        quests = parser.parse_file()
        
        if not quests:
            print("No quest data found in the input file.")
            return
        
        # Generate database entries
        generator = QuestDatabaseGenerator(quests)
        
        # Generate summary
        summary = generator.generate_summary()
        print(summary)
        print("\n" + "="*60 + "\n")
        
        # Generate quest database entries
        quest_db_entries = generator.generate_quest_db_entries()
        print("QUEST DATABASE ENTRIES:")
        print(quest_db_entries)
        print("\n" + "="*60 + "\n")
        
        # Generate NPC database entries
        npc_db_entries = generator.generate_npc_db_entries()
        print("NPC DATABASE ENTRIES:")
        print(npc_db_entries)
        
        # Save to output files
        output_dir = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/Questie/"
        
        with open(output_dir + "parsed_quest_entries.lua", 'w') as f:
            f.write(quest_db_entries)
        
        with open(output_dir + "parsed_npc_entries.lua", 'w') as f:
            f.write(npc_db_entries)
        
        with open(output_dir + "parsing_summary.txt", 'w') as f:
            f.write(summary)
        
        print(f"\nOutput files generated:")
        print(f"  - parsed_quest_entries.lua")
        print(f"  - parsed_npc_entries.lua") 
        print(f"  - parsing_summary.txt")
        
    except Exception as e:
        print(f"Error processing quest data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()