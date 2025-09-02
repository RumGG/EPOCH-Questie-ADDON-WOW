#!/usr/bin/env lua

-- Script to find duplicate quests in Questie database
-- Identifies quests with identical names and compares their data

-- Load the quest database
local function loadQuestDatabase()
    -- Define epochQuestData table
    epochQuestData = {}
    
    -- Load the database file
    dofile("Database/Epoch/epochQuestDB.lua")
    
    return epochQuestData
end

-- Compare two quest entries for equality
local function compareQuests(quest1, quest2)
    -- Check if both are tables
    if type(quest1) ~= "table" or type(quest2) ~= "table" then
        return false
    end
    
    -- Compare all 30 fields
    for i = 1, 30 do
        local v1 = quest1[i]
        local v2 = quest2[i]
        
        -- Handle nil values
        if v1 == nil and v2 == nil then
            -- Both nil, continue
        elseif v1 == nil or v2 == nil then
            -- One is nil, not equal
            return false
        elseif type(v1) ~= type(v2) then
            -- Different types
            return false
        elseif type(v1) == "table" then
            -- For tables, convert to string for comparison
            local function tableToString(t)
                if not t then return "nil" end
                local str = "{"
                for k, v in pairs(t) do
                    if type(v) == "table" then
                        str = str .. tableToString(v) .. ","
                    else
                        str = str .. tostring(v) .. ","
                    end
                end
                return str .. "}"
            end
            if tableToString(v1) ~= tableToString(v2) then
                return false
            end
        elseif v1 ~= v2 then
            -- Direct comparison for non-tables
            return false
        end
    end
    
    return true
end

-- Extract key quest data for comparison
local function getQuestSummary(quest)
    if not quest then return "nil" end
    
    local summary = {}
    
    -- Name (field 1)
    summary.name = quest[1] or "Unknown"
    
    -- Quest giver (field 2)
    if quest[2] and quest[2][1] then
        summary.startNpc = quest[2][1][1] or "none"
    else
        summary.startNpc = "none"
    end
    
    -- Quest turn-in (field 3)  
    if quest[3] and quest[3][1] then
        summary.endNpc = quest[3][1][1] or "none"
    else
        summary.endNpc = "none"
    end
    
    -- Objectives (field 10)
    summary.objectives = ""
    if quest[10] then
        -- Creatures to kill
        if quest[10][1] then
            for _, mob in ipairs(quest[10][1] or {}) do
                summary.objectives = summary.objectives .. string.format("Kill %dx%s; ", mob[2] or 0, mob[1] or "?")
            end
        end
        -- Objects to interact with
        if quest[10][2] then
            for _, obj in ipairs(quest[10][2] or {}) do
                summary.objectives = summary.objectives .. string.format("Object %dx%s; ", obj[2] or 0, obj[1] or "?")
            end
        end
        -- Items to collect
        if quest[10][3] then
            for _, item in ipairs(quest[10][3] or {}) do
                summary.objectives = summary.objectives .. string.format("Item %dx%s; ", item[2] or 0, item[1] or "?")
            end
        end
    end
    
    -- Zone (field 17)
    summary.zone = quest[17] or "none"
    
    -- Quest flags (field 23)
    summary.questFlags = quest[23] or 0
    
    return summary
end

