#!/usr/bin/env python3

"""
Check bracket balance in the quest database file
"""

def check_brackets():
    with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    bracket_stack = []
    
    for i, line in enumerate(lines, 1):
        # Skip comments and empty lines
        if line.strip().startswith('--') or not line.strip():
            continue
            
        for char in line:
            if char == '{':
                bracket_stack.append(('{', i))
            elif char == '}':
                if not bracket_stack:
                    print(f"❌ Extra closing brace at line {i}")
                    print(f"   Line: {line.strip()[:100]}")
                    return False
                opener, opener_line = bracket_stack.pop()
                if opener != '{':
                    print(f"❌ Mismatched bracket at line {i}")
                    return False
    
    if bracket_stack:
        print(f"❌ Unclosed brackets:")
        for bracket, line_num in bracket_stack[-5:]:  # Show last 5
            print(f"   {bracket} opened at line {line_num}")
            # Show the actual line
            with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if line_num <= len(lines):
                    print(f"   Content: {lines[line_num-1].strip()[:100]}")
        return False
    
    print("✅ All brackets are balanced!")
    return True

if __name__ == "__main__":
    check_brackets()