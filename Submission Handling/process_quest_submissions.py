#!/usr/bin/env python3
"""
Automated quest data processor for Questie-Epoch GitHub submissions.
Processes quest data from GitHub issues and updates the database files.
"""

import re
import sys
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class QuestSubmissionProcessor:
    def __init__(self):
        self.quest_db_path = Path("Database/Epoch/epochQuestDB.lua")
        self.npc_db_path = Path("Database/Epoch/epochNpcDB.lua")
        self.existing_quests = {}
        self.existing_npcs = {}
        self.syntax_errors = []
        self.load_existing_data()
        
    def load_existing_data(self):
        """Load existing quest and NPC data to check for duplicates."""
        # Load quests
        if self.quest_db_path.exists():
            with open(self.quest_db_path, 'r', encoding='utf-8') as f:
                inside_table = False
                table_closed = False
                for line_num, line in enumerate(f, 1):
                    if line.strip().startswith('epochQuestData = {'):
                        inside_table = True
                        table_closed = False
                    elif line.strip() == '}' and inside_table:
                        inside_table = False
                        table_closed = True
                    
                    # Check for common syntax errors
                    if inside_table and re.match(r'^epochQuestData\[(\d+)\]', line):
                        self.syntax_errors.append(f"Quest DB Line {line_num}: Entry has 'epochQuestData' prefix inside table")
                    elif table_closed and re.match(r'^epochQuestData\[(\d+)\]', line):
                        self.syntax_errors.append(f"Quest DB Line {line_num}: Entry added OUTSIDE table (after closing brace)")
                    
                    # Check for missing commas
                    if inside_table and re.match(r'^\[\d+\] = \{.*\}', line.strip()):
                        # Check if it ends without a comma (considering comments)
                        if re.search(r'\}(\s*--.*)?$', line.strip()) and not re.search(r'\},(\s*--.*)?$', line.strip()):
                            self.syntax_errors.append(f"Quest DB Line {line_num}: Missing comma after entry (even with comment)")
                    
                    match = re.match(r'^\[?(\d+)\]', line.strip())
                    if match:
                        quest_id = int(match.group(1))
                        self.existing_quests[quest_id] = line.strip()
        
        # Load NPCs
        if self.npc_db_path.exists():
            with open(self.npc_db_path, 'r', encoding='utf-8') as f:
                inside_table = False
                table_closed = False
                for line_num, line in enumerate(f, 1):
                    if line.strip().startswith('epochNpcData = {'):
                        inside_table = True
                        table_closed = False
                    elif line.strip() == '}' and inside_table:
                        inside_table = False
                        table_closed = True
                    
                    # Check for common syntax errors
                    if inside_table and re.match(r'^epochNpcData\[(\d+)\]', line):
                        self.syntax_errors.append(f"NPC DB Line {line_num}: Entry has 'epochNpcData' prefix inside table")
                    elif table_closed and re.match(r'^epochNpcData\[(\d+)\]', line):
                        self.syntax_errors.append(f"NPC DB Line {line_num}: Entry added OUTSIDE table (after closing brace)")
                    
                    # Check for missing commas (simplified pattern)
                    if inside_table and re.match(r'^\[\d+\] = \{.*\}', line.strip()):
                        # Check if line ends with } but not },
                        if not line.strip().endswith('},'):
                            # Check if there's a comment - still needs comma before comment
                            if '--' in line:
                                if not re.search(r'\},\s*--', line):
                                    self.syntax_errors.append(f"NPC DB Line {line_num}: Missing comma before comment")
                            else:
                                self.syntax_errors.append(f"NPC DB Line {line_num}: Missing comma after entry")
                    
                    match = re.match(r'^\[?(\d+)\]', line.strip())
                    if match:
                        npc_id = int(match.group(1))
                        self.existing_npcs[npc_id] = line.strip()
    
    def parse_submission(self, text: str) -> Dict:
        """Parse a quest submission from GitHub issue format."""
        data = {
            'quest_id': None,
            'name': None,
            'giver_npc': None,
            'turnin_npc': None,
            'level': None,
            'zone': None,
            'faction': None,
            'objectives': [],
            'mobs': [],
            'items': [],
            'objects': [],
            'coords': None,
            'incomplete': False
        }
        
        # Check for incomplete data warning
        if "⚠️ WARNING: INCOMPLETE DATA ⚠️" in text:
            data['incomplete'] = True
        
        # Extract quest ID and name
        quest_match = re.search(r'Quest ID:\s*(\d+)', text)
        if quest_match:
            data['quest_id'] = int(quest_match.group(1))
            
        name_match = re.search(r'Quest Name:\s*"([^"]+)"', text)
        if not name_match:
            name_match = re.search(r'name\s*=\s*"([^"]+)"', text)
        if name_match:
            data['name'] = name_match.group(1)
        
        # Extract quest giver
        giver_match = re.search(r'questGiver\s*=\s*\{[^}]*npcId\s*=\s*(\d+)[^}]*name\s*=\s*"([^"]+)"', text)
        if giver_match:
            data['giver_npc'] = {
                'id': int(giver_match.group(1)),
                'name': giver_match.group(2)
            }
            # Get coordinates
            coord_match = re.search(r'questGiver.*?coords\s*=\s*\{x\s*=\s*([\d.]+),\s*y\s*=\s*([\d.]+)\}', text, re.DOTALL)
            if coord_match:
                data['giver_npc']['coords'] = {
                    'x': float(coord_match.group(1)),
                    'y': float(coord_match.group(2))
                }
        
        # Extract turn-in NPC
        turnin_match = re.search(r'turnIn\s*=\s*\{[^}]*npcId\s*=\s*(\d+)[^}]*name\s*=\s*"([^"]+)"', text)
        if turnin_match:
            data['turnin_npc'] = {
                'id': int(turnin_match.group(1)),
                'name': turnin_match.group(2)
            }
            # Get coordinates
            coord_match = re.search(r'turnIn.*?coords\s*=\s*\{x\s*=\s*([\d.]+),\s*y\s*=\s*([\d.]+)\}', text, re.DOTALL)
            if coord_match:
                data['turnin_npc']['coords'] = {
                    'x': float(coord_match.group(1)),
                    'y': float(coord_match.group(2))
                }
        
        # Extract level
        level_match = re.search(r'level\s*=\s*(\d+)', text)
        if level_match:
            data['level'] = int(level_match.group(1))
        
        # Extract zone
        zone_match = re.search(r'zone\s*=\s*"([^"]+)"', text)
        if zone_match:
            data['zone'] = zone_match.group(1)
            data['zone_id'] = self.get_zone_id(zone_match.group(1))
        
        # Extract objectives
        obj_pattern = r'\{text\s*=\s*"([^"]+)"[^}]*\}'
        for match in re.finditer(obj_pattern, text):
            data['objectives'].append(match.group(1))
        
        # Extract mobs
        mob_pattern = r'\[(\d+)\]\s*=\s*\{[^}]*name\s*=\s*"([^"]+)"'
        for match in re.finditer(mob_pattern, text):
            data['mobs'].append({
                'id': int(match.group(1)),
                'name': match.group(2)
            })
        
        return data
    
    def get_zone_id(self, zone_name: str) -> Optional[int]:
        """Map zone names to IDs."""
        zone_map = {
            "Dun Morogh": 1,
            "Duskwood": 10,
            "Wetlands": 11,
            "Elwynn Forest": 12,
            "Durotar": 14,
            "The Barrens": 17,
            "Stranglethorn Vale": 33,
            "Alterac Mountains": 36,
            "Westfall": 40,
            "Arathi Highlands": 45,
            "The Hinterlands": 47,
            "Searing Gorge": 51,
            "Tirisfal Glades": 85,
            "Silverpine Forest": 130,
            "Teldrassil": 141,
            "Hillsbrad Foothills": 267,
            "Ashenvale": 331,
            "Feralas": 357,
            "Thousand Needles": 400
        }
        return zone_map.get(zone_name)
    
    def validate_submission(self, data: Dict) -> List[str]:
        """Validate submission data and return list of issues."""
        issues = []
        
        # Check quest ID range
        if not data['quest_id']:
            issues.append("Missing quest ID")
        elif data['quest_id'] < 26000 or data['quest_id'] > 29000:
            issues.append(f"Quest ID {data['quest_id']} outside Epoch range (26000-29000)")
        
        # Check if quest already exists
        if data['quest_id'] and data['quest_id'] in self.existing_quests:
            existing = self.existing_quests[data['quest_id']]
            if '[Epoch] Quest' in existing:
                issues.append(f"INFO: Quest {data['quest_id']} exists with placeholder name - needs update")
            else:
                issues.append(f"WARNING: Quest {data['quest_id']} already exists - check if update needed")
        
        # Check for required fields
        if not data['name']:
            issues.append("Missing quest name")
        elif '[Epoch]' in data['name']:
            issues.append("Quest has placeholder name")
        
        if not data['giver_npc']:
            issues.append("Missing quest giver NPC")
        else:
            # Check if NPC exists
            npc_id = data['giver_npc']['id']
            if npc_id not in self.existing_npcs:
                issues.append(f"Quest giver NPC {npc_id} not in database - needs to be added")
        
        if not data['turnin_npc']:
            issues.append("CRITICAL: Missing turn-in NPC (gold ? won't show)")
        else:
            # Check if NPC exists
            npc_id = data['turnin_npc']['id']
            if npc_id not in self.existing_npcs:
                # Check for phased NPC (±1)
                if (npc_id - 1) in self.existing_npcs:
                    issues.append(f"INFO: Turn-in NPC {npc_id} not found, but {npc_id-1} exists (phasing?)")
                elif (npc_id + 1) in self.existing_npcs:
                    issues.append(f"INFO: Turn-in NPC {npc_id} not found, but {npc_id+1} exists (phasing?)")
                else:
                    issues.append(f"Turn-in NPC {npc_id} not in database - needs to be added")
        
        if data['incomplete']:
            issues.append("INFO: Data marked as incomplete (quest was already in log)")
        
        return issues
    
    def generate_quest_entry(self, data: Dict) -> str:
        """Generate Lua code for quest entry."""
        quest_id = data['quest_id']
        name = data['name'] or f"[Epoch] Quest {quest_id}"
        
        # Quest giver
        giver = "nil"
        if data['giver_npc']:
            giver = f"{{{{{data['giver_npc']['id']}}}}}"
        
        # Turn-in NPC (CRITICAL)
        turnin = "nil"
        if data['turnin_npc']:
            turnin = f"{{{{{data['turnin_npc']['id']}}}}}"
        
        # Level
        level = data['level'] or 60
        
        # Objectives
        objectives = "nil"
        if data['objectives']:
            obj_str = '","'.join(data['objectives'])
            objectives = f'{{"{obj_str}"}}'
        
        # Zone
        zone = data.get('zone_id') or "nil"
        
        # Faction (default to both if not specified)
        faction = data.get('faction', 8)
        
        # Build the entry
        entry = f'epochQuestData[{quest_id}] = {{"{name}",{giver},{turnin},nil,{level},nil,nil,'
        entry += f'{objectives},nil,nil,nil,nil,nil,nil,nil,nil,{zone},nil,nil,nil,nil,nil,{faction},'
        entry += f'0,nil,nil,nil,nil,nil,nil}}'
        
        return entry
    
    def generate_npc_entry(self, npc_data: Dict, zone_id: int = None) -> str:
        """Generate Lua code for NPC entry."""
        npc_id = npc_data['id']
        name = npc_data['name']
        
        # Coordinates
        coords = "nil"
        if 'coords' in npc_data and zone_id:
            x = npc_data['coords']['x']
            y = npc_data['coords']['y']
            coords = f"{{[{zone_id}]={{{{{x:.2f},{y:.2f}}}}}}}}"
        
        # Build the entry WITHOUT epochNpcData prefix (it goes inside the table)
        # IMPORTANT: Just [id] = {...}, not epochNpcData[id] = {...}
        entry = f'[{npc_id}] = {{"{name}",nil,1,60,0,{coords},nil,{zone_id or "nil"},'
        entry += f'nil,nil,nil,"AH",nil,3}}'  # 3 = QUEST_GIVER + GOSSIP
        
        return entry
    
    def process_issue(self, issue_text: str, issue_number: int) -> Dict:
        """Process a single GitHub issue."""
        result = {
            'issue': issue_number,
            'success': False,
            'quest_id': None,
            'action': None,
            'errors': [],
            'warnings': []
        }
        
        # Parse the submission
        data = self.parse_submission(issue_text)
        result['quest_id'] = data['quest_id']
        
        # Validate
        issues = self.validate_submission(data)
        
        # Separate errors from warnings/info
        for issue in issues:
            if issue.startswith(('INFO:', 'WARNING:')):
                result['warnings'].append(issue)
            elif issue.startswith('CRITICAL:'):
                result['errors'].append(issue)
            else:
                result['errors'].append(issue)
        
        # Determine action
        if not result['errors']:
            if data['quest_id'] in self.existing_quests:
                if '[Epoch] Quest' in self.existing_quests[data['quest_id']]:
                    result['action'] = 'update_placeholder'
                else:
                    result['action'] = 'update_existing'
            else:
                result['action'] = 'add_new'
            
            result['success'] = True
            result['quest_entry'] = self.generate_quest_entry(data)
            
            # Generate NPC entries if needed
            result['npc_entries'] = []
            if data['giver_npc'] and data['giver_npc']['id'] not in self.existing_npcs:
                zone_id = data.get('zone_id')
                result['npc_entries'].append(self.generate_npc_entry(data['giver_npc'], zone_id))
            
            if data['turnin_npc'] and data['turnin_npc']['id'] not in self.existing_npcs:
                zone_id = data.get('zone_id')
                result['npc_entries'].append(self.generate_npc_entry(data['turnin_npc'], zone_id))
        
        return result
    
    def generate_report(self, results: List[Dict]) -> str:
        """Generate summary report of processing."""
        report = ["# Quest Data Processing Report\n"]
        
        # Check for syntax errors first
        if self.syntax_errors:
            report.append("## ⚠️ SYNTAX ERRORS DETECTED ⚠️")
            report.append("Fix these before processing new data:\n")
            for error in self.syntax_errors[:5]:  # Show first 5
                report.append(f"- {error}")
            if len(self.syntax_errors) > 5:
                report.append(f"- ... and {len(self.syntax_errors) - 5} more\n")
            report.append("\n**Fix command:**")
            report.append("```bash")
            report.append("# Remove epochNpcData prefix from inside table:")
            report.append("perl -i -pe 's/^epochNpcData(\\[\\d+\\])/\\1/' Database/Epoch/epochNpcDB.lua")
            report.append("# Remove epochQuestData prefix from inside table:")
            report.append("perl -i -pe 's/^epochQuestData(\\[\\d+\\])/\\1/' Database/Epoch/epochQuestDB.lua")
            report.append("```\n")
        
        # Summary stats
        total = len(results)
        successful = sum(1 for r in results if r['success'])
        new_quests = sum(1 for r in results if r.get('action') == 'add_new')
        updated_placeholders = sum(1 for r in results if r.get('action') == 'update_placeholder')
        updated_existing = sum(1 for r in results if r.get('action') == 'update_existing')
        failed = total - successful
        
        report.append(f"## Summary")
        report.append(f"- Total issues processed: {total}")
        report.append(f"- Successful: {successful}")
        report.append(f"  - New quests added: {new_quests}")
        report.append(f"  - Placeholders updated: {updated_placeholders}")
        report.append(f"  - Existing updated: {updated_existing}")
        report.append(f"- Failed: {failed}\n")
        
        # Issues that can be closed
        report.append(f"## Issues Ready to Close")
        closeable = [r['issue'] for r in results if r['success']]
        if closeable:
            report.append(f"Issues: {', '.join(f'#{i}' for i in closeable)}\n")
            report.append("```bash")
            report.append(f"# Close all successful issues:")
            report.append(f"for issue in {' '.join(str(i) for i in closeable)}; do")
            report.append(f"  gh issue close $issue")
            report.append(f"done")
            report.append("```\n")
        else:
            report.append("None\n")
        
        # Failed issues
        if failed > 0:
            report.append(f"## Failed Issues (Need Manual Review)")
            for r in results:
                if not r['success']:
                    report.append(f"\n### Issue #{r['issue']} - Quest {r['quest_id']}")
                    report.append("**Errors:**")
                    for error in r['errors']:
                        report.append(f"- {error}")
                    if r['warnings']:
                        report.append("**Warnings:**")
                        for warning in r['warnings']:
                            report.append(f"- {warning}")
        
        # Successful with warnings
        report.append(f"\n## Successful with Warnings")
        for r in results:
            if r['success'] and r['warnings']:
                report.append(f"\n### Issue #{r['issue']} - Quest {r['quest_id']}")
                for warning in r['warnings']:
                    report.append(f"- {warning}")
        
        return '\n'.join(report)

def main():
    """Main entry point for batch processing."""
    processor = QuestSubmissionProcessor()
    
    # Example: Process multiple issues
    # In practice, you'd fetch these from GitHub API or pass as arguments
    test_submission = """
    Quest ID: 26939
    Quest Name: "Peace in Death"
    
    questGiver = {npcId = 45898, name = "Joseph Strinbrow", coords = {x = 60.45, y = 52.41}}
    turnIn = {npcId = 45898, name = "Joseph Strinbrow", coords = {x = 60.45, y = 52.41}}
    
    objectives = {
        {text = "Joseph Strinbrow's spirit laid to rest", objectId = 60445}
    }
    
    zone = "Tirisfal Glades"
    level = 5
    """
    
    result = processor.process_issue(test_submission, 374)
    print(processor.generate_report([result]))

if __name__ == "__main__":
    main()