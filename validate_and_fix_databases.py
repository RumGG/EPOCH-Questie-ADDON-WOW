#!/usr/bin/env python3
"""
Questie Database Validator and Fixer
Validates and fixes common issues in epochQuestDB.lua and epochNpcDB.lua files.
"""

import re
import sys
import os
from pathlib import Path
import argparse
from collections import defaultdict

class QuestieDBValidator:
    def __init__(self, auto_fix=False):
        self.auto_fix = auto_fix
        self.issues = []
        self.fixes_applied = []
        
        # Quest field definitions (index to name mapping)
        self.quest_fields = {
            0: 'name',
            1: 'startedBy',
            2: 'finishedBy',
            3: 'requiredLevel',
            4: 'questLevel',
            5: 'requiredRaces',
            6: 'requiredClasses',
            7: 'objectivesText',
            8: 'triggerEnd',
            9: 'objectives',
            10: 'sourceItemId',
            11: 'preQuestGroup',
            12: 'preQuestSingle',
            13: 'childQuests',
            14: 'inGroupWith',
            15: 'exclusiveTo',
            16: 'zoneOrSort',
            17: 'requiredSkill',
            18: 'requiredMinRep',
            19: 'requiredMaxRep',
            20: 'requiredSourceItems',
            21: 'nextQuestInChain',
            22: 'questFlags',
            23: 'specialFlags',
            24: 'parentQuest',
            25: 'reputationReward',
            26: 'extraObjectives',
            27: 'requiredSpell',
            28: 'requiredSpecialization',
            29: 'requiredMaxLevel'
        }
        
        # NPC field definitions
        self.npc_fields = {
            0: 'name',
            1: 'minLevel',
            2: 'maxLevel',
            3: 'minLevelHealth',
            4: 'maxLevelHealth',
            5: 'rank',
            6: 'spawns',
            7: 'waypoints',
            8: 'zoneID',
            9: 'questStarts',
            10: 'questEnds',
            11: 'factionID',
            12: 'friendlyToFaction',
            13: 'npcFlags',
            14: 'id'
        }

    def escape_double_dash(self, text):
        """Escape double dashes in strings to prevent Lua comment issues."""
        if isinstance(text, str) and '--' in text:
            # Replace -- with a single dash or em dash
            return text.replace('--', '-')
        return text

    def parse_lua_value(self, value_str):
        """Parse a Lua value string and return Python equivalent."""
        value_str = value_str.strip()
        
        if value_str == 'nil':
            return None
        elif value_str.startswith('"') and value_str.endswith('"'):
            # String value - unescape and check for double dash
            unescaped = value_str[1:-1].replace('\\"', '"').replace('\\\\', '\\')
            return self.escape_double_dash(unescaped)
        elif value_str.startswith('{'):
            # Table/array - keep as string but check for double dash
            return self.escape_double_dash(value_str)
        elif value_str.isdigit() or (value_str.startswith('-') and value_str[1:].isdigit()):
            return int(value_str)
        else:
            return value_str

    def smart_split(self, content):
        """Split content by commas that are not inside brackets or quotes."""
        fields = []
        current_field = ''
        depth = 0
        in_quotes = False
        escape_next = False
        
        for char in content:
            if escape_next:
                current_field += char
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                current_field += char
                continue
                
            if char == '"' and not escape_next:
                in_quotes = not in_quotes
                current_field += char
            elif not in_quotes:
                if char == '{':
                    depth += 1
                    current_field += char
                elif char == '}':
                    depth -= 1
                    current_field += char
                elif char == ',' and depth == 0:
                    fields.append(current_field.strip())
                    current_field = ''
                else:
                    current_field += char
            else:
                current_field += char
                
        if current_field.strip():
            fields.append(current_field.strip())
            
        return fields

    def fix_field_type(self, field_str, expected_type):
        """Fix common field type errors."""
        field_str = field_str.strip()
        
        if expected_type == 'number':
            # Handle {{number}} -> number
            if field_str.startswith('{{') and field_str.endswith('}}'):
                numbers = re.findall(r'\d+', field_str)
                if numbers:
                    return numbers[0]
            # Handle {number} -> number
            elif field_str.startswith('{') and field_str.endswith('}'):
                numbers = re.findall(r'\d+', field_str)
                if numbers and len(numbers) == 1:
                    return numbers[0]
        
        return field_str

    def validate_quest_entry(self, quest_id, entry_str, line_num):
        """Validate a single quest entry and fix if needed."""
        issues = []
        
        # Parse the entry
        match = re.match(r'^\[(\d+)\] = \{(.*)\}', entry_str.strip())
        if not match:
            issues.append(f"Line {line_num}: Quest {quest_id} - Malformed entry structure")
            return issues, None
            
        content = match.group(2)
        
        # Split by commas not inside brackets or quotes
        fields = self.smart_split(content)
        
        # Check and fix each field
        fixed_fields = []
        for i, field in enumerate(fields):
            field_name = self.quest_fields.get(i, f'field_{i}')
            field = field.strip()
            
            # Fix double dash in name field
            if i == 0 and '--' in field:
                if self.auto_fix:
                    old_field = field
                    field = field.replace('--', '-')
                    self.fixes_applied.append(f"Quest {quest_id}: Fixed double dash in name")
                else:
                    issues.append(f"Line {line_num}: Quest {quest_id} - Name contains double dash which breaks Lua comments")
            
            # Fix requiredLevel and questLevel type errors
            if field_name in ['requiredLevel', 'questLevel'] and field != 'nil':
                if field.startswith('{{') or (field.startswith('{') and not field.startswith('{{')):
                    if self.auto_fix:
                        old_field = field
                        field = self.fix_field_type(field, 'number')
                        if field != old_field:
                            self.fixes_applied.append(f"Quest {quest_id}: Fixed {field_name} from {old_field} to {field}")
                    else:
                        issues.append(f"Line {line_num}: Quest {quest_id} - {field_name} should be number, got {field}")
            
            # Fix numeric fields that should be numbers
            if field_name in ['zoneOrSort', 'nextQuestInChain', 'questFlags', 'specialFlags', 'parentQuest'] and field != 'nil':
                if field.startswith('{'):
                    if self.auto_fix:
                        old_field = field
                        field = self.fix_field_type(field, 'number')
                        if field != old_field:
                            self.fixes_applied.append(f"Quest {quest_id}: Fixed {field_name} from {old_field} to {field}")
                    else:
                        issues.append(f"Line {line_num}: Quest {quest_id} - {field_name} should be number, got {field}")
            
            # Check objectives field for nil creature/item/spell IDs
            if field_name == 'objectives' and field != 'nil':
                # Check for {{{nil, patterns - two common formats
                if '{{{nil,' in field:
                    if self.auto_fix:
                        # Move to spell objective (position 6)
                        # Two patterns to handle:
                        # Pattern 1: {{{nil,"text",num}}} -> {nil,nil,nil,nil,nil,{{1,"text",num}}}
                        # Pattern 2: {{{nil,num,"text"}}} -> {nil,nil,nil,nil,nil,{{1,"text",num}}}
                        
                        # Try pattern 1 first (text before number)
                        match = re.search(r'\{\{\{nil,(".*?"),(\d+)\}\}\}', field)
                        if match:
                            text = match.group(1)
                            count = match.group(2)
                            field = f"{{nil,nil,nil,nil,nil,{{{{1,{text},{count}}}}}}}"
                            self.fixes_applied.append(f"Quest {quest_id}: Fixed nil objective ID - moved to spellObjective")
                        else:
                            # Try pattern 2 (number before text)
                            match = re.search(r'\{\{\{nil,(\d+),(".*?")\}\}\}', field)
                            if match:
                                count = match.group(1)
                                text = match.group(2)
                                field = f"{{nil,nil,nil,nil,nil,{{{{1,{text},{count}}}}}}}"
                                self.fixes_applied.append(f"Quest {quest_id}: Fixed nil objective ID - moved to spellObjective (reordered)")
                    else:
                        issues.append(f"Line {line_num}: Quest {quest_id} - objectives has nil ID which will cause parsing errors")
            
            fixed_fields.append(field)
        
        return issues, fixed_fields if self.auto_fix else None

    def validate_npc_entry(self, npc_id, entry_str, line_num):
        """Validate a single NPC entry and fix if needed."""
        issues = []
        
        # Parse the entry
        match = re.match(r'^\[(\d+)\] = \{(.*)\}', entry_str.strip())
        if not match:
            issues.append(f"Line {line_num}: NPC {npc_id} - Malformed entry structure")
            return issues, None
            
        content = match.group(2)
        
        # Check for duplicate zone spawns (common data entry error)
        # Pattern: {[12]={{coords}}},{[12]={{coords}}} - same zone listed twice
        duplicate_zone_pattern = r'\{\[(\d+)\]\=\{\{[^}]+\}\}\},\{\[\1\]\=\{\{[^}]+\}\}\}'
        if re.search(duplicate_zone_pattern, content):
            if self.auto_fix:
                # Remove the duplicate zone entry
                # Find all zone entries
                zone_matches = re.findall(r'\{\[(\d+)\]\=\{\{[^}]+\}\}\}', content)
                seen_zones = set()
                new_content_parts = []
                
                # Split content into parts and rebuild without duplicates
                parts = self.smart_split(content)
                for i, part in enumerate(parts):
                    if i == 6:  # spawns field (index 6)
                        # Extract unique zones only
                        zone_data = {}
                        current_zones = re.findall(r'\[(\d+)\]\=\{\{([^}]+)\}\}', part)
                        for zone_id, coords in current_zones:
                            if zone_id not in zone_data:
                                zone_data[zone_id] = coords
                        
                        # Rebuild spawns field without duplicates
                        if zone_data:
                            spawn_parts = []
                            for zone_id, coords in zone_data.items():
                                spawn_parts.append(f"[{zone_id}]={{{{{coords}}}}}")
                            part = "{" + ",".join(spawn_parts) + "}"
                            if len(zone_data) > 1:
                                self.fixes_applied.append(f"NPC {npc_id}: Removed duplicate zone spawns")
                    
                    new_content_parts.append(part)
                
                content = ','.join(new_content_parts)
            else:
                issues.append(f"Line {line_num}: NPC {npc_id} - Has duplicate zone spawn entries")
        
        # Fix zone separator issues
        if '},{[' in content:
            if self.auto_fix:
                content = content.replace('},{[', '},[')
                self.fixes_applied.append(f"NPC {npc_id}: Fixed zone spawn separator")
            else:
                issues.append(f"Line {line_num}: NPC {npc_id} - Incorrect zone spawn separator pattern detected")
        
        # Fix double dash in name
        if '--' in content and not content.index('--') > content.rfind('"'):
            # Double dash is inside the actual data, not a comment
            if self.auto_fix:
                # Find the name field (first quoted string)
                name_match = re.search(r'"([^"]*--[^"]*)"', content)
                if name_match:
                    old_name = name_match.group(1)
                    new_name = old_name.replace('--', '-')
                    content = content.replace(f'"{old_name}"', f'"{new_name}"')
                    self.fixes_applied.append(f"NPC {npc_id}: Fixed double dash in name")
            else:
                issues.append(f"Line {line_num}: NPC {npc_id} - Name contains double dash which breaks Lua comments")
        
        return issues, content if self.auto_fix else None

    def validate_file(self, filepath, db_type='quest'):
        """Validate a database file."""
        self.issues = []
        duplicates = defaultdict(list)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Skip non-entry lines
            if not line.strip().startswith('['):
                continue
            
            # Extract ID
            id_match = re.match(r'^\[(\d+)\]', line.strip())
            if not id_match:
                continue
                
            entry_id = id_match.group(1)
            duplicates[entry_id].append(line_num)
            
            # Skip commented lines
            if line.strip().startswith('--'):
                continue
            
            # Get the full entry (might span multiple lines)
            entry_str = line.strip()
            if not entry_str.rstrip().endswith(',') and not entry_str.rstrip().endswith('},'):
                # Multi-line entry
                for j in range(i+1, len(lines)):
                    entry_str += ' ' + lines[j].strip()
                    if lines[j].strip().endswith(',') or lines[j].strip().endswith('},'):
                        break
            
            # Remove trailing comma and comments for validation
            if ' --' in entry_str:
                entry_str = entry_str[:entry_str.index(' --')]
            entry_str = entry_str.rstrip(',')
            
            # Validate based on type
            if db_type == 'quest':
                issues, _ = self.validate_quest_entry(entry_id, entry_str, line_num)
            else:
                issues, _ = self.validate_npc_entry(entry_id, entry_str, line_num)
            
            self.issues.extend(issues)
        
        # Report duplicates
        for entry_id, line_nums in duplicates.items():
            if len(line_nums) > 1:
                self.issues.append(f"Duplicate {db_type} ID {entry_id} on lines: {line_nums}")
        
        return self.issues

    def fix_file(self, filepath, db_type='quest'):
        """Fix issues in a database file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        seen_ids = set()
        
        for i, line in enumerate(lines):
            line_num = i + 1
            
            # Keep non-entry lines as-is
            if not line.strip().startswith('['):
                fixed_lines.append(line)
                continue
            
            # Extract ID
            id_match = re.match(r'^\[(\d+)\]', line.strip())
            if not id_match:
                fixed_lines.append(line)
                continue
                
            entry_id = id_match.group(1)
            
            # Handle duplicates
            if entry_id in seen_ids:
                self.fixes_applied.append(f"Commented out duplicate {db_type} {entry_id} on line {line_num}")
                fixed_lines.append(f"-- DUPLICATE: {line}")
                continue
            
            seen_ids.add(entry_id)
            
            # Skip already commented lines
            if line.strip().startswith('--'):
                fixed_lines.append(line)
                continue
            
            # Get the full entry
            entry_str = line.strip()
            comment = ''
            if ' --' in entry_str:
                comment = entry_str[entry_str.index(' --'):]
                entry_str = entry_str[:entry_str.index(' --')]
            entry_str = entry_str.rstrip(',')
            
            # Fix based on type
            if db_type == 'quest':
                issues, fixed_fields = self.validate_quest_entry(entry_id, entry_str, line_num)
                if fixed_fields:
                    # Reconstruct the quest entry
                    fixed_line = f"[{entry_id}] = {{{','.join(fixed_fields)}}},{comment}\n"
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
            else:
                issues, fixed_content = self.validate_npc_entry(entry_id, entry_str, line_num)
                if fixed_content:
                    # Reconstruct the NPC entry
                    fixed_line = f"[{entry_id}] = {{{fixed_content}}},{comment}\n"
                    fixed_lines.append(fixed_line)
                else:
                    fixed_lines.append(line)
        
        return fixed_lines

    def validate_and_fix(self, quest_db_path, npc_db_path):
        """Validate and optionally fix both database files."""
        print("\033[1mChecking Quest Database...\033[0m")
        quest_issues = self.validate_file(quest_db_path, 'quest')
        
        print("\n\033[1mChecking NPC Database...\033[0m")
        npc_issues = self.validate_file(npc_db_path, 'npc')
        
        all_issues = quest_issues + npc_issues
        
        # Display results
        print("\n\033[1mValidation Results:\033[0m")
        print("-" * 40)
        
        if all_issues:
            # Group issues by type
            errors = [i for i in all_issues if 'Duplicate' in i or 'should be number' in i or 'double dash' in i]
            warnings = [i for i in all_issues if i not in errors]
            
            if errors:
                print(f"\033[91mErrors found ({len(errors)}):\033[0m")
                for error in errors[:10]:  # Show first 10
                    print(f"  • {error}")
                if len(errors) > 10:
                    print(f"  ... and {len(errors) - 10} more errors")
            
            if warnings:
                print(f"\n\033[93mWarnings found ({len(warnings)}):\033[0m")
                for warning in warnings[:5]:  # Show first 5
                    print(f"  • {warning}")
                if len(warnings) > 5:
                    print(f"  ... and {len(warnings) - 5} more warnings")
        else:
            print("\033[92m✓ No issues found!\033[0m")
        
        # Apply fixes if requested
        if self.auto_fix and all_issues:
            print("\n\033[96mApplying fixes...\033[0m")
            
            # Fix quest database
            print("\n\033[96mFixing quest database...\033[0m")
            fixed_quest_lines = self.fix_file(quest_db_path, 'quest')
            output_path = quest_db_path.replace('.lua', '_FIXED.lua')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_quest_lines)
            print(f"  Fixed quest database saved to: {output_path}")
            
            # Fix NPC database
            print("\n\033[96mFixing npc database...\033[0m")
            fixed_npc_lines = self.fix_file(npc_db_path, 'npc')
            output_path = npc_db_path.replace('.lua', '_FIXED.lua')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_npc_lines)
            print(f"  Fixed NPC database saved to: {output_path}")
            
            # Show fixes applied
            if self.fixes_applied:
                print(f"\n\033[92mFixes applied ({len(self.fixes_applied)}):\033[0m")
                for fix in self.fixes_applied[:10]:
                    print(f"  ✓ {fix}")
                if len(self.fixes_applied) > 10:
                    print(f"  ... and {len(self.fixes_applied) - 10} more fixes")
            
            print("\n\033[1mNext steps:\033[0m")
            print("1. Review the _FIXED files to ensure changes are correct")
            print("2. Back up your original files")
            print("3. Rename _FIXED files to replace originals")
            print("4. Restart WoW completely")
            
            return True
        
        return len(all_issues) == 0

def main():
    parser = argparse.ArgumentParser(description='Validate and fix Questie Epoch database files')
    parser.add_argument('--fix', action='store_true', help='Apply fixes automatically')
    parser.add_argument('--quest-db', default='Database/Epoch/epochQuestDB.lua', help='Path to quest database')
    parser.add_argument('--npc-db', default='Database/Epoch/epochNpcDB.lua', help='Path to NPC database')
    
    args = parser.parse_args()
    
    print("\033[1mQuestie Database Validator and Fixer\033[0m")
    print("=" * 60)
    
    # Check if files exist
    if not os.path.exists(args.quest_db):
        print(f"\033[91mError: Quest database not found: {args.quest_db}\033[0m")
        sys.exit(1)
    if not os.path.exists(args.npc_db):
        print(f"\033[91mError: NPC database not found: {args.npc_db}\033[0m")
        sys.exit(1)
    
    validator = QuestieDBValidator(auto_fix=args.fix)
    success = validator.validate_and_fix(args.quest_db, args.npc_db)
    
    if not args.fix and not success:
        print("\n\033[93mTip: Run with --fix to automatically fix these issues\033[0m")
        sys.exit(1)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()