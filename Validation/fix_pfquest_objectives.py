#!/usr/bin/env python3

"""
Fix pfQuest objectives that have incorrect triple-brace structure for objects
The pattern {{{objectId,count}}} should be {{objectId,count}}
"""

import re

def fix_pfquest_objectives():
    """Fix triple-brace objects in pfQuest data"""
    
    with open("pfquest_objectives_v2.lua", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Count issues before fixing
    triple_brace_count = len(re.findall(r'\{\{\{[0-9]+,[0-9]+\}\}\}', content))
    print(f"Found {triple_brace_count} triple-brace object patterns to fix")
    
    # Fix the pattern: {{{id,count}}} -> {{id,count}}
    # This specifically targets objects field which has the issue
    fixed_content = re.sub(
        r',\{\{\{([0-9]+,[0-9]+)\}\}\}',  # Match ,{{{digits,digits}}}
        r',{{\1}}',                        # Replace with ,{{digits,digits}}
        content
    )
    
    # Also fix when it's at the beginning of objects field
    fixed_content = re.sub(
        r'\{nil,\{\{\{([0-9]+,[0-9]+)\}\}\}',  # Match {nil,{{{digits,digits}}}
        r'{nil,{{\1}}',                          # Replace with {nil,{{digits,digits}}
        fixed_content
    )
    
    # Fix quadruple braces too: {{{{id,count}}}} -> {{id,count}}
    fixed_content = re.sub(
        r'\{\{\{\{([0-9]+,[0-9]+)\}\}\}\}',  # Match {{{{digits,digits}}}}
        r'{{\1}}',                            # Replace with {{digits,digits}}
        fixed_content
    )
    
    # Count issues after fixing
    remaining_issues = len(re.findall(r'\{\{\{[0-9]+,[0-9]+\}\}\}', fixed_content))
    remaining_quad = len(re.findall(r'\{\{\{\{[0-9]+,[0-9]+\}\}\}\}', fixed_content))
    print(f"Remaining triple-brace patterns: {remaining_issues}")
    print(f"Remaining quadruple-brace patterns: {remaining_quad}")
    
    # Save fixed version
    with open("pfquest_objectives_v2_fixed.lua", 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print(f"✅ Fixed pfQuest data saved to pfquest_objectives_v2_fixed.lua")
    
    # Show a few examples of fixes
    print("\nExamples of fixes made:")
    
    # Find quest 26763 as an example
    for line in fixed_content.split('\n'):
        if '[26763]' in line:
            print(f"Quest 26763: {line[:200]}...")
            break
    
    return triple_brace_count - remaining_issues

if __name__ == "__main__":
    fixes_made = fix_pfquest_objectives()
    print(f"\nTotal fixes made: {fixes_made}")