#!/usr/bin/env python3

"""
Fix lines that have extra closing braces at the end (nil}} instead of nil})
"""

def fix_extra_braces():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    fixes_made = 0
    
    for i, line in enumerate(lines):
        if not line.strip().startswith('[') or '=' not in line:
            continue
            
        if line.strip().startswith('--'):
            continue
        
        # Look for lines ending with nil}} (extra brace)
        if ',nil}},' in line or line.strip().endswith(',nil}}'):
            original = line
            # Replace nil}} with nil}
            line = line.replace('nil}}', 'nil}')
            
            # Make sure we didn't break nested structures
            # Count opening and closing braces
            open_count = line.count('{')
            close_count = line.count('}')
            
            # For a proper quest line, opens should equal closes
            if open_count == close_count:
                lines[i] = line
                fixes_made += 1
                # Extract quest ID for logging
                import re
                match = re.search(r'\[(\d+)\]', line)
                if match:
                    print(f"Fixed quest {match.group(1)}: removed extra closing brace")
    
    # Write back
    with open("../Database/Epoch/epochQuestDB.lua", 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f'\n✅ Fixed {fixes_made} quests with extra closing braces')

if __name__ == "__main__":
    fix_extra_braces()