#!/usr/bin/env python3

"""
Comprehensive fix for ALL string issues in pfQuest data
Handles various edge cases and malformed strings
"""

import re

def comprehensive_string_fix():
    """Fix all possible string issues in pfQuest entries"""
    
    with open("Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_made = 0
    issues_found = []
    
    # Process line by line for better error reporting
    lines = content.split('\n')
    fixed_lines = []
    
    for line_num, line in enumerate(lines, 1):
        original_line = line
        
        # Only process pfQuest entries
        if not ('From pfQuest' in line and line.strip().startswith('[')):
            fixed_lines.append(line)
            continue
        
        # Extract quest ID for reporting
        quest_match = re.search(r'\[(\d+)\]', line)
        quest_id = quest_match.group(1) if quest_match else "unknown"
        
        # Fix 1: Completely empty objective strings {"\\"}
        if '{"\\"}' in line:
            line = line.replace('{"\\"}', '{"Complete the quest."}')
            issues_found.append(f"Quest {quest_id}: Fixed empty escaped string")
            fixes_made += 1
        
        # Fix 2: Strings that end with just a backslash quote
        if re.search(r'{"[^"]*\\"}', line):
            line = re.sub(r'{"([^"]*?)\\"}', r'{"\1."}', line)
            issues_found.append(f"Quest {quest_id}: Fixed string ending with backslash")
            fixes_made += 1
        
        # Fix 3: Truncated strings (ending with " to \")
        if re.search(r'{"[^"]*to \\"}', line):
            line = re.sub(r'{"([^"]*to )\\"}', r'{"\1[NPC]."}', line)
            issues_found.append(f"Quest {quest_id}: Fixed truncated 'to' string")
            fixes_made += 1
        
        # Fix 4: Empty strings {""}
        if '{""}' in line:
            line = line.replace('{""}', '{"Complete the quest."}')
            issues_found.append(f"Quest {quest_id}: Fixed completely empty string")
            fixes_made += 1
        
        # Fix 5: Strings with unescaped quotes inside
        # Look for patterns like {"text"text"} which should be {"text\"text"}
        problematic_quotes = re.findall(r'{"[^"]*"[^"]*"}', line)
        for match in problematic_quotes:
            # Skip if it's properly escaped already
            if '\\"' not in match:
                # This is a problematic unescaped quote - replace with simple text
                line = line.replace(match, '{"Complete the quest."}')
                issues_found.append(f"Quest {quest_id}: Fixed unescaped quotes in string")
                fixes_made += 1
        
        # Fix 6: Strings that are just whitespace or punctuation
        whitespace_pattern = r'{"[\s\.,;:!?]*"}'
        if re.search(whitespace_pattern, line):
            line = re.sub(whitespace_pattern, '{"Complete the quest."}', line)
            issues_found.append(f"Quest {quest_id}: Fixed whitespace-only string")
            fixes_made += 1
        
        # Fix 7: WoW formatting codes that break strings
        wow_codes = ['$B', '$N', '$C', '$R', '$G']
        for code in wow_codes:
            if code in line:
                line = line.replace(code, ' ')
                issues_found.append(f"Quest {quest_id}: Removed WoW formatting code {code}")
                fixes_made += 1
        
        # Fix 8: Newline characters that break strings
        if '\\n' in line:
            line = line.replace('\\n', ' ')
            issues_found.append(f"Quest {quest_id}: Fixed newline characters")
            fixes_made += 1
        
        # Fix 9: Multiple spaces (cleanup)
        if re.search(r'{\s*"\s+', line):
            line = re.sub(r'{"(\s+)', r'{"', line)  # Remove leading spaces in strings
            line = re.sub(r'(\s+)"}', r'"}', line)  # Remove trailing spaces in strings
            line = re.sub(r'\s+', ' ', line)       # Collapse multiple spaces
            issues_found.append(f"Quest {quest_id}: Cleaned up extra spaces")
            fixes_made += 1
        
        # Final validation: ensure the line doesn't end with malformed strings
        if re.search(r'{"[^"]*"[^}]*$', line):  # String that doesn't close properly
            # Extract quest info and create a safe replacement
            base_pattern = r'(\[[0-9]+\]\s*=\s*\{[^{]*),\{[^}]*$'
            if re.search(base_pattern, line):
                line = re.sub(r',\{[^}]*$', ',{"Complete the quest."}', line)
                if not line.endswith('}, -- From pfQuest'):
                    line = line.rstrip() + '}, -- From pfQuest'
                issues_found.append(f"Quest {quest_id}: Fixed malformed line ending")
                fixes_made += 1
        
        fixed_lines.append(line)
    
    # Reconstruct the content
    fixed_content = '\n'.join(fixed_lines)
    
    # Write fixed version
    with open("Database/Epoch/epochQuestDB_COMPREHENSIVE_FIX.lua", 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"🔧 Comprehensive string fixes applied!")
    print(f"   Total fixes: {fixes_made}")
    print(f"   Output: epochQuestDB_COMPREHENSIVE_FIX.lua")
    
    if issues_found:
        print(f"\n📋 Issues fixed:")
        # Group by type
        issue_types = {}
        for issue in issues_found:
            issue_type = issue.split(': ', 1)[1] if ': ' in issue else issue
            issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
        
        for issue_type, count in issue_types.items():
            print(f"  {count}x {issue_type}")
    
    # Validation
    print(f"\n🧪 Validation:")
    open_braces = fixed_content.count('{')
    close_braces = fixed_content.count('}')
    open_quotes = fixed_content.count('"')
    
    print(f"  Braces: {open_braces} open, {close_braces} close")
    print(f"  Quotes: {open_quotes}")
    
    if open_braces == close_braces:
        print("  ✅ Braces balanced")
    else:
        print(f"  ❌ Brace imbalance: {open_braces - close_braces}")
    
    if open_quotes % 2 == 0:
        print("  ✅ Quotes balanced")
    else:
        print("  ❌ Unmatched quotes")
    
    # Check for remaining problematic patterns
    problems = []
    if '{"\\"}' in fixed_content:
        problems.append("Empty escaped strings")
    if re.search(r'{"[^"]*\\"}', fixed_content):
        problems.append("Strings ending with backslash")
    if '{""}' in fixed_content:
        problems.append("Empty strings")
    
    if problems:
        print(f"  ⚠️  Remaining: {', '.join(problems)}")
    else:
        print("  ✅ No obvious problems detected")
    
    return fixes_made

if __name__ == "__main__":
    fixes = comprehensive_string_fix()
    print(f"\n🎉 Applied {fixes} comprehensive fixes to pfQuest strings!")