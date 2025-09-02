# GNOME QUEST FIX - FOUND THE ISSUE!

## THE PROBLEM IDENTIFIED
By comparing Thievin' Crabs (working) with Shift into G.E.A.R. (broken):

### Field 23 - questFlags
- **Thievin' Crabs**: questFlags = 2 ✅ (mob markers show)
- **Shift into G.E.A.R.**: questFlags = 8 ❌ (mob markers don't show)

## FIXES APPLIED

### 1. Quest 28901 - Shift into G.E.A.R.
Changed questFlags from 8 to 2

### 2. Quest 28902 - No Room for Sympathy  
Changed questFlags from 8 to 2

### 3. Quest 28903 - Encrypted Memorandum
Changed questFlags from 8 to 2

### 4. NPC 46836 - Tinker Captain Whistlescrew
Fixed questEnds field (removed 28903 which ends at NPC 46882)

## Files Modified
- `Database/Epoch/epochQuestDB.lua` - Lines 365-367 (questFlags changed)
- `Database/Epoch/epochNpcDB.lua` - Line 909 (NPC questEnds fixed)

## What questFlags Mean
- Flag 2 = Normal quest (shows objectives on map)
- Flag 8 = Unknown special behavior (breaks mob markers)

## TO APPLY THE FIX
1. Save all files
2. **COMPLETELY EXIT WOW** (not just /reload)
3. Start WoW
4. The mob markers should now appear!

## Why This Happened
The pfQuest conversion or manual entry used questFlag 8 for all gnome quests. This flag has some special behavior that prevents mob markers from showing on the map. Changing to flag 2 (standard quest) fixes it.