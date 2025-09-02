#!/usr/bin/env python3
"""
Comprehensive syntax fixer for Questie database files.
Handles ALL common syntax issues including:
- Missing commas
- Wrong table prefixes
- Misplaced code outside tables
- Table structure issues
"""

import re
import sys
from pathlib import Path

class ComprehensiveDatabaseFixer:
    def __init__(self, filename):
        self.filename = filename
        self.lines = []
        self.table_name = None
        self.fixes_made = []
        
    def load_file(self):
        """Load the database file."""
        with open(self.filename, 'r', encoding='utf-8') as f:
            self.lines = f.readlines()
        
        # Detect table name
        for line in self.lines:
            if 'epochNpcData = {' in line:
                self.table_name = 'epochNpcData'
                break
            elif 'epochQuestData = {' in line:
                self.table_name = 'epochQuestData'
                break
    
    def fix_all_issues(self):
        """Fix all syntax issues in the file."""
        print(f"\n{'='*60}")
        print(f"Fixing {self.filename}")
        print('='*60)
        
        # Step 1: Find table boundaries
        table_start = -1
        table_end = -1
        brace_count = 0
        
        for i, line in enumerate(self.lines):
            if f'{self.table_name} = {{' in line:
                table_start = i
                brace_count = 1
            elif table_start >= 0:
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0:
                    table_end = i
                    break
        
        if table_start == -1:
            print(f"❌ Could not find table start for {self.table_name}")
            return False
            
        print(f"📍 Table spans lines {table_start+1} to {table_end+1}")
        
        # Step 2: Fix entries with wrong prefix inside table
        for i in range(table_start + 1, table_end):
            line = self.lines[i]
            if re.match(f'^{self.table_name}\\[\\d+\\]', line):
                # Remove the prefix
                self.lines[i] = re.sub(f'^{self.table_name}(\\[\\d+\\])', r'\1', line)
                self.fixes_made.append(f"Line {i+1}: Removed {self.table_name} prefix inside table")
        
        # Step 3: Fix missing commas inside table
        for i in range(table_start + 1, table_end):
            line = self.lines[i]
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('--'):
                continue
            
            # Check if this is a table entry
            if re.match(r'^\[\d+\] = \{.*\}', line.strip()):
                # Check if it needs a comma
                if not line.rstrip().endswith('},') and not line.rstrip().endswith('},\n'):
                    # Check if next non-empty line is another entry or closing brace
                    next_line_idx = i + 1
                    while next_line_idx < table_end:
                        next_line = self.lines[next_line_idx].strip()
                        if next_line and not next_line.startswith('--'):
                            if next_line.startswith('[') or next_line == '}':
                                # This line needs a comma
                                if '--' in line:
                                    # Add comma before comment
                                    self.lines[i] = re.sub(r'\}(\s*)(--.*)?(\n?)$', r'},\1\2\3', line)
                                else:
                                    # Add comma at end
                                    self.lines[i] = line.rstrip() + ',\n'
                                self.fixes_made.append(f"Line {i+1}: Added missing comma")
                            break
                        next_line_idx += 1
        
        # Step 4: Move code that should be after table
        code_after_table = []
        entries_after_table = []
        
        for i in range(table_end + 1, len(self.lines)):
            line = self.lines[i]
            # Check for entries that should be inside table
            if re.match(f'^{self.table_name}\\[\\d+\\]', line) or re.match(r'^\[\d+\] = \{', line):
                entries_after_table.append((i, line))
            # Check for code that should be after table (like QuestieDB assignment)
            elif 'QuestieDB._' in line or line.strip() and not line.strip().startswith('--'):
                code_after_table.append((i, line))
        
        # Step 5: Reorganize if needed
        if entries_after_table:
            print(f"⚠️  Found {len(entries_after_table)} entries after table close - moving inside")
            # Move entries inside table
            new_lines = []
            
            # Add everything up to table end (excluding closing brace)
            new_lines.extend(self.lines[:table_end])
            
            # Add entries that were after table (fixing prefixes)
            for idx, line in entries_after_table:
                if re.match(f'^{self.table_name}\\[\\d+\\]', line):
                    line = re.sub(f'^{self.table_name}(\\[\\d+\\])', r'\1', line)
                # Ensure comma
                if not line.rstrip().endswith(','):
                    line = line.rstrip() + ',\n'
                new_lines.append(line)
                self.fixes_made.append(f"Line {idx+1}: Moved entry inside table")
            
            # Add closing brace
            new_lines.append('}\n')
            
            # Add code that should be after table
            new_lines.append('\n')
            for idx, line in code_after_table:
                new_lines.append(line)
            
            # Add any remaining lines (comments, etc)
            for i in range(table_end + 1, len(self.lines)):
                line = self.lines[i]
                is_entry = any(i == idx for idx, _ in entries_after_table)
                is_code = any(i == idx for idx, _ in code_after_table)
                if not is_entry and not is_code and line.strip() != '}':
                    new_lines.append(line)
            
            self.lines = new_lines
        
        # Special case: QuestieDB assignment inside table
        for i in range(table_start + 1, table_end):
            line = self.lines[i]
            if 'QuestieDB._' in line:
                print(f"⚠️  Line {i+1}: QuestieDB assignment inside table - needs to be moved after")
                # This is tricky - we need to restructure
                # Remove this line from inside table
                self.lines[i] = ''
                # Find the closing brace and add after it
                for j in range(i, len(self.lines)):
                    if self.lines[j].strip() == '}':
                        self.lines.insert(j + 1, '\n' + line)
                        self.fixes_made.append(f"Line {i+1}: Moved QuestieDB assignment after table")
                        break
        
        return True
    
    def save_file(self):
        """Save the fixed file."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.writelines(self.lines)
    
    def report(self):
        """Report what was fixed."""
        if self.fixes_made:
            print(f"\n✅ Fixed {len(self.fixes_made)} issues:")
            for fix in self.fixes_made[:20]:  # Show first 20
                print(f"  - {fix}")
            if len(self.fixes_made) > 20:
                print(f"  ... and {len(self.fixes_made) - 20} more")
        else:
            print("✅ No issues found")

def validate_lua_structure(filename):
    """Validate basic Lua table structure."""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    
    if open_braces != close_braces:
        print(f"⚠️  Brace mismatch: {open_braces} open, {close_braces} close")
        return False
    
    # Check for basic structure
    if 'epochNpcData = {' in content or 'epochQuestData = {' in content:
        # Find the assignment
        if 'QuestieDB._' in content:
            # Check it's after the closing brace
            table_close = content.rfind('}')
            questie_assign = content.find('QuestieDB._')
            if questie_assign < table_close:
                print("⚠️  QuestieDB assignment appears before table close")
                return False
    
    return True

def main():
    """Main function."""
    print("="*60)
    print("COMPREHENSIVE QUESTIE DATABASE SYNTAX FIXER")
    print("="*60)
    
    files = [
        'Database/Epoch/epochNpcDB.lua',
        'Database/Epoch/epochQuestDB.lua'
    ]
    
    for filepath in files:
        if not Path(filepath).exists():
            print(f"❌ File not found: {filepath}")
            continue
        
        fixer = ComprehensiveDatabaseFixer(filepath)
        fixer.load_file()
        
        if fixer.fix_all_issues():
            fixer.save_file()
            fixer.report()
        
        # Validate structure
        print(f"\n📝 Validating structure...")
        if validate_lua_structure(filepath):
            print("✅ Structure looks good")
        else:
            print("❌ Structure issues remain - manual fix needed")
    
    print("\n" + "="*60)
    print("DONE! Test in-game to verify")
    print("="*60)

if __name__ == "__main__":
    main()