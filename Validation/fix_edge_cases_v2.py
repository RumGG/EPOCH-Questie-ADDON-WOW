#!/usr/bin/env python3

"""
Edge Case Fixer V2 - Properly fixes the 24 quests with triple-brace issues
These quests have creatures directly triple-braced without the 6-element wrapper
"""

import re
import os
import shutil
from datetime import datetime

# List of quests with known issues from test report
# Updated with additional quests found during testing
PROBLEM_QUESTS = [
    26766, 26769, 26939, 26282, 26723, 28768, 26890, 26292, 27273, 26684,
    26685, 27221, 27224, 26849, 27339, 27342, 27345, 27374, 27396, 27417,
    27419, 27468, 27469, 27509,
    # Additional quests found in second pass
    27299, 26817, 26208, 27037, 26597, 28764, 28765, 27208, 26892, 27204
]

class EdgeCaseFixerV2:
    """Fixes specific edge cases in quest objectives"""
    
    def __init__(self):
        self.fixes_made = 0
        self.quests_fixed = []
        self.debug_mode = True
    
    def fix_unwrapped_creatures(self, objectives_str):
        """
        Fix triple-braced creatures that lack the 6-element wrapper
        Pattern: {{{id,count}}} or {{{id,"name"}}}
        Should be: {{{{id,count}},nil,nil,nil,nil,nil}}
        """
        if not objectives_str.startswith('{{{'):
            return objectives_str, False
        
        # Check if it already has the 6-element structure
        if ',nil,nil,nil,nil,nil}' in objectives_str:
            return objectives_str, False  # Already correct
        
        # It's a bare triple-braced creature, needs wrapping
        # Remove outer braces to get the creature part
        inner = objectives_str[1:-1]  # Remove outer { }
        
        # Wrap it properly: creatures go in position 1 of 6-element structure
        fixed = '{' + inner + ',nil,nil,nil,nil,nil}'
        
        if self.debug_mode:
            print(f"    Wrapping unwrapped creature objectives")
            print(f"      From: {objectives_str}")
            print(f"      To:   {fixed}")
        
        return fixed, True
    
    def fix_quest_line(self, line, quest_id):
        """
        Fix a specific quest line based on its ID
        """
        # Skip if not a target quest
        if quest_id not in PROBLEM_QUESTS:
            return line, False
        
        # Extract the quest structure - include newline in suffix
        match = re.search(r'(\[' + str(quest_id) + r'\]\s*=\s*\{)(.*?)(\},(?:\s*--[^\n]*)?\n?$)', line, re.DOTALL)
        if not match:
            return line, False
        
        prefix = match.group(1)
        content = match.group(2)
        suffix = match.group(3)
        
        # Split content into fields
        fields = self.split_fields(content)
        
        if len(fields) < 10:
            if self.debug_mode:
                print(f"  Quest {quest_id}: Not enough fields ({len(fields)})")
            return line, False
        
        # Check field 10 (index 9) - objectives
        objectives = fields[9] if len(fields) > 9 else None
        
        if objectives and objectives != 'nil':
            # Apply fixes for unwrapped creatures
            fixed_objectives, changed = self.fix_unwrapped_creatures(objectives)
            
            if changed:
                fields[9] = fixed_objectives
                # Rebuild the line
                fixed_content = ','.join(fields)
                # Ensure we keep the newline if it was there
                if not suffix.endswith('\n') and line.endswith('\n'):
                    suffix += '\n'
                fixed_line = prefix + fixed_content + suffix
                
                if self.debug_mode:
                    print(f"  ✅ Fixed quest {quest_id}")
                
                self.quests_fixed.append(quest_id)
                self.fixes_made += 1
                return fixed_line, True
        
        return line, False
    
    def split_fields(self, content):
        """Split quest content into fields, respecting nesting"""
        fields = []
        current = ''
        depth = 0
        in_string = False
        
        for i, char in enumerate(content):
            if char == '"' and (i == 0 or content[i-1] != '\\'):
                in_string = not in_string
            elif not in_string:
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                elif char == ',' and depth == 0:
                    fields.append(current)
                    current = ''
                    continue
            
            current += char
        
        if current:
            fields.append(current)
        
        return fields
    
    def process_file(self, input_file, output_file):
        """Process the entire file"""
        print(f"Processing {input_file}...")
        
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, f"epochQuestDB_edge_v2_backup_{timestamp}.lua")
        shutil.copy(input_file, backup_file)
        print(f"📁 Created backup: {backup_file}")
        
        # Read input
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Process each line
        fixed_lines = []
        
        for line_num, line in enumerate(lines, 1):
            # Skip non-quest lines
            if not (line.strip().startswith('[') and '=' in line):
                fixed_lines.append(line)
                continue
            
            # Extract quest ID
            quest_match = re.search(r'\[(\d+)\]', line)
            if not quest_match:
                fixed_lines.append(line)
                continue
            
            quest_id = int(quest_match.group(1))
            
            # Try to fix if it's a problem quest
            fixed_line, was_fixed = self.fix_quest_line(line, quest_id)
            fixed_lines.append(fixed_line)
        
        # Validate
        content = ''.join(fixed_lines)
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        print(f"\nValidation:")
        print(f"  Fixed {self.fixes_made} quests")
        print(f"  Brace balance: {open_braces} open, {close_braces} close", end='')
        
        if open_braces == close_braces:
            print(" ✅")
            
            # Write output
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            
            print(f"\n✅ Success! Output written to {output_file}")
            
            if self.quests_fixed:
                print(f"\nFixed quests: {', '.join(map(str, self.quests_fixed))}")
            
            return True
        else:
            print(f" ❌ (diff: {open_braces - close_braces})")
            print("⚠️  Not writing output due to brace imbalance")
            return False


def main():
    """Main function"""
    print("=" * 70)
    print("EDGE CASE FIXER V2")
    print("=" * 70)
    print(f"Targeting {len(PROBLEM_QUESTS)} specific quests with unwrapped creatures\n")
    
    fixer = EdgeCaseFixerV2()
    
    # Default files
    input_file = "../Database/Epoch/epochQuestDB.lua"
    output_file = "../Database/Epoch/epochQuestDB_EDGE_FIXED_V2.lua"
    
    # Process
    success = fixer.process_file(input_file, output_file)
    
    if success:
        print("\n" + "=" * 70)
        print("NEXT STEPS:")
        print("=" * 70)
        print("1. Test the fixed file:")
        print(f"   python3 test_framework.py {output_file}")
        print("\n2. If tests pass, apply the fix:")
        print(f"   cp {output_file} {input_file}")
        print("\n3. Restart WoW completely and test")
    
    return 0 if success else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())