#!/usr/bin/env python3
# Script to remove contaminated quests
import re

contaminated_ids = [9609, 9610]


with open('epochQuestDB_CLEANED.lua', 'r') as f:
    lines = f.readlines()

with open('epochQuestDB_FINAL.lua', 'w') as f:
    skip_next = False
    for line in lines:
        match = re.match(r'\s*\[(\d+)\]', line)
        if match and int(match.group(1)) in contaminated_ids:
            skip_next = True
            continue
        if skip_next and line.strip().endswith('},'):
            skip_next = False
            continue
        f.write(line)
