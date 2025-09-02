# Questie Epoch Quest Data Processing Guide

## Overview
This guide helps process quest data submissions from GitHub issues for the Questie-Epoch addon (WoW 3.3.5a, Project Epoch server).

## Critical Context
- **Server**: Project Epoch (custom WoW 3.3.5a server with 600+ custom quests)
- **Quest IDs**: Epoch uses 26000-29000 range for custom content
- **Database Files**: Direct modification only - correction files don't work
- **Testing**: Changes require full WoW restart, not just /reload

## File Locations
```
Database/Epoch/epochQuestDB.lua    # Quest definitions
Database/Epoch/epochNpcDB.lua      # NPC definitions  
Database/Epoch/epochItemDB.lua     # Item definitions
Database/Epoch/epochObjectDB.lua   # Object definitions
```

## Quest Database Format (30 fields)
```lua
epochQuestData[questId] = {
    "Quest Name",           -- 1: Name (string)
    {{startNPC}},          -- 2: Quest giver NPC IDs
    {{endNPC}},            -- 3: Turn-in NPC IDs (REQUIRED for gold ?)
    nil,                   -- 4: Starter item
    60,                    -- 5: Level
    60,                    -- 6: Required level
    nil,                   -- 7: Next quest in chain
    {"Quest objectives"},  -- 8: Objective text
    nil,                   -- 9: Objective data (old format)
    {{{npcId,"Kill 10"}}}, -- 10: Objectives (new format)
    nil,                   -- 11-16: Various quest data
    85,                    -- 17: Zone ID
    nil,                   -- 18-22: More quest data
    1,                     -- 23: Faction (1=Alliance, 2=Horde, 8=Both)
    0,                     -- 24: Profession
    nil,nil,nil,nil,nil,nil -- 25-30: Additional fields
}
```

## NPC Database Format
```lua
epochNpcData[npcId] = {
    "NPC Name",            -- Name
    nil,                   -- Subname
    minLevel,              -- Min level
    maxLevel,              -- Max level
    rank,                  -- Rank (0=normal, 1=elite, etc)
    {[zoneId]={{x,y}}},   -- Spawn coordinates by zone
    nil,                   -- Waypoints
    zoneId,                -- Primary zone
    {questsGiven},         -- Quest IDs this NPC starts
    {questsTurnIn},        -- Quest IDs this NPC completes
    12,                    -- Type (humanoid, beast, etc)
    "A",                   -- Faction (A/H/AH)
    nil,                   -- ID2
    65671                  -- npcFlags (bitwise)
}
```

## Common NPC Flags
```
GOSSIP = 1
QUEST_GIVER = 2  
REPAIR = 4
VENDOR = 128
INNKEEPER = 65536

Examples:
- Quest giver only: 2
- Quest giver + gossip: 3
- Innkeeper + vendor + gossip: 65671
```

## Processing Checklist

### 1. Check for Existing Quest
```bash
grep "epochQuestData\[26XXX\]" Database/Epoch/epochQuestDB.lua
```
- Many quests exist with placeholder names like "[Epoch] Quest 26XXX"
- Update existing entries rather than adding duplicates

### 2. Validate Quest Data
- [ ] Quest ID in range 26000-29000
- [ ] Quest name is not placeholder
- [ ] Has quest giver NPC (field 2)
- [ ] Has turn-in NPC (field 3) - CRITICAL for gold question mark
- [ ] Zone ID is valid (see common zones below)
- [ ] Faction field set (1/2/8)

### 3. Check NPC Data
```bash
grep "epochNpcData\[XXXXX\]" Database/Epoch/epochNpcDB.lua
```
- [ ] Quest giver NPC exists
- [ ] Turn-in NPC exists
- [ ] NPCs have correct questsGiven/questsTurnIn arrays
- [ ] NPCs have QUEST_GIVER flag (2) in npcFlags

### 4. Handle Phasing
- NPCs can have IDs ±1 after quest completion (phasing)
- Check both 45898 and 45899 for example
- Use the NPC that has the quest in their turns_in array

### 5. Common Issues to Fix

#### Missing Turn-in NPC
```lua
-- BAD: Gold ? won't show
{{45898}},nil,nil,

-- GOOD: Gold ? will show  
{{45898}},{{45898}},nil,
```

#### Wrong Faction Setting
```lua
-- If quest exists for both Alliance AND Horde:
-- Don't create two entries!
-- Use faction = 8 (both)
```

#### Duplicate Entries
- Lua uses last definition, earlier ones ignored
- Check for multiple definitions of same quest ID
- Keep most complete version

#### Placeholder Data
```lua
-- BAD: Placeholder name
"[Epoch] Quest 26939",

-- GOOD: Real name
"Peace in Death",
```

## Common Zone IDs
```
1 = Dun Morogh
10 = Duskwood
11 = Wetlands
12 = Elwynn Forest
14 = Durotar
17 = The Barrens
33 = Stranglethorn Vale
36 = Alterac Mountains
40 = Westfall
45 = Arathi Highlands
47 = The Hinterlands
51 = Searing Gorge
85 = Tirisfal Glades
130 = Silverpine Forest
141 = Teldrassil
267 = Hillsbrad Foothills
331 = Ashenvale
357 = Feralas
400 = Thousand Needles
```

