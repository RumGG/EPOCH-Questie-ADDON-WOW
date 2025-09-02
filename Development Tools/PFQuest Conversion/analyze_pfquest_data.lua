#!/usr/bin/env lua

-- Script to analyze and compare pfQuest-epoch data with Questie-Epoch data
-- and generate conversion suggestions

-- Helper function to safely load Lua files
local function loadLuaFile(filepath)
    local file = io.open(filepath, "r")
    if not file then
        print("Error: Could not open file " .. filepath)
        return nil
    end
    
    local content = file:read("*all")
    file:close()
    
    -- Create sandbox environment
    local env = {
        pfDB = {},
        epochQuestData = {},
        epochNpcData = {},
        QuestieDB = { _epochQuestData = {} },
        QuestieLoader = { ImportModule = function() return {} end }
    }
    
    local chunk, err = loadstring(content)
    if not chunk then
        print("Error loading " .. filepath .. ": " .. err)
        return nil
    end
    
    setfenv(chunk, env)
    local success, err = pcall(chunk)
    if not success then
        print("Error executing " .. filepath .. ": " .. err)
        return nil
    end
    
    return env
end

-- Load pfQuest data
local pfQuestPath = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/pfQuest-epoch/"
local questiePath = "/Users/travisheryford/Library/CloudStorage/Dropbox/WoW Interfaces/epoch/AddOns/Questie/"

print("Loading pfQuest databases...")
local pfQuestData = loadLuaFile(pfQuestPath .. "db/quests-epoch.lua")
local pfQuestText = loadLuaFile(pfQuestPath .. "db/enUS/quests-epoch.lua")
local pfUnitsData = loadLuaFile(pfQuestPath .. "db/units-epoch.lua")

print("Loading Questie databases...")
local questieQuestData = loadLuaFile(questiePath .. "Database/Epoch/epochQuestDB.lua")
local questieNpcData = loadLuaFile(questiePath .. "Database/Epoch/epochNpcDB.lua")

if not pfQuestData or not pfQuestText or not questieQuestData then
    print("Failed to load required databases")
    return
end

-- Extract the actual data
local pfQuests = pfQuestData.pfDB["quests"]["data-epoch"] or {}
local pfTexts = pfQuestText.pfDB["quests"]["enUS-epoch"] or {}
local pfUnits = pfUnitsData and pfUnitsData.pfDB["units"]["data-epoch"] or {}
local questieQuests = questieQuestData.epochQuestData or {}
local questieNpcs = questieNpcData and questieNpcData.epochNpcData or {}

-- Analyze data
local pfQuestCount = 0
local questieQuestCount = 0
local missingInQuestie = {}
local missingNames = {}

-- Count pfQuest quests
for questId, questData in pairs(pfQuests) do
    if type(questData) == "table" then
        pfQuestCount = pfQuestCount + 1
        
        -- Check if quest exists in Questie
        if not questieQuests[questId] then
            missingInQuestie[questId] = {
                data = questData,
                text = pfTexts[questId]
            }
        elseif questieQuests[questId] and questieQuests[questId][1] == "[Epoch] Quest " .. questId then
            -- Quest exists but has placeholder name
            missingNames[questId] = {
                data = questData,
                text = pfTexts[questId],
                questieEntry = questieQuests[questId]
            }
        end
    end
end

-- Count Questie quests
for questId, questData in pairs(questieQuests) do
    if type(questData) == "table" then
        questieQuestCount = questieQuestCount + 1
    end
end

print("\n=== ANALYSIS RESULTS ===")
print(string.format("pfQuest-epoch has %d quests", pfQuestCount))
print(string.format("Questie-Epoch has %d quests", questieQuestCount))
print(string.format("Missing in Questie: %d quests", table.getn(missingInQuestie)))
print(string.format("Placeholder names in Questie: %d quests", table.getn(missingNames)))

-- Helper function to convert faction
local function convertFaction(raceFlag)
    if not raceFlag then return 3 end -- Both factions
    if raceFlag == 77 then return 2 end -- Alliance (1+4+8+64 = Human+NE+Gnome+Draenei)
    if raceFlag == 178 then return 1 end -- Horde (2+16+32+128 = Orc+Tauren+Troll+BE)
    return 3 -- Default to both
end

-- Generate conversion suggestions for missing quests
print("\n=== MISSING QUESTS TO ADD ===")
local outputFile = io.open(questiePath .. "pfquest_missing_quests.lua", "w")
outputFile:write("-- Missing quests from pfQuest-epoch that should be added to Questie\n")
outputFile:write("-- Generated on " .. os.date() .. "\n\n")
outputFile:write("local missingQuests = {\n")

local count = 0
for questId, questInfo in pairs(missingInQuestie) do
    if count < 20 then -- Limit output for readability
        local text = questInfo.text or {}
        local data = questInfo.data
        
        if text.T then -- Only process if we have a title
            print(string.format("  [%d] = \"%s\" (Level %s)", 
                questId, text.T or "Unknown", data.lvl or "?"))
            
            -- Generate Questie format entry
            local startNpcs = data.start and data.start.U or nil
            local endNpcs = data["end"] and data["end"].U or nil
            local faction = convertFaction(data.race)
            
            outputFile:write(string.format('  [%d] = {"%s",', questId, text.T or "Unknown"))
            
            -- Start NPCs
            if startNpcs then
                outputFile:write("{{" .. table.concat(startNpcs, ",") .. "}},")
            else
                outputFile:write("nil,")
            end
            
            -- End NPCs
            if endNpcs then
                outputFile:write("{{" .. table.concat(endNpcs, ",") .. "}},")
            else
                outputFile:write("nil,")
            end
            
            -- Other fields
            outputFile:write(string.format('nil,%s,nil,%d,', data.lvl or 1, faction))
            
            -- Objectives
            if text.O then
                outputFile:write(string.format('{"%s"},', text.O:gsub('"', '\\"')))
            else
                outputFile:write("nil,")
            end
            
            -- Fill remaining fields with nil
            outputFile:write("nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,nil,0,nil,nil,nil,nil,nil,nil},")
            outputFile:write(" -- From pfQuest-epoch\n")
            
            count = count + 1
        end
    end
end

outputFile:write("}\n\n")
outputFile:write("-- Total missing: " .. table.getn(missingInQuestie) .. " quests\n")
outputFile:close()

-- Generate update suggestions for placeholder names
print("\n=== QUESTS WITH PLACEHOLDER NAMES TO UPDATE ===")
local updateFile = io.open(questiePath .. "pfquest_name_updates.lua", "w")
updateFile:write("-- Quests with placeholder names that can be updated from pfQuest-epoch\n")
updateFile:write("-- Generated on " .. os.date() .. "\n\n")
updateFile:write("local nameUpdates = {\n")

count = 0
for questId, questInfo in pairs(missingNames) do
    if count < 20 then
        local text = questInfo.text or {}
        if text.T then
            print(string.format("  [%d] = \"%s\" -> \"%s\"", 
                questId, questInfo.questieEntry[1], text.T))
            
            updateFile:write(string.format('  [%d] = {current = "%s", updated = "%s"},\n',
                questId, questInfo.questieEntry[1], text.T))
            count = count + 1
        end
    end
end

updateFile:write("}\n\n")
updateFile:write("-- Total with placeholder names: " .. table.getn(missingNames) .. " quests\n")
updateFile:close()

print("\n=== FILES GENERATED ===")
print("1. pfquest_missing_quests.lua - Quests to add to Questie")
print("2. pfquest_name_updates.lua - Quest names to update in Questie")
print("\nReview these files to see conversion suggestions!")