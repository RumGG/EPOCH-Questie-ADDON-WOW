#!/usr/bin/env python3

"""
Comprehensive Database Fixer
Fixes ALL nesting issues in the current epochQuestDB.lua
Rock-solid approach with validation
"""

import re
import os
import shutil
from datetime import datetime

class QuestObjectivesFixer:
    """
    Fixes quest objectives field (position 10) to proper structure
    Proper structure: {creatures, objects, items, reputation, killCredit, spells}
    """
    
    def __init__(self):
        self.fixes_made = 0
        self.quests_fixed = []
        
    def analyze_objectives(self, objectives_str):
        """
        Analyze objectives string to determine its structure
        Returns: (is_valid, issues, suggested_fix)
        """
        issues = []
        
        # Check for quadruple braces
        if '{{{{' in objectives_str:
            issues.append('quadruple_braces')
        
        # Check for triple braces not in proper structure
        if '{{{' in objectives_str:
            # Check if it's a proper 6-element structure
            if not re.search(r'^\{\{\{[^}]+\}\},nil,nil,nil,nil,nil\}$', objectives_str):
                issues.append('improper_triple_braces')
        
        # Check for naked double braces (not wrapped in structure)
        if re.match(r'^\{\{[^{]', objectives_str):
            # This is a double-brace at start, check if it has 6-element structure
            if not objectives_str.count(',nil') >= 5:
                issues.append('unwrapped_objectives')
        
        return len(issues) == 0, issues
    
    def fix_objectives(self, objectives_str):
        """
        Fix objectives string to proper format
        Returns fixed string
        """
        original = objectives_str
        
        # Step 1: Fix quadruple braces (most severe)
        if '{{{{' in objectives_str:
            # Pattern: {{{{creatures}},nil,nil,nil,nil,nil},nil,nil}
            # Fix to: {{{creatures}},nil,nil,nil,nil,nil}
            pattern = r'\{\{\{\{([^}]+(?:\}[^}]*)*?)\}\},nil,nil,nil,nil,nil\},nil,nil\}'
            match = re.search(pattern, objectives_str)
            if match:
                creatures = match.group(1)
                objectives_str = '{{{' + creatures + '}},nil,nil,nil,nil,nil}'
                self.fixes_made += 1
            else:
                # Simple quadruple to double replacement
                objectives_str = objectives_str.replace('{{{{', '{{').replace('}}}}', '}}')
                self.fixes_made += 1
        
        # Step 2: Fix triple braces in items/objects
        # Pattern: ,{{{itemId,count}}} should be ,{{itemId,count}}
        pattern = r',\{\{\{(\d+,\d+(?:,"[^"]*")?)\}\}\}'
        matches = re.findall(pattern, objectives_str)
        for match in matches:
            old = ',{{{' + match + '}}}'
            new = ',{{' + match + '}}'
            objectives_str = objectives_str.replace(old, new)
            if objectives_str != original:
                self.fixes_made += 1
        
        # Step 3: Check if objectives need wrapping
        # If it starts with {{ and doesn't have proper structure
        if objectives_str.startswith('{{') and not objectives_str.startswith('{{{'):
            # Count commas and nils to determine structure
            nil_count = objectives_str.count(',nil')
            
            # If it doesn't have enough nils, it needs wrapping
            if nil_count < 5:
                # This is bare creatures/items, wrap it
                objectives_str = '{' + objectives_str + ',nil,nil,nil,nil,nil}'
                self.fixes_made += 1
        
        return objectives_str
    
    def fix_quest_line(self, line):
        """
        Fix a complete quest line
        Returns: (fixed_line, was_fixed)
        """
        # Skip non-quest lines
        if not (line.strip().startswith('[') and '=' in line):
            return line, False
        
        # Extract quest ID
        quest_match = re.search(r'\[(\d+)\]', line)
        if not quest_match:
            return line, False
        
        quest_id = quest_match.group(1)
        
        # Find objectives field (position 10)
        # Pattern: find the 10th field in the quest structure
        # This is complex due to nested structures
        
        # Split by top-level commas (not inside braces)
        fields = self.split_quest_fields(line)
        
        if len(fields) < 10:
            return line, False
        
        # Check if field 10 (index 9) needs fixing
        objectives = fields[9]
        if objectives and objectives != 'nil':
            is_valid, issues = self.analyze_objectives(objectives)
            
            if not is_valid:
                fixed_objectives = self.fix_objectives(objectives)
                if fixed_objectives != objectives:
                    # Reconstruct the line
                    fields[9] = fixed_objectives
                    # Rebuild the quest line
                    quest_content = self.reconstruct_quest(fields)
                    
                    # Extract quest ID and any comments
                    prefix_match = re.match(r'^(\[\d+\]\s*=\s*\{)', line)
                    suffix_match = re.search(r'(\},.*$)', line)
                    
                    if prefix_match and suffix_match:
                        fixed_line = prefix_match.group(1) + quest_content + suffix_match.group(1)
                    else:
                        fixed_line = line  # Couldn't parse, keep original
                    
                    self.quests_fixed.append(quest_id)
                    return fixed_line, True
        
        return line, False
    
    def split_quest_fields(self, line):
        """
        Split quest line into fields, respecting brace nesting
        """
        # Extract just the quest data (between outer {})
        match = re.search(r'=\s*\{(.*)\},', line)
        if not match:
            return []
        
        content = match.group(1)
        fields = []
        current_field = ''
        brace_depth = 0
        in_string = False
        
        for i, char in enumerate(content):
            if char == '"' and (i == 0 or content[i-1] != '\\'):
                in_string = not in_string
            elif not in_string:
                if char == '{':
                    brace_depth += 1
                elif char == '}':
                    brace_depth -= 1
                elif char == ',' and brace_depth == 0:
                    fields.append(current_field)
                    current_field = ''
                    continue
            
            current_field += char
        
        # Add the last field
        if current_field:
            fields.append(current_field)
        
        return fields
    
    def reconstruct_quest(self, fields):
        """
        Reconstruct quest content from fields
        """
        return ','.join(fields)


