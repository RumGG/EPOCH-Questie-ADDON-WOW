# GNOME QUEST FIXES - COMPLETE SOLUTION

## The Problem
- Gnome starting zone quests weren't showing mob markers on the map
- NPC 46836 was showing completed quests as available
- Quest ID mismatch: Gnomes actually receive quest 28725, not 28901

## Root Causes Found
1. **Wrong Quest ID**: The actual quest ID gnomes receive is 28725, not 28901
2. **questFlags Issue**: All gnome quests had questFlags = 8 (special behavior) instead of 2 (normal quest)
3. **Missing Quest Entry**: Quest 28725 was completely missing from the database

## Fixes Applied

### 1. Added Missing Quest 28725
- Added quest 28725 with same data as 28901
- Kept 28901 as duplicate for backwards compatibility

### 2. Fixed questFlags for ALL Gnome Quests
Changed questFlags from 8 to 2 for:
- Quest 28725 (Shift into G.E.A.R.) - NEW ENTRY
- Quest 28901 (Shift into G.E.A.R.) - duplicate
- Quest 28902 (No Room for Sympathy)
- Quest 28903 (Encrypted Memorandum)
- Quest 28726 (A Refugee's Quandary)
- Quest 28727 (Aid to the Refugees)
- Quest 28729 (Guard Duty)
- Quest 28730 (Securing the Perimeter)
- Quest 28731 (Orders from Command)

### 3. Updated NPC 46836
- Added quest 28725 to questStarts list
- Now has: {28725,28901,28902,28903}

## Files Modified
- `Database/Epoch/epochQuestDB.lua`
  - Line 365: Added quest 28725
  - Lines 366-368: Fixed questFlags for 28901, 28902, 28903
  - Lines 371-375: Fixed questFlags for 28726, 28727, 28729, 28730, 28731
  
- `Database/Epoch/epochNpcDB.lua`
  - Line 909: Updated NPC 46836 to include quest 28725

## TO APPLY THE FIX
1. Save all files
2. **COMPLETELY EXIT WOW** (not just /reload)
3. Start WoW
4. Mob markers should now appear on the map!

## Why This Fix Works
- questFlags = 8 has special behavior that prevents mob markers from showing
- questFlags = 2 is the standard quest flag that allows normal objective display
- The correct quest ID (28725) ensures Questie recognizes the quest the player actually has