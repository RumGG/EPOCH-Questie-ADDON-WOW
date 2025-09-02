# Questie Database Validation Guide

## Quick Validation

**Before adding quest data from tickets, ALWAYS validate:**
```bash
python3 validate_db.py
```

If errors are found, the script will tell you exactly what to fix.

## Common Issues and Fixes

### 1. Missing Commas
**Error:** `Line X: Missing comma`
```bash
python3 fix_all_commas.py
```

### 2. Wrong Field 4 (NPC in requiredSkill)
**Error:** `Quest X has NPC data in field 4 (should be nil or skill)`
```bash
python3 fix_quest_field4.py
```

### 3. Duplicate Entries
**Error:** `Duplicate ID X on lines Y and Z`
```bash
python3 remove_duplicate_quests.py  # For quests
python3 fix_duplicate_npcs.py        # For NPCs
```

### 4. Triple-Nested Coordinates
**Error:** `Found X triple-nested coordinates`
```bash
python3 fix_npc_issues.py
```

### 5. Wrong Table Prefix
**Error:** `Found X entries with wrong prefix`
```bash
perl -i -pe 's/^epochQuestData(\[\d+\])/\1/' Database/Epoch/epochQuestDB.lua
perl -i -pe 's/^epochNpcData(\[\d+\])/\1/' Database/Epoch/epochNpcDB.lua
```

## Quest Database Structure

Each quest has 30 fields in this EXACT order:

```lua
[questId] = {
    "Quest Name",           -- 1: name (string)
    {{startNPC}},          -- 2: startedBy (NPCs/items/objects)
    {{endNPC}},            -- 3: finishedBy (NPCs)
    nil,                   -- 4: requiredSkill (nil or skill table)
    60,                    -- 5: requiredLevel (number)
    nil,                   -- 6: questLevel (number or nil)
    nil,                   -- 7: requiredRaces (bitmask or nil)
    {"Kill 10 mobs"},      -- 8: objectives (string table)
    nil,                   -- 9: triggerEnd
    {{{mobId,10}}},        -- 10: objectiveData
    nil,                   -- 11-30: various fields...
},
```

**CRITICAL FIELD 4 RULE:** 
- Must be `nil` or skill data like `{[185]=75}` 
- NEVER `{{npcId}}` - that causes datatype errors!

## NPC Database Structure

Each NPC has 14 fields:

```lua
[npcId] = {
    "NPC Name",            -- 1: name
    100,                   -- 2: minHealth
    150,                   -- 3: maxHealth
    10,                    -- 4: minLevel
    12,                    -- 5: maxLevel
    0,                     -- 6: rank
    {[zone]={{x,y}}},     -- 7: spawns (NEVER {{{x,y}}})
    nil,                   -- 8: waypoints
    16,                    -- 9: zoneID
    {questId},            -- 10: questStarts
    {questId},            -- 11: questEnds
    35,                    -- 12: factionID
    "AH",                  -- 13: friendlyToFaction
    nil,                   -- 14: subName
},
```

## Before Processing Tickets

1. **Validate current state:**
   ```bash
   python3 validate_db.py
   ```

2. **If clean, make a backup:**
   ```bash
   cp Database/Epoch/epochQuestDB.lua Database/Epoch/epochQuestDB.lua.backup
   cp Database/Epoch/epochNpcDB.lua Database/Epoch/epochNpcDB.lua.backup
   ```

3. **Process tickets, adding data**

4. **Validate after EVERY 10-20 tickets:**
   ```bash
   python3 validate_db.py
   ```

5. **Fix any issues immediately** before continuing

## Adding Quest Data from Tickets

### From Data Collection Export
```lua
-- Good format from /qdc export:
[questId] = {"Quest Name",{{giver}},{{turnin}},nil,level,nil,nil,{"objectives"},...},
```

### Common Mistakes to Avoid

❌ **WRONG - NPC in field 4:**
```lua
[26126] = {"Quest",{{npc}},{{npc}},{{npc}},36,...  -- BREAKS!
```

✅ **CORRECT - nil in field 4:**
```lua
[26126] = {"Quest",{{npc}},{{npc}},nil,36,...     -- Works!
```

❌ **WRONG - Missing comma:**
```lua
[26126] = {"Quest",...}  -- No comma!
[26127] = {"Quest2",...}
```

✅ **CORRECT - Has comma:**
```lua
[26126] = {"Quest",...},  -- Has comma!
[26127] = {"Quest2",...},
```

## Emergency Recovery

If the database gets corrupted:

1. **Restore backup:**
   ```bash
   cp Database/Epoch/epochQuestDB.lua.backup Database/Epoch/epochQuestDB.lua
   ```

2. **Or use git to revert:**
   ```bash
   git checkout -- Database/Epoch/epochQuestDB.lua
   ```

3. **Run full fix suite:**
   ```bash
   python3 fix_all_commas.py
   python3 fix_quest_field4.py
   python3 remove_duplicate_quests.py
   python3 validate_db.py
   ```

## Validation Scripts

- **validate_db.py** - Main validator, run this first
- **fix_all_commas.py** - Adds missing commas
- **fix_quest_field4.py** - Fixes NPC data in requiredSkill field
- **remove_duplicate_quests.py** - Removes duplicate quest entries
- **fix_duplicate_npcs.py** - Fixes duplicate NPC IDs
- **fix_npc_issues.py** - Fixes coordinate format issues

## Tips for Processing 200+ Tickets

1. **Work in batches of 10-20 tickets**
2. **Validate after each batch**
3. **Commit to git after each successful batch**
4. **Take breaks - fatigue causes errors**
5. **Use the data collector format when possible**
6. **Double-check field 4 is nil for quests**
7. **Verify NPC coordinates are {{x,y}} not {{{x,y}}}**

## Final Check Before Starting WoW

```bash
python3 validate_db.py
```

Should output:
```
✅ DATABASES ARE CLEAN - Safe to start WoW!
```

If not, fix the errors before starting WoW!