def fix_database(input_file, output_file):
    """
    Main function to fix the database
    """
    print("=" * 70)
    print("COMPREHENSIVE DATABASE FIXER")
    print("=" * 70)
    
    # Create backup
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"epochQuestDB_backup_{timestamp}.lua")
    shutil.copy(input_file, backup_file)
    print(f"📁 Created backup: {backup_file}")
    
    # Read input
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Create fixer
    fixer = QuestObjectivesFixer()
    
    # Fix each line
    print("Fixing quest objectives...")
    fixed_lines = []
    
    for line_num, line in enumerate(lines, 1):
        fixed_line, was_fixed = fixer.fix_quest_line(line)
        fixed_lines.append(fixed_line)
        
        if was_fixed and line_num % 10 == 0:
            print(f"  Processing line {line_num}... ({len(fixer.quests_fixed)} quests fixed)")
    
    # Validate
    print("\nValidating fixed database...")
    content = ''.join(fixed_lines)
    
    open_braces = content.count('{')
    close_braces = content.count('}')
    quadruple_count = content.count('{{{{')
    
    print(f"  Brace balance: {open_braces} open, {close_braces} close", end='')
    if open_braces == close_braces:
        print(" ✅")
    else:
        print(f" ❌ (diff: {open_braces - close_braces})")
    
    print(f"  Quadruple braces: {quadruple_count}", end='')
    if quadruple_count == 0:
        print(" ✅")
    else:
        print(" ❌")
    
    # Write output
    if open_braces == close_braces:
        print(f"\nWriting {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        
        print(f"\n✅ SUCCESS!")
        print(f"  Fixed {fixer.fixes_made} issues in {len(fixer.quests_fixed)} quests")
        print(f"  Output: {output_file}")
        
        if fixer.quests_fixed:
            print(f"\n  Fixed quests: {', '.join(fixer.quests_fixed[:20])}", end='')
            if len(fixer.quests_fixed) > 20:
                print(f" ... and {len(fixer.quests_fixed)-20} more")
            else:
                print()
    else:
        print("\n❌ Brace imbalance detected, not writing output")
        print("  Manual intervention required")
    
    return len(fixer.quests_fixed)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) == 1:
        # Default files
        input_file = "../Database/Epoch/epochQuestDB.lua"
        output_file = "../Database/Epoch/epochQuestDB_FIXED.lua"
    elif len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print("Usage: python comprehensive_fixer.py [input.lua output.lua]")
        sys.exit(1)
    
    fix_database(input_file, output_file)