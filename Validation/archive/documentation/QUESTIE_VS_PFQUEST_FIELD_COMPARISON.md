# Questie vs pfQuest Database Field Comparison

## Quest Database Structure Comparison

| Field # | Questie Field | Questie Description | pfQuest Field | pfQuest Description | Data Example |
|---------|---------------|---------------------|---------------|---------------------|--------------|
| 1 | name | Quest name | T | Title (quest name) | "Shift into G.E.A.R." |
| 2 | startedBy | {{NPCs},{Objects},{Items}} | start | NPC IDs that start quest | {{46836}} |
| 3 | finishedBy | {{NPCs},{Objects}} | end | NPC IDs for turn-in | {{46836}} |
| 4 | requiredLevel | Min level to get quest | min | Minimum level | nil or number |
| 5 | questLevel | Quest's level | lvl | Quest level | 1 |
| 6 | requiredRaces | Race bitmask (nil=all) | race | Race flags (77=Alliance, 178=Horde) | nil |
| 7 | requiredClasses | Class bitmask (nil=all) | class | Class restrictions | nil |
| 8 | objectivesText | {Quest description strings} | O | Objectives text | {"Kill 10 Underfed Troggs."} |
| 9 | triggerEnd | Exploration trigger | - | NOT IN PFQUEST | nil |
| 10 | **objectives** | **{{creatures},{objects},{items}}** | **obj** | **NOT CONVERTED** | **{{{46837,10,"Underfed Trogg"}}}** |
| 11 | sourceItemId | Item provided by quest giver | item | Source item | nil |
| 12 | preQuestGroup | {All must be done} | pre | Prerequisites (single ID or table) | nil |
| 13 | preQuestSingle | {Any must be done} | - | NOT IN PFQUEST | nil |
| 14 | childQuests | {Unlocked by this} | - | NOT IN PFQUEST | nil |
| 15 | inGroupWith | {Same chain quests} | - | NOT IN PFQUEST | nil |
| 16 | exclusiveTo | {Can't have both} | - | NOT IN PFQUEST | nil |
| 17 | zoneOrSort | Zone ID or QuestSort | - | NOT DIRECTLY (inferred) | 1 |
| 18 | requiredSkill | {skillId, value} | skill | Profession requirement | nil |
| 19 | requiredMinRep | {factionId, value} | - | NOT IN PFQUEST | nil |
| 20 | requiredMaxRep | {factionId, value} | - | NOT IN PFQUEST | nil |
| 21 | requiredSourceItems | {Items needed to start} | - | NOT IN PFQUEST | nil |
| 22 | nextQuestInChain | Direct follow-up | next | Next quest ID | nil |
| 23 | questFlags | Special flags | - | NOT IN PFQUEST | 8 |
| 24 | specialFlags | More flags | - | NOT IN PFQUEST | 0 |
| 25 | parentQuest | Parent quest ID | - | NOT IN PFQUEST | nil |
| 26 | reputationReward | {{factionId, value},...} | - | NOT IN PFQUEST | nil |
| 27 | extraObjectives | {{spellId, text},...} | - | NOT IN PFQUEST | nil |
| 28 | requiredSpell | Spell requirement | - | NOT IN PFQUEST | nil |
| 29 | requiredSpecialization | Spec requirement | - | NOT IN PFQUEST | nil |
| 30 | requiredMaxLevel | Maximum level | max | Maximum level | nil |

## NPC Database Structure Comparison

| Field # | Questie Field | Description | pfQuest Field | Description | Data Example |
|---------|---------------|-------------|---------------|-------------|--------------|
| 1 | name | NPC name | name | NPC name | "Underfed Trogg" |
| 2 | minLevelHealth | Min HP | - | NOT IN PFQUEST | nil |
| 3 | maxLevelHealth | Max HP | - | NOT IN PFQUEST | nil |
| 4 | minLevel | Min level | lvl or min_lvl | Minimum level | 1 |
| 5 | maxLevel | Max level | lvl or max_lvl | Maximum level | 2 |
| 6 | rank | 0=normal, 1=elite, 2=rare elite, 3=boss, 4=rare | rank | Same classification | 0 |
| 7 | **spawns** | **{[zoneId]={{x,y},...}}** | **coords** | **{[zoneId]={{x,y},...}}** | **{[1]={{24.5,60.2}}}** |
| 8 | waypoints | Patrol paths | - | NOT IN PFQUEST | nil |
| 9 | zoneID | Primary zone | - | NOT IN PFQUEST (in coords) | 1 |
| 10 | questStarts | {Quest IDs started} | starts | Quest IDs this NPC starts | nil |
| 11 | questEnds | {Quest IDs ended} | ends | Quest IDs this NPC ends | nil |
| 12 | factionID | Faction template ID | faction or fac | Faction ID | nil |
| 13 | friendlyToFaction | "A", "H", "AH", or nil | - | Uses race field instead | "A" |
| 14 | subName | Title like "Weapon Vendor" | title | NPC subtitle | nil |
| 15 | npcFlags | Bitflags (2=questgiver, etc) | - | NOT IN PFQUEST | 0 |

## Key Differences Found

### ❌ **CRITICAL: pfQuest's `obj` field was NOT converted!**
The pfQuest database has an `obj` field with mob/item/object requirements, but the conversion script didn't map it to Questie's field 10 (objectives). This is why the converted quests show `nil` for objectives!

### pfQuest Data We're Missing:
1. **Objective data (obj field)** - Contains mob IDs, item IDs, object IDs with counts
2. **NPC spawn coordinates** - pfQuest has coords but conversion may not have mapped them all
3. **Quest text (D field)** - Quest description/lore text

### Questie Data pfQuest Doesn't Have:
1. **Exploration triggers** (field 9)
2. **Multiple prerequisite types** (fields 13-16)
3. **Quest flags** (fields 23-24)
4. **Reputation requirements/rewards** (fields 19-20, 26)
5. **NPC health values** (fields 2-3)
6. **NPC waypoints** (field 8)
7. **NPC flags** (field 15)

## Example: Quest 28901 Data Comparison

### Questie Format:
```lua
[28901] = {"Shift into G.E.A.R.",{{46836}},{{46836}},nil,1,nil,nil,{"Kill 10 Underfed Troggs."},nil,{{{46837,10,"Underfed Trogg"}}},nil,nil,nil,nil,nil,nil,1,nil,nil,nil,nil,nil,8,0,nil,nil,nil,nil,nil,nil}
```

### pfQuest Original Format (theoretical):
```lua
[28901] = {
    ["T"] = "Shift into G.E.A.R.",
    ["O"] = "Kill 10 Underfed Troggs.",
    ["start"] = {46836},
    ["end"] = {46836},
    ["lvl"] = 1,
    ["obj"] = {
        ["U"] = {  -- Units/creatures to kill
            [46837] = 10  -- Kill 10 of NPC 46837
        }
    }
}
```

## The Problem
The conversion script successfully converted names, NPCs, and levels, but **failed to convert the `obj` field** which contains the actual quest objectives (what to kill, what to collect). This is why objectives show as `nil` in the converted database!