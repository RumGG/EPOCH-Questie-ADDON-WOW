#!/usr/bin/env python3
"""
Comprehensive Questie Database Validator
Validates both epochQuestDB.lua and epochNpcDB.lua for ALL possible issues
Run this BEFORE and AFTER making changes to catch problems early!
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

class Colors:
    """Terminal colors for output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class QuestieValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.quest_ids = set()
        self.npc_ids = set()
        self.duplicate_quests = defaultdict(list)
        self.duplicate_npcs = defaultdict(list)
        
    def validate_quest_database(self, filepath='Database/Epoch/epochQuestDB.lua'):
        """Validate the quest database file."""
        print(f"\n{Colors.BOLD}Validating Quest Database{Colors.RESET}")
        print("=" * 60)
        
        if not Path(filepath).exists():
            self.errors.append(f"Quest database not found: {filepath}")
            return False
            
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Check 1: Table structure
        if not self._validate_table_structure(lines, 'epochQuestData'):
            return False
            
        # Check 2: Entry syntax and duplicates
        for i, line in enumerate(lines, 1):
            if re.match(r'^\[\d+\] = \{', line.strip()):
                self._validate_quest_entry(line, i)
                
        # Check 3: Missing commas
        self._check_missing_commas(lines, 'quest')
        
        # Check 4: Wrong prefixes
        self._check_wrong_prefixes(lines, 'epochQuestData')
        
        # Check 5: Brace matching
        self._check_brace_matching(filepath)
        
        return len(self.errors) == 0
        
    def validate_npc_database(self, filepath='Database/Epoch/epochNpcDB.lua'):
        """Validate the NPC database file."""
        print(f"\n{Colors.BOLD}Validating NPC Database{Colors.RESET}")
        print("=" * 60)
        
        if not Path(filepath).exists():
            self.errors.append(f"NPC database not found: {filepath}")
            return False
            
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Check 1: Table structure
        if not self._validate_table_structure(lines, 'epochNpcData'):
            return False
            
        # Check 2: Entry syntax and duplicates
        for i, line in enumerate(lines, 1):
            if re.match(r'^\[\d+\] = \{', line.strip()):
                self._validate_npc_entry(line, i)
                
        # Check 3: Missing commas
        self._check_missing_commas(lines, 'npc')
        
        # Check 4: Wrong prefixes
        self._check_wrong_prefixes(lines, 'epochNpcData')
        
        # Check 5: Brace matching
        self._check_brace_matching(filepath)
        
        # Check 6: Coordinate format
        self._check_coordinate_format(lines)
        
        return len(self.errors) == 0
        
    def _validate_table_structure(self, lines, table_name):
        """Check if table has correct structure."""
        found_start = False
        found_end = False
        found_assignment = False
        inside_table = False
        brace_count = 0
        table_end_line = 0
        
        for i, line in enumerate(lines, 1):
            if f'{table_name} = {{' in line:
                found_start = True
                inside_table = True
                brace_count = line.count('{') - line.count('}')
                continue
                
            if inside_table:
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    found_end = True
                    inside_table = False
                    table_end_line = i
                    
            if f'QuestieDB._{table_name}' in line:
                found_assignment = True
                if inside_table or i < table_end_line:
                    self.errors.append(f"Line {i}: QuestieDB assignment inside table structure!")
                    
        if not found_start:
            self.errors.append(f"Missing table declaration: {table_name} = {{")
        if not found_end:
            self.errors.append(f"Table {table_name} not properly closed")
        if not found_assignment:
            self.warnings.append(f"Missing QuestieDB assignment for {table_name}")
            
        return found_start and found_end
        
    def _validate_quest_entry(self, line, line_num):
        """Validate a single quest entry."""
        # Extract quest ID
        match = re.match(r'^\[(\d+)\] = \{', line.strip())
        if not match:
            return
            
        quest_id = int(match.group(1))
        
        # Check for duplicates
        if quest_id in self.quest_ids:
            self.duplicate_quests[quest_id].append(line_num)
        else:
            self.quest_ids.add(quest_id)
            
        # Parse fields
        try:
            # Extract content between outer braces
            content_match = re.search(r'^\[\d+\] = \{(.+)\},?$', line.strip())
            if not content_match:
                self.errors.append(f"Line {line_num}: Malformed quest entry")
                return
                
            content = content_match.group(1)
            fields = self._parse_lua_fields(content)
            
            # Validate field count (should be 30 for quests)
            if len(fields) < 30:
                self.warnings.append(f"Line {line_num}: Quest {quest_id} has only {len(fields)} fields (expected 30)")
            elif len(fields) > 30:
                self.warnings.append(f"Line {line_num}: Quest {quest_id} has {len(fields)} fields (expected 30)")
                
            # Validate specific fields
            self._validate_quest_fields(quest_id, fields, line_num)
            
        except Exception as e:
            self.errors.append(f"Line {line_num}: Failed to parse quest {quest_id}: {e}")
            
    def _validate_npc_entry(self, line, line_num):
        """Validate a single NPC entry."""
        # Extract NPC ID
        match = re.match(r'^\[(\d+)\] = \{', line.strip())
        if not match:
            return
            
        npc_id = int(match.group(1))
        
        # Check for duplicates
        if npc_id in self.npc_ids:
            self.duplicate_npcs[npc_id].append(line_num)
        else:
            self.npc_ids.add(npc_id)
            
        # Check for triple-nested coordinates
        if '{{{' in line:
            self.errors.append(f"Line {line_num}: NPC {npc_id} has triple-nested coordinates")
            
    def _validate_quest_fields(self, quest_id, fields, line_num):
        """Validate quest field types and values."""
        if len(fields) < 5:
            return
            
        # Field indices (0-based)
        FIELD_NAMES = {
            0: 'name',
            1: 'startedBy',
            2: 'finishedBy', 
            3: 'requiredSkill',
            4: 'requiredLevel',
            5: 'questLevel',
            6: 'requiredRaces',
            7: 'requiredClasses',
            8: 'objectives',
            16: 'zoneOrSort',
            22: 'questSort',
            23: 'questFlags'
        }
        
        # Check field 3 (requiredSkill) - should be nil or skill table
        if len(fields) > 3:
            field3 = fields[3].strip()
            if field3.startswith('{{') and not field3.startswith('{['):
                # This looks like an NPC reference, not skill data
                self.errors.append(f"Line {line_num}: Quest {quest_id} has NPC data in requiredSkill field (field 4)")
                
        # Check field 4 (requiredLevel) - must be number or nil
        if len(fields) > 4:
            field4 = fields[4].strip()
            if field4.startswith('{'):
                self.errors.append(f"Line {line_num}: Quest {quest_id} has table in requiredLevel field (field 5)")
            elif field4 != 'nil' and not field4.isdigit():
                self.warnings.append(f"Line {line_num}: Quest {quest_id} has invalid requiredLevel: {field4}")
                
        # Check field 5 (questLevel) - must be number or nil
        if len(fields) > 5:
            field5 = fields[5].strip()
            if field5.startswith('{'):
                self.errors.append(f"Line {line_num}: Quest {quest_id} has table in questLevel field (field 6)")
                
        # Check numeric fields
        numeric_fields = [4, 5, 6, 16, 22, 23]  # 0-based indices
        for idx in numeric_fields:
            if idx < len(fields):
                field = fields[idx].strip()
                if field.startswith('{') and idx not in [6, 7]:  # races/classes can be tables
                    field_name = FIELD_NAMES.get(idx, f'field {idx+1}')
                    self.errors.append(f"Line {line_num}: Quest {quest_id} has table in {field_name} (should be numeric)")
                    
    def _parse_lua_fields(self, content):
        """Parse Lua table fields respecting nested structures."""
        fields = []
        current = ''
        depth = 0
        in_string = False
        
        for char in content:
            if char == '"' and (not current or current[-1] != '\\'):
                in_string = not in_string
            elif not in_string:
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                elif char == ',' and depth == 0:
                    fields.append(current.strip())
                    current = ''
                    continue
            current += char
            
        if current:
            fields.append(current.strip())
            
        return fields
        
    def _check_missing_commas(self, lines, db_type):
        """Check for missing commas at end of entries."""
        for i, line in enumerate(lines, 1):
            if re.match(r'^\[\d+\] = \{.*\}$', line.strip()):
                # This is an entry line
                if not line.rstrip().endswith(','):
                    # Check if next non-empty line is another entry or closing brace
                    for j in range(i, min(i+5, len(lines))):
                        next_line = lines[j].strip()
                        if next_line and not next_line.startswith('--'):
                            if next_line.startswith('[') or next_line == '}':
                                self.errors.append(f"Line {i}: Missing comma at end of {db_type} entry")
                                break
                            break
                            
    def _check_wrong_prefixes(self, lines, table_name):
        """Check for entries with wrong table prefix."""
        for i, line in enumerate(lines, 1):
            if re.match(f'^{table_name}\\[\\d+\\]', line.strip()):
                self.errors.append(f"Line {i}: Entry has wrong prefix '{table_name}[' (should be just '[')")
                
    def _check_brace_matching(self, filepath):
        """Check if braces are balanced."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces != close_braces:
            self.errors.append(f"Brace mismatch: {open_braces} open, {close_braces} close")
            
    def _check_coordinate_format(self, lines):
        """Check for triple-nested coordinate formats."""
        triple_nested = 0
        for i, line in enumerate(lines, 1):
            if '{{{' in line:
                triple_nested += 1
                
        if triple_nested > 0:
            self.errors.append(f"Found {triple_nested} lines with triple-nested coordinates {{{{{{}}}}}}")
            
    def print_report(self):
        """Print validation report."""
        print(f"\n{Colors.BOLD}VALIDATION REPORT{Colors.RESET}")
        print("=" * 60)
        
        # Errors (critical - will break WoW)
        if self.errors:
            print(f"\n{Colors.RED}❌ ERRORS ({len(self.errors)} found) - MUST FIX:{Colors.RESET}")
            for error in self.errors[:20]:  # Show first 20
                print(f"  • {error}")
            if len(self.errors) > 20:
                print(f"  ... and {len(self.errors) - 20} more")
        else:
            print(f"\n{Colors.GREEN}✅ No critical errors found{Colors.RESET}")
            
        # Warnings (won't break WoW but should fix)
        if self.warnings:
            print(f"\n{Colors.YELLOW}⚠️  WARNINGS ({len(self.warnings)} found):{Colors.RESET}")
            for warning in self.warnings[:10]:
                print(f"  • {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
                
        # Duplicates
        if self.duplicate_quests:
            print(f"\n{Colors.YELLOW}📋 Duplicate Quest IDs:{Colors.RESET}")
            for quest_id, lines in list(self.duplicate_quests.items())[:5]:
                print(f"  • Quest {quest_id} on lines: {lines}")
                
        if self.duplicate_npcs:
            print(f"\n{Colors.YELLOW}📋 Duplicate NPC IDs:{Colors.RESET}")
            for npc_id, lines in list(self.duplicate_npcs.items())[:5]:
                print(f"  • NPC {npc_id} on lines: {lines}")
                
        # Summary
        print(f"\n{Colors.BOLD}SUMMARY:{Colors.RESET}")
        print(f"  Total Quests: {len(self.quest_ids)}")
        print(f"  Total NPCs: {len(self.npc_ids)}")
        print(f"  Errors: {len(self.errors)}")
        print(f"  Warnings: {len(self.warnings)}")
        print(f"  Duplicate Quests: {len(self.duplicate_quests)}")
        print(f"  Duplicate NPCs: {len(self.duplicate_npcs)}")
        
        # Final verdict
        print(f"\n{Colors.BOLD}VERDICT:{Colors.RESET}")
        if self.errors:
            print(f"{Colors.RED}❌ DATABASE HAS CRITICAL ERRORS - FIX BEFORE STARTING WOW{Colors.RESET}")
            return False
        elif self.warnings or self.duplicate_quests or self.duplicate_npcs:
            print(f"{Colors.YELLOW}⚠️  Database will work but has issues that should be fixed{Colors.RESET}")
            return True
        else:
            print(f"{Colors.GREEN}✅ DATABASE IS CLEAN AND READY!{Colors.RESET}")
            return True
            
def quick_fix_common_issues():
    """Offer to automatically fix common issues."""
    print(f"\n{Colors.BOLD}QUICK FIX OPTIONS:{Colors.RESET}")
    print("1. Fix all missing commas")
    print("2. Fix wrong table prefixes")
    print("3. Fix triple-nested coordinates")
    print("4. Remove duplicate entries (keeps first)")
    print("5. Run all fixes")
    print("0. Skip fixes")
    
    choice = input("\nSelect option (0-5): ").strip()
    
    if choice == '0':
        return
        
    if choice in ['1', '5']:
        print("Fixing missing commas...")
        import subprocess
        subprocess.run(['python3', 'fix_all_commas.py'], check=False)
        
    if choice in ['2', '5']:
        print("Fixing wrong prefixes...")
        import subprocess
        subprocess.run(['perl', '-i', '-pe', "s/^epochQuestData(\\[\\d+\\])/\\1/", 
                       'Database/Epoch/epochQuestDB.lua'], check=False)
        subprocess.run(['perl', '-i', '-pe', "s/^epochNpcData(\\[\\d+\\])/\\1/", 
                       'Database/Epoch/epochNpcDB.lua'], check=False)
                       
    if choice in ['3', '5']:
        print("Fixing coordinate format...")
        import subprocess
        subprocess.run(['python3', 'fix_npc_issues.py'], check=False)
        
    if choice in ['4', '5']:
        print("Removing duplicates...")
        # Would need to implement duplicate removal
        print("  (Manual review recommended for duplicates)")
        
    print(f"\n{Colors.GREEN}Fixes applied! Run validator again to verify.{Colors.RESET}")

def main():
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     QUESTIE DATABASE VALIDATOR - COMPREHENSIVE CHECK      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    # Check for --fix flag
    auto_fix = '--fix' in sys.argv
    interactive = '--interactive' in sys.argv
    
    validator = QuestieValidator()
    
    # Validate both databases
    quest_ok = validator.validate_quest_database()
    npc_ok = validator.validate_npc_database()
    
    # Print report
    validator.print_report()
    
    # Auto-fix or offer fixes if there are errors
    if validator.errors:
        if auto_fix:
            print(f"\n{Colors.YELLOW}Running automatic fixes...{Colors.RESET}")
            import subprocess
            subprocess.run(['python3', 'fix_all_commas.py'], check=False)
            subprocess.run(['python3', 'fix_npc_issues.py'], check=False)
            print(f"{Colors.GREEN}Fixes applied! Run validator again to verify.{Colors.RESET}")
        elif interactive:
            quick_fix_common_issues()
        else:
            print(f"\n{Colors.YELLOW}Run with --fix to automatically fix common issues{Colors.RESET}")
            print(f"Or run with --interactive for manual fix selection")
        
    # Exit code for scripting
    sys.exit(0 if (quest_ok and npc_ok) else 1)

if __name__ == "__main__":
    main()