#!/usr/bin/env python3
"""
Process all quest data submissions from GitHub issues automatically.
Extracts database entries and consolidates them into ready-to-add Lua files.
"""

import requests
import re
import json
from datetime import datetime
import time

# Configuration
GITHUB_REPO = "trav346/Questie"
GITHUB_TOKEN = ""  # Optional: Add a personal access token for higher rate limits
OUTPUT_DIR = "./processed_submissions"

def get_all_issues():
    """Fetch all issues from the GitHub repository."""
    issues = []
    page = 1
    
    headers = {}
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    
    while True:
        print(f"Fetching page {page} of issues...")
        url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
        params = {
            'state': 'all',  # Get both open and closed issues
            'per_page': 100,
            'page': page,
            'labels': ''  # You could filter by label if you tag quest submissions
        }
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            print(f"Error fetching issues: {response.status_code}")
            print(response.text)
            break
            
        page_issues = response.json()
        
        if not page_issues:
            break
            
        issues.extend(page_issues)
        page += 1
        
        # Be nice to GitHub's API
        time.sleep(0.5)
    
    return issues

def extract_quest_data(issue_body):
    """Extract quest ID and database entries from issue body."""
    if not issue_body:
        return None
    
    # Look for quest ID patterns
    quest_id_match = re.search(r'Quest ID:\s*(\d+)', issue_body, re.IGNORECASE)
    if not quest_id_match:
        # Try alternative pattern
        quest_id_match = re.search(r'Missing Quest:.*\(ID:\s*(\d+)\)', issue_body, re.IGNORECASE)
    
    if not quest_id_match:
        return None
    
    quest_id = quest_id_match.group(1)
    
    # Extract quest name
    quest_name_match = re.search(r'Quest Name:\s*(.+?)(?:\n|$)', issue_body)
    quest_name = quest_name_match.group(1).strip() if quest_name_match else "Unknown"
    
    # Look for DATABASE ENTRIES section
    db_entries_match = re.search(
        r'DATABASE ENTRIES:.*?\n(.*?)(?:\n(?:═{3,}|END OF QUEST|$))',
        issue_body,
        re.DOTALL | re.IGNORECASE
    )
    
    quest_entry = None
    npc_entries = []
    
    if db_entries_match:
        db_section = db_entries_match.group(1)
        
        # Extract quest database entry
        quest_match = re.search(
            r'\[(\d+)\]\s*=\s*\{([^}]+)\}',
            db_section
        )
        if quest_match:
            quest_entry = f"[{quest_match.group(1)}] = {{{quest_match.group(2)}}}"
        
        # Extract NPC entries
        npc_pattern = r'\[(\d+)\]\s*=\s*\{[^}]+\}'
        npc_matches = re.findall(npc_pattern, db_section)
        for match in npc_matches:
            if match != quest_id:  # Skip the quest entry itself
                full_match = re.search(f'\\[{match}\\]\\s*=\\s*\\{{[^}}]+\\}}', db_section)
                if full_match:
                    npc_entries.append(full_match.group(0))
    
    # If no DATABASE ENTRIES section, try to construct from raw data
    if not quest_entry:
        # Extract what we can from the standard format
        level_match = re.search(r'Level:\s*(\d+)', issue_body)
        level = level_match.group(1) if level_match else "nil"
        
        giver_match = re.search(r'QUEST GIVER:.*?NPC:\s*(.+?)\s*\(ID:\s*(\d+)\)', issue_body, re.DOTALL)
        giver_id = giver_match.group(2) if giver_match else "nil"
        giver_name = giver_match.group(1) if giver_match else None
        
        turnin_match = re.search(r'TURN-IN NPC:.*?NPC:\s*(.+?)\s*\(ID:\s*(\d+)\)', issue_body, re.DOTALL)
        if not turnin_match:
            turnin_match = re.search(r'Turn.?in.*?to\s+(.+?)\s*\(ID:\s*(\d+)\)', issue_body, re.IGNORECASE)
        
        turnin_id = turnin_match.group(2) if turnin_match else "nil"
        turnin_name = turnin_match.group(1) if turnin_match else None
        
        # Construct basic quest entry
        quest_entry = f'[{quest_id}] = {{"{quest_name}",'
        if giver_id != "nil":
            quest_entry += f"{{{{{giver_id}}}}}"
        else:
            quest_entry += "nil"
        quest_entry += ","
        if turnin_id != "nil":
            quest_entry += f"{{{{{turnin_id}}}}}"
        else:
            quest_entry += "nil"
        quest_entry += f",nil,{level}"
        quest_entry += ",nil,nil,nil,nil,nil"  # races, classes, objectives text, trigger, objectives
        quest_entry += ",nil" * 20  # Fields 11-30
        quest_entry += "}"
    
    return {
        'quest_id': quest_id,
        'quest_name': quest_name,
        'quest_entry': quest_entry,
        'npc_entries': npc_entries,
        'issue_number': None,  # Will be set by caller
        'issue_title': None,   # Will be set by caller
        'issue_url': None      # Will be set by caller
    }

