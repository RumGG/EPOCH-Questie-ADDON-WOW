#!/usr/bin/env python3
"""
Fix ALL missing commas in Questie database files at once.
This will prevent the endless syntax error debugging cycle.
"""

import re
import sys

def fix_database_commas(filename):
    """Fix all missing commas in a database file."""
    
    print(f"\nProcessing {filename}...")
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixed_lines = []
    inside_table = False
    fixes_made = 0
    
    for i, line in enumerate(lines, 1):
        # Track if we're inside the main table
        if 'epochNpcData = {' in line or 'epochQuestData = {' in line:
            inside_table = True
        elif line.strip() == '}' and inside_table:
            inside_table = False
        
        # Fix lines that need commas
        if inside_table and re.match(r'^\[\d+\] = \{.*\}', line.strip()):
            # Check if it ends with } but not },
            if not line.rstrip().endswith('},'):
                # Add comma before newline (preserving comments)
                if '--' in line:
                    # Has a comment - add comma before comment
                    line = re.sub(r'\}(\s*)(--.*)?$', r'},\1\2', line)
                else:
                    # No comment - just add comma
                    line = line.rstrip() + ',\n'
                fixes_made += 1
                print(f"  Fixed line {i}: Added missing comma")
        
        fixed_lines.append(line)
    
    if fixes_made > 0:
        # Write the fixed file
        with open(filename, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
        print(f"  ✓ Fixed {fixes_made} missing commas")
    else:
        print(f"  ✓ No missing commas found")
    
    return fixes_made

def check_other_issues(filename):
    """Check for other common syntax issues."""
    
    issues = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    inside_table = False
    table_closed = False
    
    for i, line in enumerate(lines, 1):
        # Track table state
        if 'epochNpcData = {' in line or 'epochQuestData = {' in line:
            inside_table = True
            table_closed = False
        elif line.strip() == '}' and inside_table:
            inside_table = False
            table_closed = True
        
        # Check for prefix inside table
        if inside_table:
            if re.match(r'^epochNpcData\[\d+\]', line) or re.match(r'^epochQuestData\[\d+\]', line):
                issues.append(f"Line {i}: Entry has table name prefix inside table")
        
        # Check for entries outside table
        if table_closed:
            if re.match(r'^epochNpcData\[\d+\]', line) or re.match(r'^epochQuestData\[\d+\]', line):
                issues.append(f"Line {i}: Entry added OUTSIDE table (after closing brace)")
            elif re.match(r'^\[\d+\] = \{', line):
                issues.append(f"Line {i}: Entry found after table closed - may need to be moved inside")
    
    if issues:
        print(f"\nOther issues found in {filename}:")
        for issue in issues[:10]:  # Show first 10
            print(f"  ⚠️  {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more issues")
    
    return issues

def main():
    """Main function to fix all database files."""
    
    print("=" * 60)
    print("Questie Database Syntax Fixer")
    print("=" * 60)
    
    files = [
        'Database/Epoch/epochNpcDB.lua',
        'Database/Epoch/epochQuestDB.lua'
    ]
    
    total_fixes = 0
    total_issues = []
    
    for filename in files:
        try:
            fixes = fix_database_commas(filename)
            total_fixes += fixes
            
            issues = check_other_issues(filename)
            total_issues.extend(issues)
            
        except FileNotFoundError:
            print(f"  ❌ File not found: {filename}")
        except Exception as e:
            print(f"  ❌ Error processing {filename}: {e}")
    
    print("\n" + "=" * 60)
    print("Summary:")
    print(f"  Total commas fixed: {total_fixes}")
    print(f"  Other issues found: {len(total_issues)}")
    
    if total_fixes == 0 and len(total_issues) == 0:
        print("\n✅ All database files are clean!")
    else:
        print("\n⚠️  Review the changes and test in-game")
        if total_issues:
            print("  Some issues require manual fixing (see above)")

if __name__ == "__main__":
    main()