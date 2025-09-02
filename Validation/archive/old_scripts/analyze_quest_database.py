#!/usr/bin/env python3
"""
Analyze and fix Questie Epoch quest database issues:
1. Identify and merge duplicate quest entries
2. Fix missing turn-in NPCs
3. Generate comprehensive report
"""

import re
import json
from collections import defaultdict, Counter
from typing import Dict, List, Tuple, Optional

class QuestAnalyzer:
    def __init__(self, quest_db_path: str, npc_db_path: str):
        self.quest_db_path = quest_db_path
        self.npc_db_path = npc_db_path
        self.quests = {}
        self.duplicates = defaultdict(list)
        self.npcs = {}
        self.issues = []
        
    def parse_quest_line(self, line: str, line_num: int) -> Optional[Tuple[int, dict]]:
        """Parse a single quest definition line."""
        match = re.match(r'epochQuestData\[(\d+)\] = \{(.*)\}', line.strip())
        if not match:
            return None
            
        quest_id = int(match.group(1))
        data_str = match.group(2)
        
        # Parse the quest data
        quest_data = {
            'line_num': line_num,
            'raw': line.strip(),
            'name': None,
            'quest_giver': None,
            'turn_in': None,
            'level': None,
            'faction': None,  # Field 23: 1=Alliance, 2=Horde, 8=Both
            'zone': None,
            'objectives': None,
            'comment': None
        }
        
        # Extract quest name
        name_match = re.search(r'"([^"]+)"', data_str)
        if name_match:
            quest_data['name'] = name_match.group(1)
            
        # Extract comment if present
        comment_match = re.search(r'-- (.+)$', line)
        if comment_match:
            quest_data['comment'] = comment_match.group(1)
            
        # Parse the fields (simplified - focuses on key fields)
        # Format: {"Name",{{giver}},{{turnin}},nil,level,nil,nil,objectives,...,zone,...,faction,...)
        parts = data_str.split(',')
        
        # Try to extract quest giver (field 2)
        giver_match = re.search(r',\{\{(\d+)\}\}', data_str)
        if giver_match:
            quest_data['quest_giver'] = int(giver_match.group(1))
            
        # Try to extract turn-in NPC (field 3)
        # Look for pattern after quest giver
        turnin_pattern = r',\{\{(\d+)\}\},[^,]*,\{\{(\d+)\}\}'
        if re.search(turnin_pattern, data_str):
            turnin_match = re.findall(r'\{\{(\d+)\}\}', data_str)
            if len(turnin_match) >= 2:
                quest_data['turn_in'] = int(turnin_match[1])
        
        # Extract faction (field 23) - count commas to find it
        fields = re.split(r',(?![^{]*\})', data_str)
        if len(fields) > 22:
            faction_str = fields[22].strip()
            if faction_str.isdigit():
                quest_data['faction'] = int(faction_str)
                
        # Extract zone (field 17)
        if len(fields) > 16:
            zone_str = fields[16].strip()
            if zone_str.isdigit():
                quest_data['zone'] = int(zone_str)
                
        # Extract level (field 5)
        if len(fields) > 4:
            level_str = fields[4].strip()
            if level_str.isdigit():
                quest_data['level'] = int(level_str)
        
        return quest_id, quest_data
        
    def parse_npc_line(self, line: str) -> Optional[Tuple[int, dict]]:
        """Parse NPC database line to find quest associations."""
        match = re.match(r'epochNpcData\[(\d+)\] = \{.*\{([^}]*)\},\{([^}]*)\}', line)
        if not match:
            return None
            
        npc_id = int(match.group(1))
        quests_given = match.group(2)
        quests_turnin = match.group(3)
        
        npc_data = {
            'gives': [],
            'turns_in': []
        }
        
        # Parse quest IDs from gives/turns_in
        if quests_given and quests_given != 'nil':
            npc_data['gives'] = [int(x) for x in re.findall(r'\d+', quests_given)]
        if quests_turnin and quests_turnin != 'nil':
            npc_data['turns_in'] = [int(x) for x in re.findall(r'\d+', quests_turnin)]
            
        return npc_id, npc_data
        
    def load_databases(self):
        """Load quest and NPC databases."""
        print("Loading quest database...")
        with open(self.quest_db_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if 'epochQuestData[' in line:
                    result = self.parse_quest_line(line, line_num)
                    if result:
                        quest_id, quest_data = result
                        if quest_id in self.quests:
                            # Duplicate found
                            self.duplicates[quest_id].append(quest_data)
                        else:
                            self.quests[quest_id] = quest_data
                            
        # Add first occurrence to duplicates list
        for quest_id, duplicate_list in self.duplicates.items():
            duplicate_list.insert(0, self.quests[quest_id])
                            
        print(f"Found {len(self.quests)} unique quests")
        print(f"Found {len(self.duplicates)} quests with duplicates")
        
        print("\nLoading NPC database...")
        with open(self.npc_db_path, 'r', encoding='utf-8') as f:
            for line in f:
                if 'epochNpcData[' in line:
                    result = self.parse_npc_line(line)
                    if result:
                        npc_id, npc_data = result
                        self.npcs[npc_id] = npc_data
                        
        print(f"Found {len(self.npcs)} NPCs")
        
    def analyze_duplicates(self):
        """Analyze duplicate quests and determine best version."""
        print("\n=== DUPLICATE QUEST ANALYSIS ===\n")
        
        merge_recommendations = []
        
        for quest_id, versions in self.duplicates.items():
            print(f"\nQuest {quest_id}: {versions[0]['name']}")
            print(f"  Found {len(versions)} versions:")
            
            # Analyze each version
            best_version = None
            best_score = -1
            faction_flags = set()
            
            for i, ver in enumerate(versions):
                score = 0
                # Score based on completeness
                if ver['quest_giver']: score += 2
                if ver['turn_in']: score += 3  # Turn-in is more important
                if ver['objectives']: score += 1
                if ver['level']: score += 1
                if ver['zone']: score += 1
                if ver['faction']: 
                    score += 1
                    faction_flags.add(ver['faction'])
                    
                print(f"    Version {i+1} (line {ver['line_num']}): score={score}")
                print(f"      Giver: {ver['quest_giver']}, Turn-in: {ver['turn_in']}, "
                      f"Faction: {ver['faction']}, Zone: {ver['zone']}")
                if ver['comment']:
                    print(f"      Comment: {ver['comment']}")
                    
                if score > best_score:
                    best_score = score
                    best_version = i
                    
            # Check if versions are for different factions
            if len(faction_flags) > 1 and (1 in faction_flags and 2 in faction_flags):
                print(f"  ⚠️  FACTION CONFLICT: Quest exists for both Alliance(1) and Horde(2)")
                print(f"      Should be marked as faction=8 (both)")
                self.issues.append({
                    'type': 'faction_conflict',
                    'quest_id': quest_id,
                    'factions': list(faction_flags)
                })
                
            print(f"  ✓ Recommend keeping version {best_version + 1}")
            merge_recommendations.append((quest_id, best_version))
            
        return merge_recommendations
        
    def analyze_missing_turnins(self):
        """Find quests with missing turn-in NPCs that should have them."""
        print("\n=== MISSING TURN-IN NPC ANALYSIS ===\n")
        
        fixes_needed = []
        
        for quest_id, quest_data in self.quests.items():
            if quest_data['quest_giver'] and not quest_data['turn_in']:
                # Check if the quest giver also turns it in
                giver_id = quest_data['quest_giver']
                if giver_id in self.npcs:
                    npc_data = self.npcs[giver_id]
                    if quest_id in npc_data['turns_in']:
                        print(f"Quest {quest_id} ({quest_data['name']})")
                        print(f"  Missing turn-in but NPC {giver_id} shows it turns in this quest")
                        fixes_needed.append((quest_id, giver_id))
                        
                # Check for phased NPCs (±1 ID)
                for offset in [-1, 1]:
                    phased_id = giver_id + offset
                    if phased_id in self.npcs:
                        npc_data = self.npcs[phased_id]
                        if quest_id in npc_data['turns_in']:
                            print(f"Quest {quest_id} ({quest_data['name']})")
                            print(f"  Phased NPC {phased_id} (original: {giver_id}) turns in this quest")
                            fixes_needed.append((quest_id, phased_id))
                            break
                            
        print(f"\nFound {len(fixes_needed)} quests that need turn-in NPCs added")
        return fixes_needed
        
    def generate_report(self):
        """Generate comprehensive issue report."""
        print("\n=== COMPREHENSIVE ISSUE REPORT ===\n")
        
        report = []
        report.append("# Questie Epoch Database Issue Report\n")
        report.append(f"Total Quests: {len(self.quests)}\n")
        report.append(f"Duplicate Quests: {len(self.duplicates)}\n")
        
        # Missing turn-ins
        missing_turnins = sum(1 for q in self.quests.values() 
                             if q['quest_giver'] and not q['turn_in'])
        report.append(f"Quests with missing turn-in NPCs: {missing_turnins}\n")
        
        # Faction analysis
        faction_counts = Counter(q['faction'] for q in self.quests.values() if q['faction'])
        report.append("\n## Faction Distribution:\n")
        report.append(f"- Alliance only (1): {faction_counts.get(1, 0)}\n")
        report.append(f"- Horde only (2): {faction_counts.get(2, 0)}\n")
        report.append(f"- Both factions (8): {faction_counts.get(8, 0)}\n")
        
        # Zone distribution
        zone_counts = Counter(q['zone'] for q in self.quests.values() if q['zone'])
        report.append("\n## Top 10 Zones by Quest Count:\n")
        for zone, count in zone_counts.most_common(10):
            report.append(f"- Zone {zone}: {count} quests\n")
            
        # Detailed duplicate list
        report.append("\n## Duplicate Quest Details:\n")
        for quest_id in sorted(self.duplicates.keys()):
            versions = self.duplicates[quest_id]
            report.append(f"\n### Quest {quest_id}: {versions[0]['name']}\n")
            for i, ver in enumerate(versions):
                report.append(f"- Version {i+1} (line {ver['line_num']}): ")
                report.append(f"Faction={ver['faction']}, Zone={ver['zone']}\n")
                
        return ''.join(report)
        
    def generate_fixes(self, merge_recs, turnin_fixes):
        """Generate SQL-style fixes for the issues."""
        print("\n=== GENERATING FIXES ===\n")
        
        fixes = []
        
        # Generate duplicate removal commands
        fixes.append("-- Remove duplicate quest entries (keeping best version)\n")
        for quest_id, best_version in merge_recs:
            versions = self.duplicates[quest_id]
            for i, ver in enumerate(versions):
                if i != best_version:
                    fixes.append(f"-- Remove line {ver['line_num']}: Quest {quest_id}\n")
                    
        # Generate turn-in NPC additions
        fixes.append("\n-- Add missing turn-in NPCs\n")
        for quest_id, npc_id in turnin_fixes:
            fixes.append(f"-- Quest {quest_id}: Add turn-in NPC {npc_id}\n")
            
        return ''.join(fixes)

def main():
    analyzer = QuestAnalyzer(
        'Database/Epoch/epochQuestDB.lua',
        'Database/Epoch/epochNpcDB.lua'
    )
    
    analyzer.load_databases()
    merge_recs = analyzer.analyze_duplicates()
    turnin_fixes = analyzer.analyze_missing_turnins()
    
    # Generate report
    report = analyzer.generate_report()
    with open('quest_database_report.md', 'w') as f:
        f.write(report)
    print("\nReport saved to quest_database_report.md")
    
    # Generate fixes
    fixes = analyzer.generate_fixes(merge_recs, turnin_fixes)
    with open('quest_database_fixes.txt', 'w') as f:
        f.write(fixes)
    print("Fixes saved to quest_database_fixes.txt")

if __name__ == "__main__":
    main()