def process_all_issues():
    """Process all issues and extract quest data."""
    print("Fetching all issues from GitHub...")
    issues = get_all_issues()
    print(f"Found {len(issues)} total issues")
    
    quest_data = {}
    npc_data = {}
    processed_count = 0
    
    for issue in issues:
        # Skip pull requests
        if 'pull_request' in issue:
            continue
        
        # Look for quest data in the issue
        data = extract_quest_data(issue.get('body', ''))
        
        if data:
            data['issue_number'] = issue['number']
            data['issue_title'] = issue['title']
            data['issue_url'] = issue['html_url']
            
            quest_id = data['quest_id']
            
            # Store quest data (keep the most recent if duplicates)
            if quest_id not in quest_data:
                quest_data[quest_id] = data
                processed_count += 1
                print(f"Found quest {quest_id}: {data['quest_name']} (Issue #{issue['number']})")
            else:
                print(f"Duplicate quest {quest_id} in issue #{issue['number']} (keeping earlier submission)")
    
    print(f"\nProcessed {processed_count} unique quests from {len(issues)} issues")
    return quest_data

def write_consolidated_files(quest_data):
    """Write consolidated database files."""
    import os
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Write quest database additions
    quest_file = os.path.join(OUTPUT_DIR, f"epochQuestDB_additions_{timestamp}.lua")
    with open(quest_file, 'w', encoding='utf-8') as f:
        f.write("-- Automatically extracted quest entries from GitHub issues\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- Total quests: {len(quest_data)}\n\n")
        f.write("local questAdditions = {\n")
        
        for quest_id in sorted(quest_data.keys(), key=int):
            data = quest_data[quest_id]
            f.write(f"    -- {data['quest_name']} (Issue #{data['issue_number']})\n")
            f.write(f"    -- {data['issue_url']}\n")
            f.write(f"    {data['quest_entry']},\n\n")
        
        f.write("}\n")
    
    print(f"Wrote quest entries to: {quest_file}")
    
    # Write NPC database additions
    npc_file = os.path.join(OUTPUT_DIR, f"epochNpcDB_additions_{timestamp}.lua")
    all_npcs = {}
    
    for quest_id, data in quest_data.items():
        for npc_entry in data['npc_entries']:
            # Extract NPC ID from entry
            npc_id_match = re.match(r'\[(\d+)\]', npc_entry)
            if npc_id_match:
                npc_id = npc_id_match.group(1)
                if npc_id not in all_npcs:
                    all_npcs[npc_id] = {
                        'entry': npc_entry,
                        'quests': [quest_id],
                        'issue': data['issue_number']
                    }
                else:
                    all_npcs[npc_id]['quests'].append(quest_id)
    
    with open(npc_file, 'w', encoding='utf-8') as f:
        f.write("-- Automatically extracted NPC entries from GitHub issues\n")
        f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"-- Total NPCs: {len(all_npcs)}\n\n")
        f.write("local npcAdditions = {\n")
        
        for npc_id in sorted(all_npcs.keys(), key=int):
            npc = all_npcs[npc_id]
            f.write(f"    -- Related to quests: {', '.join(npc['quests'])} (Issue #{npc['issue']})\n")
            f.write(f"    {npc['entry']},\n\n")
        
        f.write("}\n")
    
    print(f"Wrote NPC entries to: {npc_file}")
    
    # Write summary report
    report_file = os.path.join(OUTPUT_DIR, f"processing_report_{timestamp}.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("Quest Data Processing Report\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total quests processed: {len(quest_data)}\n")
        f.write(f"Total NPCs extracted: {len(all_npcs)}\n\n")
        
        f.write("Quests by ID:\n")
        f.write("-" * 30 + "\n")
        for quest_id in sorted(quest_data.keys(), key=int):
            data = quest_data[quest_id]
            f.write(f"{quest_id}: {data['quest_name']} (Issue #{data['issue_number']})\n")
    
    print(f"Wrote report to: {report_file}")

def main():
    """Main entry point."""
    print("GitHub Quest Data Processor")
    print("=" * 50)
    
    if not GITHUB_TOKEN:
        print("WARNING: No GitHub token set. API rate limits will be restrictive.")
        print("Set GITHUB_TOKEN in the script for better performance.\n")
    
    quest_data = process_all_issues()
    
    if quest_data:
        write_consolidated_files(quest_data)
        print("\nProcessing complete!")
        print(f"Check the '{OUTPUT_DIR}' directory for output files.")
    else:
        print("\nNo quest data found in issues.")

if __name__ == "__main__":
    main()