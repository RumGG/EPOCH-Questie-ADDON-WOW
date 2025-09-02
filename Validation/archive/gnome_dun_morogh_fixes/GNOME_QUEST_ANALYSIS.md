# Gnome Starting Area Quest Analysis

## Current Status
The gnome starting quests ALREADY HAVE complete data in the current database!

## Quest Data Present:

### Quest 28901: "Shift into G.E.A.R."
- **Quest giver**: NPC 46836 (Tinker Captain Whistlescrew) ✅
- **Objectives**: Kill 10 Underfed Troggs (NPC 46837) ✅
- **Mob spawn data**: 5 coordinates in zone 1 (Dun Morogh) ✅

### Quest 28902: "No Room for Sympathy"
- **Quest giver**: NPC 46836 (Tinker Captain Whistlescrew) ✅
- **Objectives**: Kill 8 Irradiated Oozes (46839) + 4 Infected Gnomes (46838) ✅
- **Mob spawn data**: 
  - Irradiated Ooze: 5 coordinates in zone 1 ✅
  - Infected Gnome: Need to check

### Quest 28903: "Encrypted Memorandum"
- **Quest giver**: NPC 46836 ✅
- **Turn-in**: NPC 46882 (Windle Fusespring) ✅
- **Type**: Delivery quest (no mobs to kill)

## Data Comparison:
- **Current Database**: Has full objective data with mob IDs and counts
- **pfQuest Conversion**: Has identical data
- **No difference between databases for these quests!**

## NPCs with Spawn Locations:
- ✅ 46836: Tinker Captain Whistlescrew (24.7, 59.1) - Quest giver
- ✅ 46837: Underfed Trogg (5 spawn points) - Quest mob
- ✅ 46839: Irradiated Ooze (5 spawn points) - Quest mob
- ❓ 46838: Infected Gnome - Need to verify
- ❓ 46882: Windle Fusespring - Need to verify

## Potential Issues:
If mob markers aren't showing in-game, it could be:

1. **Quest prerequisites**: Maybe these quests have hidden prerequisites
2. **Level requirements**: Character might not meet level requirements
3. **Race/class restrictions**: Might be limited to gnomes only
4. **Quest chain**: Quest 28725 mentioned by user might be the actual starter
5. **Database not recompiled**: After changes, database needs recompilation

## Quest 28725:
- **NOT in current database**
- **NOT in pfQuest conversion**
- User says this is the "first quest you get"
- This might be the missing piece!

## Recommendations:
1. **Add Quest 28725** if it exists in-game
2. **Check Infected Gnome (46838)** spawn locations
3. **Verify quest chain** - what triggers 28901?
4. **Test in-game** with a gnome character
5. **Use data collector** to capture quest 28725 if it exists