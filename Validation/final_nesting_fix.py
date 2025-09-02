#!/usr/bin/env python3

"""
Final comprehensive fix for ALL nesting issues
Uses brute force approach to ensure every quest has correct nesting
"""

import re

def final_nesting_fix():
    """Fix ALL remaining nesting issues comprehensively"""
    
    with open("Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_made = 0
    
    # Keep fixing until no more patterns are found
    while True:
        before_fixes = fixes_made
        
        # Fix 1: Any quadruple nesting {{{{ -> {{{
        count_before = content.count('{{{{')
        content = content.replace('{{{{', '{{{')
        fixes_made += count_before
        
        # Fix 2: Any quadruple closing }}}} -> }}}
        count_before = content.count('}}}}')  
        content = content.replace('}}}}', '}}}')
        fixes_made += count_before
        
        # Fix 3: Quintuple nesting {{{{{ -> {{{
        count_before = content.count('{{{{{')
        content = content.replace('{{{{{', '{{{')
        fixes_made += count_before
        
        # Fix 4: Quintuple closing }}}}} -> }}}
        count_before = content.count('}}}}}')
        content = content.replace('}}}}}', '}}}')
        fixes_made += count_before
        
        # Fix 5: Any sextuple or higher nesting
        for i in range(6, 20):  # Handle up to 20 levels of nesting
            pattern = '{' * i
            if pattern in content:
                content = content.replace(pattern, '{{{')
                fixes_made += 1
            
            pattern = '}' * i  
            if pattern in content:
                content = content.replace(pattern, '}}}')
                fixes_made += 1
        
        # If no changes were made in this iteration, we're done
        if fixes_made == before_fixes:
            break
    
    # Now fix specific problematic patterns in objectives
    lines = content.split('\n')
    fixed_lines = []
    
    for line_num, line in enumerate(lines, 1):
        if not (line.strip().startswith('[') and '=' in line):
            fixed_lines.append(line)
            continue
        
        # Extract quest ID
        quest_match = re.search(r'\[(\d+)\]', line)
        quest_id = quest_match.group(1) if quest_match else "unknown"
        
        # For objectives field (position 10), ensure proper nesting
        # Pattern: look for objectives that still have improper nesting
        
        # Fix items field specifically: ,nil,{{{...}}} -> ,nil,{{...}}
        if ',nil,{{{' in line and '}}}' in line:
            # Find the items field and fix it
            items_pattern = r',nil,\{\{\{([^}]+(?:\}[^}]*)*?)\}\}\}'
            line = re.sub(items_pattern, r',nil,{{\1}}', line)
            fixes_made += 1
        
        # Fix creatures field: {{{...}}} at start of objectives -> {{...}}
        obj_start_pattern = r'nil,\{\{\{([^}]+(?:\}[^}]*)*?)\}\}\},nil,nil'
        if re.search(obj_start_pattern, line):
            line = re.sub(obj_start_pattern, r'nil,{{{\1}}},nil,nil', line)
            fixes_made += 1
        
        fixed_lines.append(line)
    
    content = '\n'.join(fixed_lines)
    
    # Write the final fixed version
    with open("Database/Epoch/epochQuestDB_FINAL_NESTING_FIX.lua", 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"🔨 Final comprehensive nesting fixes applied!")
    print(f"   Total fixes: {fixes_made}")
    print(f"   Output: epochQuestDB_FINAL_NESTING_FIX.lua")
    
    # Validation
    print(f"\n🧪 Final validation:")
    
    open_braces = content.count('{')
    close_braces = content.count('}')
    print(f"  Braces: {open_braces} open, {close_braces} close")
    
    if open_braces == close_braces:
        print("  ✅ Braces balanced")
    else:
        print(f"  ❌ Brace imbalance: {open_braces - close_braces}")
    
    # Check for remaining problematic patterns
    issues = []
    for pattern, name in [
        ('{{{{', 'quadruple nesting'),
        ('}}}}', 'quadruple closing'),
        ('{{{{{', 'quintuple nesting'),
        ('}}}}}', 'quintuple closing'),
        (',nil,{{{', 'triple items nesting')
    ]:
        count = content.count(pattern)
        if count > 0:
            issues.append(f"{count} {name}")
    
    if issues:
        print(f"  ⚠️  Remaining issues: {', '.join(issues)}")
    else:
        print("  ✅ No remaining nesting issues!")
    
    # Check specific problem quests
    print(f"\n🔍 Checking problem quests:")
    for target_quest in [11, 76]:
        for line in content.split('\n'):
            if f'[{target_quest}]' in line and '=' in line:
                # Show just the objectives part
                obj_match = re.search(r'nil,(\{[^}]*(?:\{[^}]*\}[^}]*)*\}),nil', line)
                if obj_match:
                    obj_str = obj_match.group(1)
                    print(f"  Quest {target_quest} objectives: {obj_str[:80]}...")
                break
    
    return fixes_made

if __name__ == "__main__":
    fixes = final_nesting_fix()
    print(f"\n🎉 Applied {fixes} final nesting fixes!")