## Data Collection Format (from /qdc export)
When users submit data from the collection system:

```lua
{
    questGiver = {npcId = 45898, name = "Joseph Strinbrow"},
    turnIn = {npcId = 45898, name = "Joseph Strinbrow"},
    objectives = {
        {text = "Joseph Strinbrow's spirit laid to rest", 
         objectId = 60445, coords = {x=60.1, y=53.3}}
    },
    mobs = {
        [45898] = {name = "Joseph Strinbrow", coords = {...}}
    }
}
```

## Red Flags - Do Not Process
- Quest IDs below 26000 (not Epoch)
- NPCs with IDs below 40000 (likely not Epoch)
- Quests with retail WoW names (check Wowhead)
- Data that would overwrite Blizzard content

## Verification Steps
1. Check if quest already exists (may need updating)
2. Verify NPCs exist in epochNpcDB.lua
3. Ensure turn-in NPC is set (field 3)
4. Confirm zone ID matches coordinates
5. Check for faction conflicts (should be 8 if both)

## Testing Workflow
1. Make changes to database files
2. Exit WoW completely (not just /reload)
3. Restart WoW
4. Check quest tracker shows quest properly
5. Verify NPCs appear on map with markers

## Common Mistakes to Avoid
1. **Don't create correction files** - They don't load properly
2. **Don't trust single coordinates** - NPCs often have multiple spawns
3. **Don't assume quest giver = turn-in** - Often different NPCs
4. **Don't ignore phasing** - Check ±1 NPC IDs
5. **Don't add duplicates** - Always grep first
6. **Don't use table name prefix inside table** - Use `[id] = {...}` not `epochNpcData[id] = {...}`

### Common Syntax Errors

#### 1. Table name prefix inside table
When adding entries to database files, they must NOT have the table name prefix:
```lua
-- WRONG (causes syntax error):
epochNpcData = {
    ...
    epochNpcData[45004] = {"Name",...},  -- ❌ Will cause '}' expected error
}

-- CORRECT:
epochNpcData = {
    ...
    [45004] = {"Name",...},  -- ✓ Proper table entry
}
```

#### 2. Adding entries outside the table
Entries must be INSIDE the table, before the closing brace:
```lua
-- WRONG (causes syntax error):
epochNpcData = {
    ...
    [45003] = {"Last Entry",...}
}  -- Table closes here!

epochNpcData[45004] = {"Name",...}  -- ❌ Outside table - syntax error!

-- CORRECT:
epochNpcData = {
    ...
    [45003] = {"Entry",...},
    [45004] = {"Name",...}  -- ✓ Inside table
}
```

#### 3. Missing commas between entries
Every entry except the last one needs a trailing comma:
```lua
-- WRONG (causes syntax error):
epochNpcData = {
    ...
    [45003] = {"Entry 1",...}  -- ❌ Missing comma
    [45004] = {"Entry 2",...}  -- Syntax error: unexpected symbol
}

-- CORRECT:
epochNpcData = {
    ...
    [45003] = {"Entry 1",...},  -- ✓ Has comma
    [45004] = {"Entry 2",...}   -- Last entry - comma optional
}
```

Fix commands if these happen:
```bash
# Remove prefix from inside table:
perl -i -pe 's/^epochNpcData(\[\d+\])/\1/' Database/Epoch/epochNpcDB.lua
perl -i -pe 's/^epochQuestData(\[\d+\])/\1/' Database/Epoch/epochQuestDB.lua

# Move entries from outside to inside table (manual fix needed):
# 1. Find the closing brace }
# 2. Move all epochXXXData[id] entries before it
# 3. Remove the epochXXXData prefix from those entries
```

## Script for Bulk Processing
```python
import re

def parse_quest_submission(text):
    """Extract quest data from GitHub issue"""
    # Look for quest ID
    quest_id = re.search(r'Quest ID: (\d+)', text)
    # Look for NPCs
    giver = re.search(r'questGiver.*?npcId = (\d+)', text)
    turnin = re.search(r'turnIn.*?npcId = (\d+)', text)
    # Extract and format for Lua
    # ...
```

## When to Reject Submissions
- Incomplete data (no quest accepted from start)
- Missing critical NPCs
- Obviously incorrect zone/coordinates
- Retail WoW content (non-Epoch)
- Malformed or suspicious data

## Priority Order
1. Quests with complete data (giver + turnin + objectives)
2. Quests fixing placeholders
3. Quests adding missing turn-ins
4. New quests not in database
5. Minor coordinate corrections

## Notes on Data Quality
- User submissions often have incomplete data (warned with ⚠️)
- Coordinates can be approximate (player movement)
- Object names might be generic ("Ground Object")
- Some NPCs are phased versions (check ±1 ID)
- Trust NPC database over user submissions for turn-ins

## Commit Message Format
```
Add quest data from GitHub issues #X-Y

- Added X new quests with complete data
- Fixed Y quests with missing turn-in NPCs
- Updated Z placeholder quest names
```

## Final Checklist Before Committing
- [ ] All quest IDs are unique (no duplicates)
- [ ] All NPCs referenced exist in epochNpcDB.lua
- [ ] Turn-in NPCs set for all quests (field 3)
- [ ] No placeholder names remain
- [ ] Faction conflicts resolved (use 8 for both)
- [ ] Zone IDs match coordinate data