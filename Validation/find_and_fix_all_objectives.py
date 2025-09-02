#!/usr/bin/env python3

"""
Find and fix ALL remaining objectives structure issues
No more whack-a-mole - fix them all at once!
"""

import re

def fix_all_objectives():
    """Find and fix all problematic objectives structures"""
    
    with open("Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_made = 0
    quest_fixes = []
    
    # Split into lines for processing
    lines = content.split('\\n')
    fixed_lines = []
    
    for line_num, line in enumerate(lines, 1):
        original_line = line
        
        # Only process quest lines
        if not (line.strip().startswith('[') and '=' in line):
            fixed_lines.append(line)
            continue
        
        # Get quest ID for reporting
        quest_match = re.search(r'\\[(\\d+)\\]', line)
        quest_id = quest_match.group(1) if quest_match else f"line {line_num}"
        
        line_changed = False
        
        # Pattern 1: Simple objectives that need full structure
        # },nil,{{...}},nil,nil,nil,nil,nil,nil -> },nil,{{{...}},nil,nil,nil,nil,nil},nil,nil,nil,nil,nil,nil
        pattern1 = r'},nil,(\\{\\{[^}]+(?:\\}[^}]*)*?\\}\\}),nil,nil,nil,nil,nil,nil'
        if re.search(pattern1, line):
            line = re.sub(pattern1, r'},nil,{\\1,nil,nil,nil,nil,nil},nil,nil,nil,nil,nil,nil', line)
            quest_fixes.append(f"Quest {quest_id}: fixed simple objectives (pattern 1)")
            fixes_made += 1
            line_changed = True
        
        # Pattern 2: Mixed objectives (creatures + items)
        # },nil,{{...}},nil,{{...}},nil,nil,nil,nil,nil -> },nil,{{{...}},nil,{{...}},nil,nil,nil},nil,nil,nil,nil,nil,nil
        elif '},nil,' in line and not line_changed:
            # Look for creatures followed by items
            pattern2 = r'},nil,(\\{\\{[^}]+(?:\\}[^}]*)*?\\}\\}),nil,(\\{\\{[^}]+(?:\\}[^}]*)*?\\}\\}),nil,nil,nil,nil,nil'
            if re.search(pattern2, line):
                line = re.sub(pattern2, r'},nil,{\\1,nil,\\2,nil,nil,nil},nil,nil,nil,nil,nil,nil', line)
                quest_fixes.append(f"Quest {quest_id}: fixed mixed objectives (creatures + items)")
                fixes_made += 1
                line_changed = True
        
        # Pattern 3: Simple case that ends with just },nil,nil
        # },nil,{{...}},nil,nil -> },nil,{{{...}},nil,nil,nil,nil,nil},nil,nil  
        if not line_changed and '},nil,' in line:
            pattern3 = r'},nil,(\\{\\{[^}]+(?:\\}[^}]*)*?\\}\\}),nil,nil'
            if re.search(pattern3, line) and not re.search(r'},nil,\\{\\{[^}]+\\}\\},nil,\\{\\{[^}]+\\}\\},nil', line):
                line = re.sub(pattern3, r'},nil,{\\1,nil,nil,nil,nil,nil},nil,nil', line)
                quest_fixes.append(f"Quest {quest_id}: fixed simple objectives (pattern 3)")
                fixes_made += 1
                line_changed = True
        
        fixed_lines.append(line)
    
    # Write back
    fixed_content = '\\n'.join(fixed_lines)
    
    with open("Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"🔧 Fixed {fixes_made} objectives structures")
    
    if quest_fixes:
        print(f"\\n📋 Sample fixes:")
        for fix in quest_fixes[:15]:
            print(f"  {fix}")
        if len(quest_fixes) > 15:
            print(f"  ... and {len(quest_fixes) - 15} more")
    
    # Verify final state
    remaining_patterns = len(re.findall(r'},nil,\\{\\{[^}]+\\}\\},', fixed_content))
    print(f"\\n   Remaining problematic patterns: {remaining_patterns}")
    
    # Check brace balance
    open_braces = fixed_content.count('{')
    close_braces = fixed_content.count('}')
    print(f"   Braces: {open_braces} open, {close_braces} close")
    
    if open_braces == close_braces:
        print("   ✅ Braces balanced")
    else:
        print(f"   ⚠️  Brace imbalance: {open_braces - close_braces}")
    
    return fixes_made

if __name__ == "__main__":
    print("🔍 Scanning for ALL objectives structure issues...")
    fixes = fix_all_objectives()
    print(f"\\n🎉 Fixed {fixes} objectives - no more whack-a-mole!")