#!/usr/bin/env python3

"""
Careful nesting fix that preserves quest structure integrity
Only fixes the specific nesting patterns without breaking other syntax
"""

import re

def careful_nesting_fix():
    """Apply nesting fixes while preserving structure"""
    
    with open("Database/Epoch/epochQuestDB_CLEAN_START.lua", 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes_made = 0
    issues_fixed = []
    
    # Process line by line to maintain structure integrity
    lines = content.split('\n')
    fixed_lines = []
    
    for line_num, line in enumerate(lines, 1):
        original_line = line
        
        # Only process quest lines
        if not (line.strip().startswith('[') and '=' in line):
            fixed_lines.append(line)
            continue
        
        # Extract quest ID for reporting
        quest_match = re.search(r'\[(\d+)\]', line)
        quest_id = quest_match.group(1) if quest_match else "unknown"
        
        # Fix 1: Simple quadruple nesting in objectives
        # {{{{40,1},{476,1}}}} -> {{{40,1},{476,1}}}
        if '{{{{' in line and '}}}}' in line:
            # Count occurrences to be precise
            before_quad = line.count('{{{{')
            before_quad_close = line.count('}}}}')
            
            line = line.replace('{{{{', '{{{')
            line = line.replace('}}}}', '}}}')
            
            if before_quad > 0:
                issues_fixed.append(f"Quest {quest_id}: Fixed {before_quad} quadruple nesting patterns")
                fixes_made += before_quad
        
        # Fix 2: Simple triple nesting for items
        # {{{782,1}}} -> {{782,1}} (but only in items position)
        # Pattern: ,nil,{{{number,number}}} (items field)
        items_pattern = r',nil,\{\{\{(\d+,\d+[^}]*)\}\}\}'
        if re.search(items_pattern, line):
            line = re.sub(items_pattern, r',nil,{{\1}}', line)
            issues_fixed.append(f"Quest {quest_id}: Fixed triple nesting in items field")
            fixes_made += 1
        
        # Fix 3: Triple nesting with text/names (be more specific)
        # {{{782,1,"name"}}} -> {{782,1,"name"}} in items position
        items_with_text_pattern = r',nil,\{\{\{(\d+,\d+[^}]*"[^"]*"[^}]*)\}\}\}'
        if re.search(items_with_text_pattern, line):
            line = re.sub(items_with_text_pattern, r',nil,{{\1}}', line)
            issues_fixed.append(f"Quest {quest_id}: Fixed triple nesting with text in items field")
            fixes_made += 1
        
        fixed_lines.append(line)
    
    # Reconstruct content
    fixed_content = '\n'.join(fixed_lines)
    
    with open("Database/Epoch/epochQuestDB_CAREFUL_FIX.lua", 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"🎯 Careful nesting fixes applied!")
    print(f"   Total fixes: {fixes_made}")
    print(f"   Output: epochQuestDB_CAREFUL_FIX.lua")
    
    if issues_fixed:
        print(f"\n📋 Issues fixed:")
        for issue in issues_fixed[:10]:
            print(f"  {issue}")
        if len(issues_fixed) > 10:
            print(f"  ... and {len(issues_fixed) - 10} more")
    
    # Validate syntax
    print(f"\n🧪 Syntax validation:")
    open_braces = fixed_content.count('{')
    close_braces = fixed_content.count('}')
    print(f"  Braces: {open_braces} open, {close_braces} close")
    
    if open_braces == close_braces:
        print("  ✅ Braces balanced")
    else:
        print(f"  ❌ Brace imbalance: {open_braces - close_braces}")
    
    # Check specific problem quests
    print(f"\n🔍 Checking problem quests:")
    for target_quest in [11, 76]:
        for line in fixed_content.split('\n'):
            if f'[{target_quest}]' in line:
                # Extract objectives
                obj_match = re.search(r'nil,(\{[^}]*(?:\{[^}]*\}[^}]*)*\}),nil', line)
                if obj_match:
                    print(f"  Quest {target_quest}: {obj_match.group(1)[:60]}...")
                break
    
    # Check for remaining problematic patterns
    remaining_quad = fixed_content.count('{{{{')
    remaining_items_triple = len(re.findall(r',nil,\{\{\{\d+,\d+', fixed_content))
    
    print(f"  Remaining quadruple nesting: {remaining_quad}")
    print(f"  Remaining items triple nesting: {remaining_items_triple}")
    
    return fixes_made

if __name__ == "__main__":
    fixes = careful_nesting_fix()
    print(f"\n🎉 Applied {fixes} careful nesting fixes!")