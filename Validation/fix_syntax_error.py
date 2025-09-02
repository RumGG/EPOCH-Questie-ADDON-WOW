#!/usr/bin/env python3

"""
Fix syntax errors in epochQuestDB.lua
"""

def fix_syntax_errors():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Fix double closing braces at end of quest lines
        if line.strip().endswith('}}, -- ') or '}}, --' in line:
            # This should be }, --
            line = line.replace('}}, --', '}, --')
            fixes_made += 1
            print(f"Line {i+1}: Fixed double closing brace")
            
        # Fix other syntax patterns
        if line.strip().endswith('}}'):
            if not line.strip().endswith('{}}') and not '{{' in line[-20:]:
                # This might be a quest line ending with }} instead of },
                line = line.replace('}}\n', '},\n')
                fixes_made += 1
                print(f"Line {i+1}: Fixed quest line ending")
        
        if line != original_line:
            lines[i] = line
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes_made} syntax errors')

if __name__ == "__main__":
    fix_syntax_errors()