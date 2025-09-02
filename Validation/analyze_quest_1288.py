#!/usr/bin/env python3

import re

with open("../Database/Epoch/epochQuestDB.lua", 'r', encoding='utf-8') as f:
    lines = f.readlines()

for line in lines:
    if '[1288]' in line:
        print("Found quest 1288:")
        print(line)
        
        # Extract the quest data
        match = re.search(r'\[1288\] = \{(.*)\},', line)
        if match:
            data = '{' + match.group(1) + '}'
            # Split by commas but be careful with nested structures
            # Count the fields
            field_count = 1
            depth = 0
            for char in data:
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                elif char == ',' and depth == 1:
                    field_count += 1
            
            print(f"Total fields: {field_count}")
            
            # Find position 18
            parts = []
            current = ""
            depth = 0
            for char in data[1:-1]:  # Skip outer braces
                if char == '{':
                    depth += 1
                    current += char
                elif char == '}':
                    depth -= 1
                    current += char
                elif char == ',' and depth == 0:
                    parts.append(current)
                    current = ""
                else:
                    current += char
            if current:
                parts.append(current)
            
            print(f"\nField count by splitting: {len(parts)}")
            for i, part in enumerate(parts[:25], 1):
                print(f"Field {i}: {part[:50]}...")
        break