-- Main function
local function findDuplicates()
    print("Loading quest database...")
    local quests = loadQuestDatabase()
    
    -- Build a map of quest names to IDs
    local nameToIds = {}
    local totalQuests = 0
    
    for questId, questData in pairs(quests) do
        totalQuests = totalQuests + 1
        local name = questData[1] or "Unknown"
        
        if not nameToIds[name] then
            nameToIds[name] = {}
        end
        table.insert(nameToIds[name], questId)
    end
    
    print(string.format("Analyzed %d quests", totalQuests))
    print("=" .. string.rep("=", 78))
    
    -- Find and analyze duplicates
    local duplicateGroups = {}
    local exactDuplicates = {}
    local similarQuests = {}
    
    for name, ids in pairs(nameToIds) do
        if #ids > 1 then
            -- Skip placeholder entries
            if not string.find(name, "^%[Epoch%] Quest %d+$") then
                table.insert(duplicateGroups, {name = name, ids = ids})
            end
        end
    end
    
    -- Sort by name for consistent output
    table.sort(duplicateGroups, function(a, b) return a.name < b.name end)
    
    -- Analyze each duplicate group
    print("\nQUESTS WITH DUPLICATE NAMES:")
    print("=" .. string.rep("=", 78))
    
    for _, group in ipairs(duplicateGroups) do
        print(string.format("\n\"%s\" - %d instances:", group.name, #group.ids))
        print("-" .. string.rep("-", 78))
        
        local questDataList = {}
        for _, id in ipairs(group.ids) do
            local quest = quests[id]
            local summary = getQuestSummary(quest)
            table.insert(questDataList, {id = id, quest = quest, summary = summary})
        end
        
        -- Check for exact duplicates
        local foundExactDuplicate = false
        for i = 1, #questDataList do
            for j = i + 1, #questDataList do
                if compareQuests(questDataList[i].quest, questDataList[j].quest) then
                    if not foundExactDuplicate then
                        print("  ⚠️  EXACT DUPLICATES FOUND:")
                    end
                    foundExactDuplicate = true
                    print(string.format("      Quest %d and %d are IDENTICAL - one can be purged", 
                        questDataList[i].id, questDataList[j].id))
                    
                    table.insert(exactDuplicates, {
                        name = group.name,
                        id1 = questDataList[i].id,
                        id2 = questDataList[j].id
                    })
                end
            end
        end
        
        -- Display quest details
        for _, data in ipairs(questDataList) do
            local s = data.summary
            print(string.format("  Quest %d:", data.id))
            print(string.format("    Start NPC: %s | End NPC: %s | Zone: %s | Flags: %s", 
                tostring(s.startNpc), tostring(s.endNpc), tostring(s.zone), tostring(s.questFlags)))
            if s.objectives ~= "" then
                print(string.format("    Objectives: %s", s.objectives))
            else
                print("    Objectives: None")
            end
        end
        
        -- Check if they're sequential (likely different parts of a chain)
        local sequential = true
        for i = 2, #group.ids do
            if group.ids[i] ~= group.ids[i-1] + 1 then
                sequential = false
                break
            end
        end
        
        if sequential and not foundExactDuplicate then
            print("  ℹ️  Note: Sequential IDs - likely a quest chain, should be preserved")
            table.insert(similarQuests, {name = group.name, ids = group.ids})
        end
    end
    
    -- Summary report
    print("\n" .. string.rep("=", 80))
    print("SUMMARY REPORT")
    print(string.rep("=", 80))
    print(string.format("Total quests analyzed: %d", totalQuests))
    print(string.format("Quest names with duplicates: %d", #duplicateGroups))
    print(string.format("Exact duplicates to purge: %d", #exactDuplicates))
    print(string.format("Similar quests to preserve (quest chains): %d", #similarQuests))
    
    -- List quests to purge
    if #exactDuplicates > 0 then
        print("\n" .. string.rep("=", 80))
        print("RECOMMENDED PURGE LIST:")
        print(string.rep("=", 80))
        print("The following quest IDs can be safely removed (keeping the lower ID):")
        
        for _, dup in ipairs(exactDuplicates) do
            local keepId = math.min(dup.id1, dup.id2)
            local removeId = math.max(dup.id1, dup.id2)
            print(string.format("  REMOVE Quest %d (duplicate of %d) - \"%s\"", 
                removeId, keepId, dup.name))
        end
    end
    
    -- List quest chains to preserve
    if #similarQuests > 0 then
        print("\n" .. string.rep("=", 80))
        print("QUEST CHAINS TO PRESERVE:")
        print(string.rep("=", 80))
        print("The following appear to be quest chains and should be kept:")
        
        for _, chain in ipairs(similarQuests) do
            local idStr = table.concat(chain.ids, ", ")
            print(string.format("  \"%s\": Quests %s", chain.name, idStr))
        end
    end
    
    -- Special case: Check for our known duplicate
    print("\n" .. string.rep("=", 80))
    print("SPECIFIC CASE: Shift into G.E.A.R.")
    print(string.rep("=", 80))
    if quests[28725] and quests[28901] then
        print("Quest 28725 exists: " .. (quests[28725][1] or "Unknown"))
        print("Quest 28901 exists: " .. (quests[28901][1] or "Unknown"))
        if compareQuests(quests[28725], quests[28901]) then
            print("✅ Confirmed: 28725 and 28901 are EXACT duplicates")
            print("Recommendation: Remove 28901, keep 28725 (actual quest ID)")
        else
            print("⚠️  Warning: 28725 and 28901 have the same name but different data")
            print("Further investigation needed")
        end
    end
end

-- Run the script
findDuplicates()