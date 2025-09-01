---@class QuestieDataCollector
local QuestieDataCollector = QuestieLoader:CreateModule("QuestieDataCollector")

---@type QuestieDB
local QuestieDB = QuestieLoader:ImportModule("QuestieDB")
---@type QuestieLib
local QuestieLib = QuestieLoader:ImportModule("QuestieLib")
---@type QuestieQuest
local QuestieQuest = QuestieLoader:ImportModule("QuestieQuest")
---@type ZoneDB
local ZoneDB = QuestieLoader:ImportModule("ZoneDB")

-- Compatibility reassignments (following codebase pattern)
local C_Timer = QuestieCompat.C_Timer

-- Version control - only accept data from this version or later
local MINIMUM_VERSION = "1.1.0"
local CURRENT_VERSION = "1.1.0"

-- SavedVariables table for collected data
-- This will be initialized after ADDON_LOADED event

local _activeTracking = {} -- Currently tracking these quest IDs
local _lastQuestGiver = nil -- Store last NPC interacted with
local _questAcceptCoords = {} -- Store coordinates when accepting quests
local _originalTooltipSettings = nil -- Store original tooltip settings for restoration
local _recentKills = {} -- Store recent combat kills for objective correlation
local _initialized = false -- Track if we've initialized
local _currentLootSource = nil -- Track what we're currently looting from
local _lastInteractedObject = nil -- Track last object we moused over
local _dataMismatches = {} -- Track database mismatches for reporting
local _serviceNPCs = {} -- Track service NPCs (vendors, trainers, etc)
local _mailboxes = {} -- Track mailbox locations
local _pendingXPReward = nil -- Track XP reward for quest turn-in

-- Forward declaration of helper function for creating clickable quest data links
local CreateQuestDataLink

-- Helper function for debug messages
local function DebugMessage(msg, r, g, b)
    -- Check if this is a [DEBUG] or [DataCollector Debug] message
    if string.find(msg, "%[DEBUG%]") or string.find(msg, "%[DataCollector Debug%]") then
        if Questie.db and Questie.db.profile and Questie.db.profile.showDataCollectionMessages then
            DEFAULT_CHAT_FRAME:AddMessage(msg, r or 1, g or 1, b or 1)
        end
        return
    end
    
    -- Check if this is a [DATA] message
    if string.find(msg, "%[DATA%]") then
        -- [DATA] messages only show if showDataCollectionMessages is enabled
        if Questie.db and Questie.db.profile and Questie.db.profile.showDataCollectionMessages then
            DEFAULT_CHAT_FRAME:AddMessage(msg, r or 1, g or 1, b or 1)
        end
    else
        -- Regular debug messages show if debugDataCollector is enabled
        if Questie.db and Questie.db.profile and Questie.db.profile.debugDataCollector then
            DEFAULT_CHAT_FRAME:AddMessage(msg, r or 1, g or 1, b or 1)
        end
    end
end

-- Helper function to validate zone data
local function ValidateZoneData(questId, expectedZone, actualZone)
    if not expectedZone or not actualZone then
        return true -- Can't validate without data
    end
    
    if expectedZone ~= actualZone then
        DebugMessage("|cFFFF0000[DATA VALIDATION WARNING]|r Quest " .. questId .. " expected zone '" .. expectedZone .. "' but got '" .. actualZone .. "'", 1, 0, 0)
        
        -- Record the mismatch
        if not _dataMismatches[questId] then
            _dataMismatches[questId] = {}
        end
        _dataMismatches[questId].zoneExpected = expectedZone
        _dataMismatches[questId].zoneActual = actualZone
        
        return false
    end
    
    return true
end

-- Helper function to check if quest exists in database
local function IsQuestInDatabase(questId)
    -- If dev mode is enabled, pretend no quests are in database (collect everything)
    if Questie.db.profile.dataCollectionDevMode then
        return false
    end
    
    local questData = QuestieDB.GetQuest(questId)
    return questData and questData.name and questData.name ~= "[Epoch] Quest " .. questId
end

-- Helper function to check for database mismatches
local function CheckDatabaseMismatch(entityType, entityId, fieldName, collectedValue, databaseValue)
    if not collectedValue or not databaseValue then
        return false
    end
    
    -- Compare values (handle different types)
    local mismatch = false
    if type(collectedValue) ~= type(databaseValue) then
        mismatch = true
    elseif type(collectedValue) == "table" then
        -- For coordinates, check if they're significantly different
        if collectedValue.x and databaseValue.x then
            local xDiff = math.abs(collectedValue.x - databaseValue.x)
            local yDiff = math.abs(collectedValue.y - databaseValue.y)
            if xDiff > 1 or yDiff > 1 then -- Allow 1% tolerance
                mismatch = true
            end
        end
    else
        mismatch = (collectedValue ~= databaseValue)
    end
    
    if mismatch then
        local key = entityType .. "_" .. entityId .. "_" .. fieldName
        if not _dataMismatches[key] then
            _dataMismatches[key] = {
                entityType = entityType,
                entityId = entityId,
                fieldName = fieldName,
                collectedValue = collectedValue,
                databaseValue = databaseValue,
                timestamp = time()
            }
            
            DebugMessage("|cFFFFAA00[DATABASE MISMATCH]|r " .. entityType .. " " .. entityId .. " field '" .. fieldName .. "': DB has '" .. tostring(databaseValue) .. "' but found '" .. tostring(collectedValue) .. "'", 1, 0.7, 0)
        end
        return true
    end
    
    return false
end

function QuestieDataCollector:Initialize()
    -- Prevent double initialization
    if _initialized then
        return
    end
    
    -- Only initialize if explicitly enabled
    if not Questie or not Questie.db or not Questie.db.profile.enableDataCollection then
        return
    end
    
    -- Create or ensure the global SavedVariable exists
    -- This happens AFTER SavedVariables are loaded
    if type(QuestieDataCollection) ~= "table" then
        _G.QuestieDataCollection = {}
    end
    if not QuestieDataCollection.quests then
        QuestieDataCollection.quests = {}
    end
    if not QuestieDataCollection.mismatches then
        QuestieDataCollection.mismatches = {}
    end
    if not QuestieDataCollection.serviceNPCs then
        QuestieDataCollection.serviceNPCs = {}
    end
    if not QuestieDataCollection.mailboxes then
        QuestieDataCollection.mailboxes = {}
    end
    if not QuestieDataCollection.version then
        QuestieDataCollection.version = CURRENT_VERSION
    end
    if not QuestieDataCollection.sessionStart then
        QuestieDataCollection.sessionStart = date("%Y-%m-%d %H:%M:%S")
    end
    
    -- Update version for existing data
    QuestieDataCollection.version = CURRENT_VERSION
    
    -- Count tracked quests (only missing ones)
    local questCount = 0
    local inDatabaseCount = 0
    for questId in pairs(QuestieDataCollection.quests) do
        if not IsQuestInDatabase(questId) then
            questCount = questCount + 1
        else
            inDatabaseCount = inDatabaseCount + 1
        end
    end
    
    -- Hook into events
    QuestieDataCollector:RegisterEvents()
    
    -- Hook tooltip to capture object names on mouseover
    -- This helps identify containers/objects before we interact with them
    if not _tooltipHooked then
        GameTooltip:HookScript("OnShow", function()
            if GameTooltip:IsVisible() then
                local name = GameTooltipTextLeft1:GetText()
                if name and name ~= "" then
                    -- Store as potential object we might interact with
                    _lastInteractedObject = {
                        name = name,
                        timestamp = time()
                    }
                end
            end
        end)
        _tooltipHooked = true
    end
    
    -- Enable tooltip IDs
    QuestieDataCollector:EnableTooltipIDs()
    
    -- Only show messages on first initialization, not after login
    if not _initialized then
        DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[Questie Data Collector v" .. CURRENT_VERSION .. "]|r Ready!", 0, 1, 0)
        
        if Questie.db.profile.dataCollectionDevMode then
            DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[DEV MODE] Collecting ALL quests (including known ones)|r", 1, 0, 0)
        else
            DEFAULT_CHAT_FRAME:AddMessage("|cFFFFFF00Now only tracking quests MISSING from database|r", 1, 1, 0)
        end
        
        DEFAULT_CHAT_FRAME:AddMessage("|cFFFFFF00Mismatch detection enabled for improved accuracy|r", 1, 1, 0)
        
        if questCount > 0 then
            DEFAULT_CHAT_FRAME:AddMessage("|cFF00FFFF" .. questCount .. " missing quests being tracked|r", 0, 1, 1)
        end
        if inDatabaseCount > 0 and not Questie.db.profile.dataCollectionDevMode then
            DEFAULT_CHAT_FRAME:AddMessage("|cFFFFAA00Note: " .. inDatabaseCount .. " tracked quests are now in database and won't be collected|r", 1, 0.7, 0)
        end
        DEFAULT_CHAT_FRAME:AddMessage("|cFFFFFF00Type /qdc for commands|r", 1, 1, 0)
    end
    
    _initialized = true
    
    -- Wait for Questie to be fully initialized before checking quests
    if not Questie.started then
        C_Timer.After(5, function()
            QuestieDataCollector:CheckActiveQuests()
        end)
    else
        QuestieDataCollector:CheckActiveQuests()
    end
end

-- Store zone data properly
local function GetCurrentZoneData()
    local zoneData = {}
    
    -- Get zone text directly from API
    zoneData.zone = GetZoneText()
    zoneData.subZone = GetSubZoneText()
    zoneData.realZone = GetRealZoneText()
    
    -- Get map IDs
    local mapId = nil
    if WorldMapFrame and WorldMapFrame.GetMapID then
        mapId = WorldMapFrame:GetMapID()
    end
    
    -- Get area ID from current position
    local areaId = nil
    if GetCurrentMapAreaID then
        areaId = GetCurrentMapAreaID()
    end
    
    -- Try to get Questie's zone ID (only if we have a valid mapId)
    local questieZoneId = nil
    if mapId and ZoneDB and ZoneDB.GetAreaIdByUiMapId then
        -- Use pcall to safely handle any errors from ZoneDB
        local success, result = pcall(function()
            return ZoneDB:GetAreaIdByUiMapId(mapId)
        end)
        if success then
            questieZoneId = result
        end
    end
    
    zoneData.mapId = mapId
    zoneData.areaId = areaId or questieZoneId
    zoneData.questieZoneId = questieZoneId
    
    -- Get coordinates
    local coords = QuestieDataCollector:GetPlayerCoordinates()
    if coords then
        zoneData.x = coords.x
        zoneData.y = coords.y
    end
    
    return zoneData
end

-- Enhanced coordinate capture with zone validation
function QuestieDataCollector:GetPlayerCoordinates()
    local x, y = nil, nil
    
    -- Try QuestieCoords first
    if QuestieCoords and QuestieCoords.GetPlayerMapPosition then
        x, y = QuestieCoords.GetPlayerMapPosition()
    end
    
    -- Fallback to standard API
    if not x or not y then
        x, y = GetPlayerMapPosition("player")
    end
    
    if x and y and x > 0 and y > 0 then
        -- Safely get zone data
        local success, zoneData = pcall(GetCurrentZoneData)
        if not success or not zoneData then
            -- Return coordinates without zone data if there's an error
            return {
                x = math.floor(x * 1000) / 10, -- Convert to percentage with 1 decimal
                y = math.floor(y * 1000) / 10,
                zone = "Unknown",
                subZone = "",
                areaId = nil,
                mapId = nil
            }
        end
        
        return {
            x = math.floor(x * 1000) / 10, -- Convert to percentage with 1 decimal
            y = math.floor(y * 1000) / 10,
            zone = zoneData.zone or "Unknown",
            subZone = zoneData.subZone or "",
            areaId = zoneData.areaId,
            mapId = zoneData.mapId
        }
    end
    
    return nil
end

function QuestieDataCollector:RegisterEvents()
    local frame = CreateFrame("Frame")
    
    -- Quest events
    frame:RegisterEvent("QUEST_ACCEPTED")
    frame:RegisterEvent("QUEST_COMPLETE")
    frame:RegisterEvent("QUEST_TURNED_IN")
    frame:RegisterEvent("QUEST_LOG_UPDATE")
    
    -- NPC interaction events
    frame:RegisterEvent("GOSSIP_SHOW")
    frame:RegisterEvent("QUEST_DETAIL")
    frame:RegisterEvent("QUEST_GREETING")
    frame:RegisterEvent("QUEST_PROGRESS")
    frame:RegisterEvent("QUEST_FINISHED")
    
    -- Combat and loot events for tracking mob kills and item sources
    frame:RegisterEvent("COMBAT_LOG_EVENT_UNFILTERED")
    frame:RegisterEvent("LOOT_OPENED")
    frame:RegisterEvent("CHAT_MSG_LOOT")
    frame:RegisterEvent("ITEM_PUSH")
    
    -- Targeting events for mob tracking
    frame:RegisterEvent("PLAYER_TARGET_CHANGED")
    frame:RegisterEvent("UPDATE_MOUSEOVER_UNIT")
    
    -- Service NPC events
    frame:RegisterEvent("MERCHANT_SHOW")
    frame:RegisterEvent("MERCHANT_CLOSED")
    frame:RegisterEvent("TRAINER_SHOW")
    frame:RegisterEvent("TRAINER_CLOSED")
    frame:RegisterEvent("MAIL_SHOW")
    frame:RegisterEvent("MAIL_CLOSED")
    frame:RegisterEvent("BANKFRAME_OPENED")
    frame:RegisterEvent("BANKFRAME_CLOSED")
    frame:RegisterEvent("GUILDBANKFRAME_OPENED")
    frame:RegisterEvent("GUILDBANKFRAME_CLOSED")
    
    -- XP tracking events
    frame:RegisterEvent("CHAT_MSG_COMBAT_XP_GAIN")
    frame:RegisterEvent("CHAT_MSG_SYSTEM")
    
    frame:SetScript("OnEvent", function(self, event, ...)
        QuestieDataCollector:OnEvent(event, ...)
    end)
end

function QuestieDataCollector:OnEvent(event, ...)
    if not Questie.db.profile.enableDataCollection then
        return
    end
    
    if event == "QUEST_ACCEPTED" then
        local questIndex, questId = ...
        
        -- In WoW 3.3.5, QUEST_ACCEPTED doesn't always provide questId
        -- We need to get it from the quest log (position 9)
        if not questId or questId == 0 then
            -- GetQuestLogTitle returns: title, level, tag, isHeader, isCollapsed, isComplete, frequency, unknown, questID (9th position)
            local _, _, _, _, _, _, _, _, retrievedQuestId = GetQuestLogTitle(questIndex)
            questId = retrievedQuestId
        end
        
        -- Ensure we have a valid quest ID
        if not questId or questId == 0 then
            DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[DATA ERROR]|r Could not get quest ID for index " .. tostring(questIndex), 1, 0, 0)
            return
        end
        
        -- Skip if quest is already in database
        if IsQuestInDatabase(questId) then
            DebugMessage("|cFFFFAA00[DATA]|r Quest " .. questId .. " already in database, skipping collection", 1, 0.7, 0)
            return
        end
        
        QuestieDataCollector:TrackQuestAccepted(questIndex, questId)
        
    elseif event == "QUEST_COMPLETE" then
        QuestieDataCollector:TrackQuestComplete()
        
    elseif event == "QUEST_TURNED_IN" then
        local questId, xpReward, moneyReward = ...
        
        -- Store XP if provided directly in event (newer WoW versions)
        if xpReward and xpReward > 0 then
            _pendingXPReward = xpReward
        end
        
        -- Sometimes questId is nil, try to get from recently completed quest
        if not questId or questId == 0 then
            -- Method 1: Find the most recently completed quest that's being tracked
            local mostRecentTime = 0
            local mostRecentId = nil
            for qId in pairs(_activeTracking) do
                local qData = QuestieDataCollection.quests[qId]
                if qData and qData.completedTimestamp and qData.completedTimestamp > mostRecentTime then
                    mostRecentTime = qData.completedTimestamp
                    mostRecentId = qId
                end
            end
            if mostRecentId and (time() - mostRecentTime) < 10 then -- Increased time window
                questId = mostRecentId
                DebugMessage("|cFFFFFF00[DATA]|r Using recently completed quest ID: " .. questId, 1, 1, 0)
            end
        end
        
        -- Method 2: If still no quest ID, check for any active quest with a pending XP reward
        if (not questId or questId == 0) and _pendingXPReward then
            -- Find any active quest that could be turning in
            for qId in pairs(_activeTracking) do
                local qData = QuestieDataCollection.quests[qId]
                -- If there's only one active quest, assume it's the one
                if qData and not qData.turnedIn then
                    questId = qId
                    DebugMessage("|cFFFFFF00[DATA]|r Using active quest ID from pending XP: " .. questId, 1, 1, 0)
                    break
                end
            end
        end
        
        if questId and _activeTracking[questId] then
            QuestieDataCollector:TrackQuestTurnIn(questId)
        elseif _pendingXPReward then
            -- We have XP but couldn't find the quest
            DebugMessage("|cFFFF0000[DATA ERROR]|r Have pending XP reward but couldn't determine quest ID", 1, 0, 0)
        end
        
    elseif event == "QUEST_LOG_UPDATE" then
        QuestieDataCollector:CheckQuestProgress()
        
    elseif event == "GOSSIP_SHOW" or event == "QUEST_DETAIL" or event == "QUEST_GREETING" then
        QuestieDataCollector:CaptureNPCInfo()
        
    elseif event == "PLAYER_TARGET_CHANGED" then
        QuestieDataCollector:TrackTargetedMob()
        
    elseif event == "UPDATE_MOUSEOVER_UNIT" then
        QuestieDataCollector:TrackMouseoverUnit()
        
    elseif event == "COMBAT_LOG_EVENT_UNFILTERED" then
        QuestieDataCollector:HandleCombatEvent(...)
        
    elseif event == "LOOT_OPENED" then
        QuestieDataCollector:HandleLootOpened()
        
    elseif event == "CHAT_MSG_LOOT" then
        local message = ...
        QuestieDataCollector:HandleLootMessage(message)
        
    elseif event == "ITEM_PUSH" then
        local bagSlot, iconPath = ...
        QuestieDataCollector:HandleItemPush(bagSlot, iconPath)
        
    elseif event == "MERCHANT_SHOW" then
        QuestieDataCollector:CaptureServiceNPC("vendor")
        
    elseif event == "TRAINER_SHOW" then
        QuestieDataCollector:CaptureServiceNPC("trainer")
        
    elseif event == "MAIL_SHOW" then
        QuestieDataCollector:CaptureMailbox()
        
    elseif event == "BANKFRAME_OPENED" then
        QuestieDataCollector:CaptureServiceNPC("banker")
        
    elseif event == "GUILDBANKFRAME_OPENED" then
        QuestieDataCollector:CaptureServiceNPC("guild_banker")
        
    elseif event == "CHAT_MSG_COMBAT_XP_GAIN" then
        local message = ...
        -- Parse XP from quest completion: "Experience gained: 450."
        local xp = string.match(message, "Experience gained: (%d+)")
        if xp then
            _pendingXPReward = tonumber(xp)
            -- XP message comes right before QUEST_TURNED_IN, so we store it temporarily
            DebugMessage("|cFF00FFFF[DATA]|r Captured XP reward: " .. xp, 0, 1, 1)
        end
        
    elseif event == "CHAT_MSG_SYSTEM" then
        local message = ...
        -- Also check system messages for XP (sometimes comes through here)
        local xp = string.match(message, "Experience gained: (%d+)")
        if xp then
            _pendingXPReward = tonumber(xp)
            DebugMessage("|cFF00FFFF[DATA]|r Captured XP reward: " .. xp, 0, 1, 1)
        end
    end
end

function QuestieDataCollector:TrackQuestAccepted(questIndex, questId)
    if not questId or questId == 0 then
        return
    end
    
    -- Skip if quest is already in database
    if IsQuestInDatabase(questId) then
        DebugMessage("|cFFFFAA00[DATA]|r Quest " .. questId .. " already in database, skipping collection", 1, 0.7, 0)
        return
    end
    
    local questName = GetQuestLogTitle(questIndex)
    if not questName then
        return
    end
    
    DebugMessage("|cFF00FF00[DATA]|r Tracking quest accepted: " .. questName .. " (ID: " .. questId .. ")", 0, 1, 0)
    
    -- Initialize quest data if needed
    if not QuestieDataCollection.quests[questId] then
        QuestieDataCollection.quests[questId] = {
            id = questId,
            objectives = {},
            mobs = {},
            items = {},
            objects = {},
            mismatches = {}
        }
    end
    
    local questData = QuestieDataCollection.quests[questId]
    
    -- Store quest info
    questData.name = questName
    questData.acceptedTimestamp = time()
    questData.acceptedDate = date("%Y-%m-%d %H:%M:%S")
    
    -- Get quest level and objectives text
    local level, questTag, _, _, _, _, _, _ = select(2, GetQuestLogTitle(questIndex))
    questData.level = level
    questData.tag = questTag
    
    -- Try to get objectives text
    SelectQuestLogEntry(questIndex)
    local questDescription, objectivesText = GetQuestLogQuestText()
    if questDescription and questDescription ~= "" then
        questData.questDescription = questDescription
    end
    if objectivesText and objectivesText ~= "" then
        questData.objectivesText = objectivesText
    end
    
    -- Store zone data when accepting
    local zoneData = GetCurrentZoneData()
    if zoneData then
        questData.acceptZone = zoneData.zone
        questData.acceptSubZone = zoneData.subZone
        questData.acceptAreaId = zoneData.areaId
        
        -- Store coordinates for quest acceptance
        if zoneData.x and zoneData.y then
            _questAcceptCoords[questId] = {
                x = zoneData.x,
                y = zoneData.y,
                zone = zoneData.zone,
                subZone = zoneData.subZone,
                areaId = zoneData.areaId
            }
        end
    end
    
    -- Capture quest giver info (if we have it)
    -- Increased time window to 10 seconds for better capture reliability
    if _lastQuestGiver and (_lastQuestGiver.timestamp and (time() - _lastQuestGiver.timestamp) < 10) then
        questData.questGiver = {
            id = _lastQuestGiver.id,
            name = _lastQuestGiver.name,
            coords = _lastQuestGiver.coords
        }
        DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[DATA]|r Quest Giver: " .. _lastQuestGiver.name .. " (ID: " .. _lastQuestGiver.id .. ")", 0, 1, 0)
        
        -- Check for database mismatch
        local dbQuest = QuestieDB.GetQuest(questId)
        if dbQuest and dbQuest.startedBy and dbQuest.startedBy[1] then
            local dbNpcIds = dbQuest.startedBy[1]
            if dbNpcIds and #dbNpcIds > 0 then
                local found = false
                for _, npcId in ipairs(dbNpcIds) do
                    if npcId == _lastQuestGiver.id then
                        found = true
                        break
                    end
                end
                if not found then
                    CheckDatabaseMismatch("quest", questId, "questGiver", _lastQuestGiver.id, dbNpcIds[1])
                end
            end
        end
        
        DebugMessage("|cFF00FF00[DATA]|r Quest Giver: " .. (_lastQuestGiver.name or "Unknown") .. " (ID: " .. (_lastQuestGiver.id or 0) .. ")", 0, 1, 0)
    else
        DebugMessage("|cFFFFFF00[DATA]|r Warning: Quest giver not captured for quest " .. questId, 1, 1, 0)
    end
    
    -- Clear objectives to prevent duplicates if re-accepting
    questData.objectives = {}
    
    -- Get quest objectives
    SelectQuestLogEntry(questIndex)
    local numObjectives = GetNumQuestLeaderBoards(questIndex)
    
    for i = 1, numObjectives do
        local text, objectiveType, finished = GetQuestLogLeaderBoard(i, questIndex)
        if text then
            table.insert(questData.objectives, {
                index = i,
                text = text,
                type = objectiveType,
                finished = finished,
                progress = {}
            })
            DebugMessage("|cFF00FFFF[DATA]|r Objective " .. i .. ": " .. text, 0, 1, 1)
        end
    end
    
    -- Get quest text
    local _, questText = GetQuestLogQuestText()
    if questText then
        questData.questText = questText
    end
    
    -- Mark as actively tracking
    _activeTracking[questId] = true
    
    DebugMessage("|cFF00FF00[DATA]|r Now tracking quest: " .. questName .. " (ID: " .. questId .. ")", 0, 1, 0)
    
    -- Always show this message to confirm tracking
    DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[DATA]|r Quest tracked: " .. questName .. " (ID: " .. questId .. ")", 0, 1, 0)
end

function QuestieDataCollector:TrackQuestComplete()
    -- CRITICAL: Capture the NPC immediately when QUEST_COMPLETE fires
    -- This happens when you click "Complete Quest" at the turn-in NPC
    QuestieDataCollector:CaptureNPCInfo()
    DebugMessage("|cFF00FFFF[DATA]|r QUEST_COMPLETE event - capturing turn-in NPC", 0, 1, 1)
    
    -- Try to identify which quest is being turned in
    -- Scan the quest log for complete quests that we're tracking
    local questId = nil
    local questName = nil
    
    for i = 1, GetNumQuestLogEntries() do
        local title, level, tag, isHeader, _, isComplete, _, _, qID = GetQuestLogTitle(i)
        -- Check if this quest is complete and we're tracking it
        if not isHeader and isComplete and _activeTracking[qID] then
            questId = qID
            questName = title
            DebugMessage("|cFF00FF00[DATA]|r Found completed quest: " .. questName .. " (ID: " .. questId .. ")", 0, 1, 0)
            break
        end
    end
    
    -- Fallback: Try GetQuestID if available
    if not questId or questId == 0 then
        questId = GetQuestID and GetQuestID() or nil
        if questId then
            DebugMessage("|cFFFFFF00[DATA]|r Got quest ID from GetQuestID: " .. questId, 1, 1, 0)
        end
    end
    
    -- Fallback: Try to get from the complete dialog title
    if not questId or questId == 0 then
        local questTitle = GetTitleText and GetTitleText() or nil
        if questTitle then
            for qId, qData in pairs(QuestieDataCollection.quests) do
                if qData.name == questTitle and _activeTracking[qId] then
                    questId = qId
                    questName = questTitle
                    DebugMessage("|cFFFFFF00[DATA]|r Found quest ID from title: " .. questId .. " (" .. questTitle .. ")", 1, 1, 0)
                    break
                end
            end
        end
    end
    
    if not questId or questId == 0 then
        DebugMessage("|cFFFF0000[DATA ERROR]|r Could not determine quest ID for completion", 1, 0, 0)
        return
    end
    
    -- Skip if quest is already in database
    if IsQuestInDatabase(questId) then
        return
    end
    
    if not _activeTracking[questId] then
        return
    end
    
    local questData = QuestieDataCollection.quests[questId]
    if not questData then
        return
    end
    
    questData.completedTimestamp = time()
    questData.completedDate = date("%Y-%m-%d %H:%M:%S")
    
    -- Capture turn-in NPC if available (increased window to 10 seconds)
    if _lastQuestGiver and (_lastQuestGiver.timestamp and (time() - _lastQuestGiver.timestamp) < 10) then
        questData.turnInNpc = {
            id = _lastQuestGiver.id,
            name = _lastQuestGiver.name,
            coords = _lastQuestGiver.coords
        }
        
        -- Check for database mismatch
        local dbQuest = QuestieDB.GetQuest(questId)
        if dbQuest and dbQuest.finishedBy and dbQuest.finishedBy[1] then
            local dbNpcIds = dbQuest.finishedBy[1]
            if dbNpcIds and #dbNpcIds > 0 then
                local found = false
                for _, npcId in ipairs(dbNpcIds) do
                    if npcId == _lastQuestGiver.id then
                        found = true
                        break
                    end
                end
                if not found then
                    CheckDatabaseMismatch("quest", questId, "turnInNpc", _lastQuestGiver.id, dbNpcIds[1])
                end
            end
        end
        
        DebugMessage("|cFF00FF00[DATA]|r Turn-in NPC: " .. (_lastQuestGiver.name or "Unknown") .. " (ID: " .. (_lastQuestGiver.id or 0) .. ")", 0, 1, 0)
    end
    
    -- Store completion zone data
    local zoneData = GetCurrentZoneData()
    if zoneData then
        questData.turnInZone = zoneData.zone
        questData.turnInSubZone = zoneData.subZone
        questData.turnInAreaId = zoneData.areaId
        
        if zoneData.x and zoneData.y then
            questData.turnInCoords = {
                x = zoneData.x,
                y = zoneData.y,
                zone = zoneData.zone,
                subZone = zoneData.subZone,
                areaId = zoneData.areaId
            }
        end
    end
    
    DebugMessage("|cFF00FF00[DATA]|r Quest completed: " .. (questData.name or "Unknown") .. " (ID: " .. questId .. ")", 0, 1, 0)
end

function QuestieDataCollector:TrackQuestTurnIn(questId)
    if not questId or questId == 0 then
        return
    end
    
    -- Skip if quest is already in database
    if IsQuestInDatabase(questId) then
        return
    end
    
    if not _activeTracking[questId] then
        return
    end
    
    local questData = QuestieDataCollection.quests[questId]
    if not questData then
        return
    end
    
    -- Mark quest as turned in
    questData.turnedIn = true
    questData.turnInTimestamp = time()
    questData.turnInDate = date("%Y-%m-%d %H:%M:%S")
    
    -- Capture XP reward if we have it
    if _pendingXPReward and _pendingXPReward > 0 then
        questData.xpReward = _pendingXPReward
        DebugMessage("|cFF00FFFF[DATA]|r Quest XP reward: " .. _pendingXPReward, 0, 1, 1)
        _pendingXPReward = nil -- Clear it after using
    end
    
    -- Remove from active tracking
    _activeTracking[questId] = nil
    
    DebugMessage("|cFF00FF00[DATA]|r Quest turned in: " .. (questData.name or "Unknown") .. " (ID: " .. questId .. ")", 0, 1, 0)
end

function QuestieDataCollector:CheckQuestProgress()
    for questId in pairs(_activeTracking) do
        -- Skip if quest is now in database
        if IsQuestInDatabase(questId) then
            _activeTracking[questId] = nil
            DebugMessage("|cFFFFAA00[DATA]|r Quest " .. questId .. " now in database, stopping collection", 1, 0.7, 0)
        else
            QuestieDataCollector:UpdateQuestObjectives(questId)
        end
    end
end

function QuestieDataCollector:UpdateQuestObjectives(questId)
    local questData = QuestieDataCollection.quests[questId]
    if not questData then
        return
    end
    
    -- Find quest in log
    local questIndex = nil
    for i = 1, GetNumQuestLogEntries() do
        local _, _, _, _, _, _, _, qId = GetQuestLogTitle(i)
        if qId == questId then
            questIndex = i
            break
        end
    end
    
    if not questIndex then
        return
    end
    
    SelectQuestLogEntry(questIndex)
    local numObjectives = GetNumQuestLeaderBoards(questIndex)
    
    for i = 1, numObjectives do
        local text, objectiveType, finished = GetQuestLogLeaderBoard(i, questIndex)
        if text and questData.objectives[i] then
            local objective = questData.objectives[i]
            
            -- Check if progress changed
            if objective.text ~= text or objective.finished ~= finished then
                -- Capture location of progress
                local coords = QuestieDataCollector:GetPlayerCoordinates()
                if coords then
                    table.insert(objective.progress, {
                        text = text,
                        finished = finished,
                        timestamp = time(),
                        coords = coords
                    })
                    
                    DebugMessage("|cFF00FFFF[DATA]|r Objective progress: " .. text, 0, 1, 1)
                end
                
                -- Update objective
                objective.text = text
                objective.finished = finished
            end
        end
    end
end

function QuestieDataCollector:CaptureNPCInfo()
    -- Try multiple unit types to capture NPC info
    local guid = UnitGUID("target") or UnitGUID("npc") or UnitGUID("questnpc") or UnitGUID("mouseover")
    if not guid then
        -- As a fallback, if we're in a quest dialog, try to get the NPC another way
        local npcName = GetUnitName("questnpc") or GetUnitName("npc")
        if npcName then
            DEFAULT_CHAT_FRAME:AddMessage("|cFFFFFF00[DATA]|r Captured NPC by name: " .. npcName, 1, 1, 0)
        end
        return
    end
    
    -- Extract NPC ID from GUID (WoW 3.3.5 format)
    local npcId = tonumber(guid:sub(6, 12), 16)
    if not npcId or npcId == 0 then
        return
    end
    
    local npcName = UnitName("target") or UnitName("npc") or UnitName("questnpc") or UnitName("mouseover")
    if not npcName then
        return
    end
    
    -- Get coordinates
    local coords = QuestieDataCollector:GetPlayerCoordinates()
    
    -- Store as last quest giver
    _lastQuestGiver = {
        id = npcId,
        name = npcName,
        timestamp = time(),
        coords = coords
    }
    
    DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[DATA]|r Captured NPC: " .. npcName .. " (ID: " .. npcId .. ")", 0, 1, 0)
    
    -- Check for database mismatch
    local dbNpc = QuestieDB:GetNPC(npcId)
    if dbNpc then
        if dbNpc.name and dbNpc.name ~= npcName then
            CheckDatabaseMismatch("npc", npcId, "name", npcName, dbNpc.name)
        end
        
        -- Check zone and coordinate mismatches if we have coordinates
        if coords and coords.areaId and dbNpc.spawns then
            local foundZone = false
            local closestDistance = 9999
            
            for zoneId, spawns in pairs(dbNpc.spawns) do
                if zoneId == coords.areaId then
                    foundZone = true
                    
                    -- Check coordinate accuracy within this zone
                    if spawns and type(spawns) == "table" then
                        for _, spawn in ipairs(spawns) do
                            if spawn and spawn[1] and spawn[2] then
                                local xDiff = math.abs(coords.x - spawn[1])
                                local yDiff = math.abs(coords.y - spawn[2])
                                local distance = math.sqrt(xDiff * xDiff + yDiff * yDiff)
                                
                                if distance < closestDistance then
                                    closestDistance = distance
                                end
                            end
                        end
                    end
                    break
                end
            end
            
            -- Report zone mismatch
            if not foundZone then
                CheckDatabaseMismatch("npc", npcId, "zone", coords.areaId, next(dbNpc.spawns))
            end
            
            -- Report coordinate mismatch if NPC is too far from any known spawn
            -- Using 10% distance threshold (10 units in 0-100 coordinate system)
            -- This avoids false positives from minor movement or patrol paths
            if foundZone and closestDistance > 10 then
                CheckDatabaseMismatch("npc", npcId, "coords", 
                    {x = coords.x, y = coords.y}, 
                    {distance = closestDistance})
                DebugMessage("|cFFFFAA00[DATA MISMATCH]|r NPC " .. npcId .. " found " .. string.format("%.1f", closestDistance) .. " units from nearest DB spawn", 1, 0.7, 0)
            end
        end
    end
    
    DebugMessage("|cFF00FF00[DATA]|r Captured NPC: " .. npcName .. " (ID: " .. npcId .. ")", 0, 1, 0)
end

function QuestieDataCollector:TrackTargetedMob()
    if not UnitExists("target") or UnitIsPlayer("target") or UnitIsFriend("player", "target") then
        return
    end
    
    local guid = UnitGUID("target")
    if not guid then
        return
    end
    
    -- Extract NPC ID from GUID
    local npcId = tonumber(guid:sub(6, 12), 16)
    if not npcId or npcId == 0 then
        return
    end
    
    local npcName = UnitName("target")
    local npcLevel = UnitLevel("target")
    
    -- Get coordinates
    local coords = QuestieDataCollector:GetPlayerCoordinates()
    
    -- Check all tracked quests to see if this mob is relevant
    for questId in pairs(_activeTracking) do
        -- Skip if quest is now in database
        if not IsQuestInDatabase(questId) then
            local questData = QuestieDataCollection.quests[questId]
            if questData then
                -- Store mob info
                if not questData.mobs[npcId] then
                    questData.mobs[npcId] = {
                        id = npcId,
                        name = npcName,
                        level = npcLevel,
                        locations = {}
                    }
                end
                
                -- Add location if we have coords
                if coords then
                    table.insert(questData.mobs[npcId].locations, coords)
                end
                
                DebugMessage("|cFFAA8833[DATA]|r Tracked quest mob: " .. npcName .. " (ID: " .. npcId .. ") for quest " .. questId, 0.67, 0.53, 0.2)
            end
        end
    end
end

function QuestieDataCollector:TrackMouseoverUnit()
    if not UnitExists("mouseover") or UnitIsPlayer("mouseover") then
        return
    end
    
    local guid = UnitGUID("mouseover")
    if not guid then
        return
    end
    
    -- Check if it's an object (GameObjects have different GUID format)
    local guidType = tonumber(guid:sub(1, 5), 16)
    if guidType and bit.band(guidType, 0x00F) == 0x00B then -- GameObject type
        local objectName = UnitName("mouseover")
        if objectName then
            local coords = QuestieDataCollector:GetPlayerCoordinates()
            _lastInteractedObject = {
                name = objectName,
                timestamp = time(),
                coords = coords
            }
            
            -- Try to find object in database and check for mismatches
            -- Objects are harder to match by name since they often have generic names
            -- We'd need the object ID from the GUID, but GameObject GUIDs don't contain IDs in 3.3.5
            -- So we'll just track the location for now
            
            DebugMessage("|cFF00AAFF[DATA]|r Moused over object: " .. objectName, 0, 0.67, 1)
        end
    else
        -- It's an NPC, track it similar to targeted mob
        QuestieDataCollector:TrackTargetedMob()
    end
end

function QuestieDataCollector:HandleCombatEvent(...)
    local timestamp, event, hideCaster, sourceGUID, sourceName, sourceFlags, sourceRaidFlags, destGUID, destName = ...
    
    if event == "UNIT_DIED" or event == "PARTY_KILL" then
        if destGUID and destName then
            -- Extract NPC ID from GUID
            local npcId = tonumber(destGUID:sub(6, 12), 16)
            if npcId and npcId > 0 then
                -- Store recent kill for item correlation
                _recentKills[npcId] = {
                    name = destName,
                    timestamp = time()
                }
                
                -- Clean up old kills (older than 10 seconds)
                for id, data in pairs(_recentKills) do
                    if (time() - data.timestamp) > 10 then
                        _recentKills[id] = nil
                    end
                end
            end
        end
    end
end

function QuestieDataCollector:HandleLootOpened()
    -- Get current location
    local coords = QuestieDataCollector:GetPlayerCoordinates()
    local zone = GetRealZoneText()
    local subZone = GetSubZoneText()
    
    -- Determine what we're looting from
    local lootSourceName = nil
    local lootSourceId = nil
    local lootSourceType = nil
    
    -- Check if we're looting a corpse
    local targetGuid = UnitGUID("target")
    if targetGuid and UnitIsDead("target") then
        lootSourceName = UnitName("target")
        lootSourceId = ExtractNpcIdFromGuid(targetGuid)
        lootSourceType = "npc"
    else
        -- Try to get container name from GameTooltip
        local containerName = nil
        if GameTooltip:IsVisible() then
            local tooltipText = GameTooltipTextLeft1:GetText()
            if tooltipText and tooltipText ~= "" then
                containerName = tooltipText
            end
        end
        
        -- Check loot frame for container name
        if not containerName and LootFrame:IsVisible() then
            local lootName = GetLootSourceInfo and GetLootSourceInfo(1) or nil
            if not lootName and LootFrameTitle and LootFrameTitle:GetText() then
                lootName = LootFrameTitle:GetText()
            end
            if lootName then
                containerName = lootName
            end
        end
        
        -- Use the container name we found, or fall back to last interacted object
        if containerName and containerName ~= "" then
            lootSourceName = containerName
            lootSourceType = "object"
            -- Update _lastInteractedObject with better name
            if not _lastInteractedObject then
                _lastInteractedObject = {}
            end
            _lastInteractedObject.name = containerName
            _lastInteractedObject.timestamp = time()
        elseif _lastInteractedObject and _lastInteractedObject.name then
            lootSourceName = _lastInteractedObject.name
            lootSourceType = "object"
        else
            lootSourceName = "Ground Object"
            lootSourceType = "object"
        end
    end
    
    -- Store current loot source for item tracking
    _currentLootSource = {
        name = lootSourceName,
        id = lootSourceId,
        type = lootSourceType,
        timestamp = time()
    }
    
    -- CRITICAL: Track this object/container for ALL active quests
    -- This is how v1.0.68 builds the extensive GROUND OBJECTS list
    if lootSourceName and lootSourceType == "object" then
        for questId in pairs(_activeTracking) do
            local questData = QuestieDataCollection.quests[questId]
            if questData then
                questData.objects = questData.objects or {}
                
                -- Use object name as key for grouping locations
                if not questData.objects[lootSourceName] then
                    questData.objects[lootSourceName] = {
                        name = lootSourceName,
                        id = lootSourceId,
                        locations = {}
                    }
                end
                
                -- Add this location if we have coordinates
                if coords and coords.x and coords.y then
                    -- Use rounded coordinates as key to prevent duplicates
                    local locKey = string.format("%.1f,%.1f", coords.x, coords.y)
                    if not questData.objects[lootSourceName].locations[locKey] then
                        questData.objects[lootSourceName].locations[locKey] = {
                            x = coords.x,
                            y = coords.y,
                            zone = zone,
                            subZone = subZone,
                            timestamp = time()
                        }
                        DebugMessage("|cFF00FFFF[DATA]|r Tracked object '" .. lootSourceName .. 
                            "' at [" .. string.format("%.1f, %.1f", coords.x, coords.y) .. "] in " .. zone, 0, 1, 1)
                    end
                end
            end
        end
    end
end

function QuestieDataCollector:HandleLootMessage(message)
    -- Parse loot message for quest items
    local itemLink = string.match(message, "|c%x+|Hitem:.-|h%[(.-)%]|h|r")
    if not itemLink then
        return
    end
    
    local itemId = tonumber(string.match(message, "|Hitem:(%d+):"))
    if not itemId then
        return
    end
    
    -- Check if this is a quest item
    local isQuestItem = false
    for questId in pairs(_activeTracking) do
        if not IsQuestInDatabase(questId) then
            local questData = QuestieDataCollection.quests[questId]
            if questData then
                -- Check objectives for this item
                for _, objective in ipairs(questData.objectives or {}) do
                    if string.find(objective.text or "", itemLink) then
                        isQuestItem = true
                        
                        -- Store item info
                        if not questData.items[itemId] then
                            questData.items[itemId] = {
                                id = itemId,
                                name = itemLink,
                                sources = {}
                            }
                        end
                        
                        -- Link to source if we have one
                        if _currentLootSource and _currentLootSource.timestamp and (time() - _currentLootSource.timestamp) < 5 then
                            local source = {
                                type = _currentLootSource.type,
                                name = _currentLootSource.name,
                                id = _currentLootSource.id,
                                timestamp = time()
                            }
                            table.insert(questData.items[itemId].sources, source)
                            
                            if _currentLootSource.type == "npc" then
                                DebugMessage("|cFF00FF00[DATA]|r Quest item " .. itemLink .. " dropped from " .. (_currentLootSource.name or "Unknown"), 0, 1, 0)
                            else
                                DebugMessage("|cFF00FFFF[DATA]|r Quest item " .. itemLink .. " obtained from " .. (_currentLootSource.name or "object"), 0, 1, 1)
                            end
                        end
                        
                        break
                    end
                end
            end
        end
    end
end

function QuestieDataCollector:HandleItemPush(bagSlot, iconPath)
    -- This is called when an item is added to inventory
    -- We can use this to correlate items with recent interactions
end

function QuestieDataCollector:CaptureServiceNPC(serviceType)
    local guid = UnitGUID("target") or UnitGUID("npc")
    if not guid then
        return
    end
    
    -- Extract NPC ID from GUID (WoW 3.3.5 format)
    local npcId = tonumber(guid:sub(6, 12), 16)
    if not npcId or npcId == 0 then
        return
    end
    
    local npcName = UnitName("target") or UnitName("npc")
    if not npcName then
        return
    end
    
    -- Get coordinates
    local coords = QuestieDataCollector:GetPlayerCoordinates()
    
    -- Initialize service NPC data if needed
    if not QuestieDataCollection.serviceNPCs[npcId] then
        QuestieDataCollection.serviceNPCs[npcId] = {
            id = npcId,
            name = npcName,
            services = {},
            locations = {}
        }
    end
    
    local npcData = QuestieDataCollection.serviceNPCs[npcId]
    
    -- Update name if different
    if npcData.name ~= npcName then
        npcData.name = npcName
    end
    
    -- Add service type if not already tracked
    local hasService = false
    for _, service in ipairs(npcData.services) do
        if service == serviceType then
            hasService = true
            break
        end
    end
    if not hasService then
        table.insert(npcData.services, serviceType)
    end
    
    -- Check for additional services based on type
    if serviceType == "vendor" then
        -- Check if NPC can repair
        if CanMerchantRepair and CanMerchantRepair() then
            local hasRepair = false
            for _, service in ipairs(npcData.services) do
                if service == "repair" then
                    hasRepair = true
                    break
                end
            end
            if not hasRepair then
                table.insert(npcData.services, "repair")
            end
        end
    end
    
    -- Add location if we have coords and it's new
    if coords then
        local isNewLocation = true
        for _, loc in ipairs(npcData.locations) do
            if loc.zone == coords.zone and loc.areaId == coords.areaId then
                -- Check if coords are significantly different (more than 10 units)
                if loc.x and loc.y then
                    local distance = math.sqrt((coords.x - loc.x)^2 + (coords.y - loc.y)^2)
                    if distance < 10 then
                        isNewLocation = false
                        break
                    end
                end
            end
        end
        
        if isNewLocation then
            table.insert(npcData.locations, {
                x = coords.x,
                y = coords.y,
                zone = coords.zone,
                subZone = coords.subZone,
                areaId = coords.areaId,
                timestamp = time()
            })
        end
    end
    
    -- Check database for this service NPC
    local dbNpc = QuestieDB:GetNPC(npcId)
    if not dbNpc then
        DebugMessage("|cFF00FFFF[DATA]|r New service NPC discovered: " .. npcName .. " (ID: " .. npcId .. ") - " .. serviceType, 0, 1, 1)
    else
        -- Check if services match what's in database
        local servicesStr = table.concat(npcData.services, ", ")
        DebugMessage("|cFF00AAFF[DATA]|r Service NPC: " .. npcName .. " (ID: " .. npcId .. ") - Services: " .. servicesStr, 0, 0.67, 1)
    end
end

function QuestieDataCollector:CaptureMailbox()
    -- Mailboxes are objects, not NPCs, so we need to handle them differently
    -- We'll capture the location where the player opened mail
    local coords = QuestieDataCollector:GetPlayerCoordinates()
    if not coords then
        return
    end
    
    -- Create a unique key for this mailbox location
    local locKey = string.format("%s_%.0f_%.0f", coords.zone or "Unknown", coords.x or 0, coords.y or 0)
    
    -- Check if we already have this mailbox
    if not QuestieDataCollection.mailboxes[locKey] then
        QuestieDataCollection.mailboxes[locKey] = {
            x = coords.x,
            y = coords.y,
            zone = coords.zone,
            subZone = coords.subZone,
            areaId = coords.areaId,
            firstSeen = time(),
            lastSeen = time(),
            timesUsed = 1
        }
        
        DebugMessage("|cFF00FF00[DATA]|r New mailbox discovered at " .. string.format("%.1f, %.1f", coords.x, coords.y) .. " in " .. (coords.zone or "Unknown"), 0, 1, 0)
    else
        -- Update last seen and increment usage count
        QuestieDataCollection.mailboxes[locKey].lastSeen = time()
        QuestieDataCollection.mailboxes[locKey].timesUsed = (QuestieDataCollection.mailboxes[locKey].timesUsed or 1) + 1
    end
end

function QuestieDataCollector:CheckActiveQuests()
    -- Check all quests in the log
    local numEntries = GetNumQuestLogEntries()
    local addedQuests = 0
    local skippedQuests = 0
    
    for i = 1, numEntries do
        local title, level, tag, isHeader, isCollapsed, isComplete, frequency, questId = GetQuestLogTitle(i)
        
        if not isHeader and questId and questId > 0 then
            -- Skip if quest is already in database
            if IsQuestInDatabase(questId) then
                skippedQuests = skippedQuests + 1
            else
                -- Initialize tracking for missing quests
                if not QuestieDataCollection.quests[questId] then
                    QuestieDataCollection.quests[questId] = {
                        id = questId,
                        name = title,
                        level = level,
                        wasAlreadyAccepted = true, -- Flag that we didn't see the accept event
                        objectives = {},
                        mobs = {},
                        items = {},
                        objects = {},
                        mismatches = {}
                    }
                    
                    -- Get current objectives
                    SelectQuestLogEntry(i)
                    local numObjectives = GetNumQuestLeaderBoards(i)
                    
                    for j = 1, numObjectives do
                        local text, objectiveType, finished = GetQuestLogLeaderBoard(j, i)
                        if text then
                            table.insert(QuestieDataCollection.quests[questId].objectives, {
                                index = j,
                                text = text,
                                type = objectiveType,
                                finished = finished,
                                progress = {}
                            })
                        end
                    end
                    
                    _activeTracking[questId] = true
                    addedQuests = addedQuests + 1
                    
                    DebugMessage("|cFFFFFF00[DATA]|r Added existing quest to tracking: " .. title .. " (ID: " .. questId .. ")", 1, 1, 0)
                end
            end
        end
    end
    
    if addedQuests > 0 then
        DEFAULT_CHAT_FRAME:AddMessage("|cFF00FFFF[Data Collector]|r Added " .. addedQuests .. " missing quests from your log to tracking", 0, 1, 1)
    end
    if skippedQuests > 0 then
        DEFAULT_CHAT_FRAME:AddMessage("|cFFFFAA00[Data Collector]|r Skipped " .. skippedQuests .. " quests already in database", 1, 0.7, 0)
    end
end

function QuestieDataCollector:EnableTooltipIDs()
    -- Store original settings to restore later
    if not _originalTooltipSettings then
        _originalTooltipSettings = {
            questId = Questie.db.profile.enableTooltipsQuestID,
            npcId = Questie.db.profile.enableTooltipsNpcID,
            objectId = Questie.db.profile.enableTooltipsObjectID,
            itemId = Questie.db.profile.enableTooltipsItemID
        }
    end
    
    -- Enable all IDs in tooltips for better data collection
    Questie.db.profile.enableTooltipsQuestID = true
    Questie.db.profile.enableTooltipsNpcID = true
    Questie.db.profile.enableTooltipsObjectID = true
    Questie.db.profile.enableTooltipsItemID = true
end

function QuestieDataCollector:RestoreTooltipSettings()
    if _originalTooltipSettings then
        Questie.db.profile.enableTooltipsQuestID = _originalTooltipSettings.questId
        Questie.db.profile.enableTooltipsNpcID = _originalTooltipSettings.npcId
        Questie.db.profile.enableTooltipsObjectID = _originalTooltipSettings.objectId
        Questie.db.profile.enableTooltipsItemID = _originalTooltipSettings.itemId
        
        _originalTooltipSettings = nil
    end
end

-- Export window for batch exporting all tracked quests
function QuestieDataCollector:ShowExportWindow()
    if not QuestieDataCollection or not QuestieDataCollection.quests then
        DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[Data Collector]|r No data collected yet!", 1, 0, 0)
        return
    end
    
    -- Count quests
    local questCount = 0
    for _ in pairs(QuestieDataCollection.quests) do
        questCount = questCount + 1
    end
    
    if questCount == 0 then
        DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[Data Collector]|r No quests tracked yet!", 1, 0, 0)
        return
    end
    
    -- Create frame if it doesn't exist
    if not self.exportFrame then
        local frame = CreateFrame("Frame", "QuestieDataExportFrame", UIParent)
        frame:SetSize(600, 400)
        frame:SetPoint("CENTER")
        frame:SetFrameStrata("DIALOG")
        frame:SetMovable(true)
        frame:EnableMouse(true)
        frame:RegisterForDrag("LeftButton")
        frame:SetScript("OnDragStart", frame.StartMoving)
        frame:SetScript("OnDragStop", frame.StopMovingOrSizing)
        
        -- Background
        frame:SetBackdrop({
            bgFile = "Interface\\DialogFrame\\UI-DialogBox-Background",
            edgeFile = "Interface\\DialogFrame\\UI-DialogBox-Border",
            tile = true, tileSize = 32, edgeSize = 32,
            insets = { left = 8, right = 8, top = 8, bottom = 8 }
        })
        
        -- Title
        local title = frame:CreateFontString(nil, "OVERLAY", "GameFontNormalLarge")
        title:SetPoint("TOP", 0, -15)
        title:SetText("Quest Data Export")
        
        -- Info text
        local info = frame:CreateFontString(nil, "OVERLAY", "GameFontNormal")
        info:SetPoint("TOP", title, "BOTTOM", 0, -5)
        frame.info = info
        
        -- Scroll frame
        local scrollFrame = CreateFrame("ScrollFrame", "QuestieDataExportScrollFrame", frame, "UIPanelScrollFrameTemplate")
        scrollFrame:SetPoint("TOPLEFT", 10, -50)
        scrollFrame:SetPoint("BOTTOMRIGHT", -30, 40)
        
        -- Edit box
        local editBox = CreateFrame("EditBox", "QuestieDataExportEditBox", scrollFrame)
        editBox:SetMultiLine(true)
        editBox:SetMaxLetters(99999)
        editBox:SetFontObject(GameFontNormalSmall)
        editBox:SetWidth(550)
        editBox:SetAutoFocus(false)
        editBox:SetScript("OnEscapePressed", function() frame:Hide() end)
        scrollFrame:SetScrollChild(editBox)
        frame.editBox = editBox
        
        -- Select All button
        local selectButton = CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
        selectButton:SetSize(100, 25)
        selectButton:SetPoint("BOTTOMLEFT", 10, 10)
        selectButton:SetText("Select All")
        selectButton:SetScript("OnClick", function()
            editBox:SetFocus()
            editBox:HighlightText()
        end)
        
        -- Close button
        local closeButton = CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
        closeButton:SetSize(100, 25)
        closeButton:SetPoint("BOTTOMRIGHT", -10, 10)
        closeButton:SetText("Close")
        closeButton:SetScript("OnClick", function() frame:Hide() end)
        
        -- Submit button
        local submitButton = CreateFrame("Button", nil, frame, "UIPanelButtonTemplate")
        submitButton:SetSize(150, 25)
        submitButton:SetPoint("BOTTOM", 0, 10)
        submitButton:SetText("Copy & Open GitHub")
        submitButton:SetScript("OnClick", function()
            editBox:SetFocus()
            editBox:HighlightText()
            DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[Data Collector]|r Data selected! Press Ctrl+C to copy, then submit at:", 0, 1, 0)
            DEFAULT_CHAT_FRAME:AddMessage("|cFF00FFFF→ https://github.com/trav346/Questie/issues/new|r", 0, 1, 1)
        end)
        
        self.exportFrame = frame
    end
    
    -- Generate export text for all quests
    local exportText = "=== QUESTIE DATA COLLECTION EXPORT ===\n"
    exportText = exportText .. "Version: 1.1.0\n"
    exportText = exportText .. "Date: " .. date("%Y-%m-%d %H:%M:%S") .. "\n"
    exportText = exportText .. "Total Quests: " .. questCount .. "\n"
    exportText = exportText .. "=====================================\n\n"
    
    -- Export each quest
    for questId, questData in pairs(QuestieDataCollection.quests) do
        exportText = exportText .. self:FormatQuestExport(questId, questData) .. "\n"
    end
    
    -- Show the frame
    self.exportFrame.info:SetText(questCount .. " quest(s) ready for export")
    self.exportFrame.editBox:SetText(exportText)
    self.exportFrame:Show()
    
    DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[Data Collector]|r Export window opened with " .. questCount .. " quest(s)", 0, 1, 0)
end

-- Format a single quest for export
function QuestieDataCollector:FormatQuestExport(questId, questData)
    local export = "────────────────────────────────────\n"
    export = export .. "Quest ID: " .. questId .. "\n"
    export = export .. "Quest Name: " .. (questData.name or "Unknown") .. "\n"
    export = export .. "Level: " .. (questData.level or "Unknown") .. "\n"
    
    -- Show quest status
    if questData.turnedIn then
        export = export .. "Status: ✅ COMPLETED\n"
    elseif _activeTracking[questId] then
        export = export .. "Status: 🔄 IN PROGRESS\n"
    else
        export = export .. "Status: ⚠️ PARTIAL DATA\n"
    end
    export = export .. "\n"
    
    if questData.wasAlreadyAccepted then
        export = export .. "⚠️ WARNING: INCOMPLETE DATA ⚠️\n"
        export = export .. "Quest was already in log when collection started.\n\n"
    end
    
    -- Quest giver
    if questData.questGiver then
        export = export .. "QUEST GIVER:\n"
        export = export .. "  NPC: " .. (questData.questGiver.name or "Unknown") .. " (ID: " .. (questData.questGiver.id or 0) .. ")\n"
        if questData.questGiver.coords then
            export = export .. "  Location: " .. (questData.questGiver.coords.zone or "Unknown") .. "\n"
            export = export .. "  Coords: " .. string.format("%.1f, %.1f", questData.questGiver.coords.x or 0, questData.questGiver.coords.y or 0) .. "\n"
        end
        export = export .. "\n"
    end
    
    -- Quest description and objectives text
    if questData.questDescription then
        export = export .. "DESCRIPTION:\n"
        export = export .. "  " .. questData.questDescription .. "\n\n"
    end
    
    if questData.objectivesText then
        export = export .. "OBJECTIVES TEXT:\n"
        export = export .. "  " .. questData.objectivesText .. "\n\n"
    end
    
    -- Objectives
    if questData.objectives and #questData.objectives > 0 then
        export = export .. "OBJECTIVES:\n"
        for i, obj in ipairs(questData.objectives) do
            local status = obj.finished and "✓" or "✗"
            export = export .. "  " .. status .. " " .. i .. ". " .. (obj.text or "Unknown") .. "\n"
            -- Show last known progress if available
            if obj.progress and #obj.progress > 0 then
                local lastProgress = obj.progress[#obj.progress]
                export = export .. "      Last update: " .. lastProgress.text .. "\n"
            end
        end
        export = export .. "\n"
    end
    
    -- Turn-in NPC
    if questData.turnInNpc then
        export = export .. "TURN-IN NPC:\n"
        export = export .. "  NPC: " .. (questData.turnInNpc.name or "Unknown") .. " (ID: " .. (questData.turnInNpc.id or 0) .. ")\n"
        if questData.turnInNpc.coords then
            export = export .. "  Location: " .. (questData.turnInNpc.coords.zone or "Unknown") .. "\n"
            export = export .. "  Coords: " .. string.format("%.1f, %.1f", questData.turnInNpc.coords.x or 0, questData.turnInNpc.coords.y or 0) .. "\n"
        end
        export = export .. "\n"
    end
    
    -- XP reward
    if questData.xpReward then
        export = export .. "REWARDS:\n"
        export = export .. "  Experience: " .. questData.xpReward .. " XP\n\n"
    end
    
    -- Related mobs
    if questData.mobs and next(questData.mobs) then
        export = export .. "RELATED MOBS:\n"
        for mobId, mobData in pairs(questData.mobs) do
            export = export .. "  " .. (mobData.name or "Unknown") .. " (ID: " .. mobId .. ", Level: " .. (mobData.level or "?") .. ")\n"
            if mobData.locations and #mobData.locations > 0 then
                export = export .. "    Sample coords: "
                for i = 1, math.min(3, #mobData.locations) do
                    local loc = mobData.locations[i]
                    export = export .. string.format("(%.1f, %.1f) ", loc.x, loc.y)
                end
                export = export .. "\n"
            end
        end
        export = export .. "\n"
    end
    
    -- Quest items
    if questData.items and next(questData.items) then
        export = export .. "QUEST ITEMS:\n"
        for itemId, itemData in pairs(questData.items) do
            export = export .. "  " .. (itemData.name or "Unknown") .. " (ID: " .. itemId .. ")\n"
            if itemData.sources and #itemData.sources > 0 then
                for _, source in ipairs(itemData.sources) do
                    export = export .. "    Source: " .. (source.name or "Unknown") .. " (" .. (source.type or "unknown") .. ")\n"
                end
            end
        end
        export = export .. "\n"
    end
    
    -- Ground objects/containers (matching v1.0.68 format)
    if questData.objects and next(questData.objects) then
        export = export .. "GROUND OBJECTS/CONTAINERS:\n"
        for objName, objData in pairs(questData.objects) do
            local firstLocation = true
            -- Sort locations for consistent output
            local sortedLocs = {}
            for locKey, locData in pairs(objData.locations or {}) do
                table.insert(sortedLocs, locData)
            end
            table.sort(sortedLocs, function(a, b) 
                return (a.timestamp or 0) < (b.timestamp or 0) 
            end)
            
            -- Output each location
            for i, locData in ipairs(sortedLocs) do
                if firstLocation then
                    export = export .. "  " .. objName
                    if objData.id then
                        export = export .. " (ID: " .. objData.id .. ")"
                    end
                    export = export .. " at [" .. string.format("%.1f, %.1f", locData.x, locData.y) .. "]"
                    if locData.zone then
                        export = export .. " in " .. locData.zone
                    end
                    export = export .. "\n"
                    firstLocation = false
                else
                    -- Additional locations
                    export = export .. "    Additional location: [" .. string.format("%.1f, %.1f", locData.x, locData.y) .. "]"
                    if locData.zone then
                        export = export .. " in " .. locData.zone
                    end
                    export = export .. "\n"
                end
            end
        end
        export = export .. "\n"
    end
    
    return export
end

-- Export functions for slash commands
function QuestieDataCollector:ExportQuest(questId)
    questId = tonumber(questId)
    if not questId then
        DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[Data Collector]|r Invalid quest ID", 1, 0, 0)
        return
    end
    
    local questData = QuestieDataCollection.quests[questId]
    if not questData then
        DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[Data Collector]|r No data collected for quest " .. questId, 1, 0, 0)
        return
    end
    
    -- Generate export text
    local export = "=== QUEST DATA EXPORT ===\n"
    export = export .. "Version: " .. (QuestieDataCollection.version or "Unknown") .. "\n"
    export = export .. "Quest ID: " .. questId .. "\n"
    export = export .. "Quest Name: " .. (questData.name or "Unknown") .. "\n"
    export = export .. "Level: " .. (questData.level or "Unknown") .. "\n\n"
    
    if questData.wasAlreadyAccepted then
        export = export .. "⚠️ WARNING: INCOMPLETE DATA ⚠️\n"
        export = export .. "This quest was already in your log when data collection started.\n"
        export = export .. "Quest giver information may be missing.\n\n"
    end
    
    -- Add quest giver info
    if questData.questGiver then
        export = export .. "QUEST GIVER:\n"
        export = export .. "  NPC: " .. (questData.questGiver.name or "Unknown") .. " (ID: " .. (questData.questGiver.id or 0) .. ")\n"
        if questData.questGiver.coords then
            export = export .. "  Location: " .. (questData.questGiver.coords.zone or "Unknown") .. "\n"
            export = export .. "  Coords: " .. string.format("%.1f, %.1f", questData.questGiver.coords.x or 0, questData.questGiver.coords.y or 0) .. "\n"
        end
        export = export .. "\n"
    end
    
    -- Add objectives
    if questData.objectives and #questData.objectives > 0 then
        export = export .. "OBJECTIVES:\n"
        for i, obj in ipairs(questData.objectives) do
            export = export .. "  " .. i .. ". " .. (obj.text or "Unknown") .. "\n"
        end
        export = export .. "\n"
    end
    
    -- Add turn-in info
    if questData.turnInNpc then
        export = export .. "TURN-IN NPC:\n"
        export = export .. "  NPC: " .. (questData.turnInNpc.name or "Unknown") .. " (ID: " .. (questData.turnInNpc.id or 0) .. ")\n"
        if questData.turnInNpc.coords then
            export = export .. "  Location: " .. (questData.turnInNpc.coords.zone or "Unknown") .. "\n"
            export = export .. "  Coords: " .. string.format("%.1f, %.1f", questData.turnInNpc.coords.x or 0, questData.turnInNpc.coords.y or 0) .. "\n"
        end
        export = export .. "\n"
    end
    
    -- Add XP reward info
    if questData.xpReward then
        export = export .. "REWARDS:\n"
        export = export .. "  Experience: " .. questData.xpReward .. " XP\n\n"
    end
    
    -- Add mobs
    if questData.mobs and next(questData.mobs) then
        export = export .. "RELATED MOBS:\n"
        for mobId, mobData in pairs(questData.mobs) do
            export = export .. "  " .. (mobData.name or "Unknown") .. " (ID: " .. mobId .. ", Level: " .. (mobData.level or "?") .. ")\n"
        end
        export = export .. "\n"
    end
    
    -- Add items
    if questData.items and next(questData.items) then
        export = export .. "QUEST ITEMS:\n"
        for itemId, itemData in pairs(questData.items) do
            export = export .. "  " .. (itemData.name or "Unknown") .. " (ID: " .. itemId .. ")\n"
            if itemData.sources and #itemData.sources > 0 then
                for _, source in ipairs(itemData.sources) do
                    export = export .. "    Source: " .. (source.name or "Unknown") .. " (" .. (source.type or "unknown") .. ")\n"
                end
            end
        end
        export = export .. "\n"
    end
    
    -- Add detected mismatches
    local hasMismatches = false
    for key, mismatch in pairs(_dataMismatches) do
        if mismatch.entityType == "quest" and mismatch.entityId == questId then
            if not hasMismatches then
                export = export .. "DATABASE MISMATCHES DETECTED:\n"
                hasMismatches = true
            end
            export = export .. "  Field: " .. mismatch.fieldName .. "\n"
            export = export .. "    Collected: " .. tostring(mismatch.collectedValue) .. "\n"
            export = export .. "    Database: " .. tostring(mismatch.databaseValue) .. "\n"
        end
    end
    
    -- Check for NPC mismatches related to this quest
    if questData.questGiver and questData.questGiver.id then
        local npcKey = "npc_" .. questData.questGiver.id .. "_coords"
        if _dataMismatches[npcKey] then
            if not hasMismatches then
                export = export .. "DATABASE MISMATCHES DETECTED:\n"
                hasMismatches = true
            end
            export = export .. "  Quest Giver NPC " .. questData.questGiver.id .. " coordinates:\n"
            local mismatch = _dataMismatches[npcKey]
            if mismatch.collectedValue and mismatch.collectedValue.x then
                export = export .. "    Found at: " .. string.format("%.1f, %.1f", mismatch.collectedValue.x, mismatch.collectedValue.y) .. "\n"
            end
            if mismatch.databaseValue and mismatch.databaseValue.distance then
                export = export .. "    Distance from DB: " .. string.format("%.1f units", mismatch.databaseValue.distance) .. "\n"
            end
        end
    end
    
    if questData.turnInNpc and questData.turnInNpc.id then
        local npcKey = "npc_" .. questData.turnInNpc.id .. "_coords"
        if _dataMismatches[npcKey] then
            if not hasMismatches then
                export = export .. "DATABASE MISMATCHES DETECTED:\n"
                hasMismatches = true
            end
            export = export .. "  Turn-in NPC " .. questData.turnInNpc.id .. " coordinates:\n"
            local mismatch = _dataMismatches[npcKey]
            if mismatch.collectedValue and mismatch.collectedValue.x then
                export = export .. "    Found at: " .. string.format("%.1f, %.1f", mismatch.collectedValue.x, mismatch.collectedValue.y) .. "\n"
            end
            if mismatch.databaseValue and mismatch.databaseValue.distance then
                export = export .. "    Distance from DB: " .. string.format("%.1f units", mismatch.databaseValue.distance) .. "\n"
            end
        end
    end
    
    if hasMismatches then
        export = export .. "\n"
    end
    
    -- Save to a frame for copying
    if not QuestieDataCollectorExportFrame then
        local f = CreateFrame("Frame", "QuestieDataCollectorExportFrame", UIParent)
        f:SetSize(600, 400)
        f:SetPoint("CENTER")
        f:SetFrameStrata("DIALOG")
        f:SetMovable(true)
        f:EnableMouse(true)
        f:RegisterForDrag("LeftButton")
        f:SetScript("OnDragStart", f.StartMoving)
        f:SetScript("OnDragStop", f.StopMovingOrSizing)
        
        -- Background
        f.bg = f:CreateTexture(nil, "BACKGROUND")
        f.bg:SetAllPoints()
        f.bg:SetColorTexture(0, 0, 0, 0.8)
        
        -- Title
        f.title = f:CreateFontString(nil, "OVERLAY", "GameFontHighlightLarge")
        f.title:SetPoint("TOP", 0, -10)
        f.title:SetText("Quest Data Export")
        
        -- Scroll frame
        f.scroll = CreateFrame("ScrollFrame", nil, f, "UIPanelScrollFrameTemplate")
        f.scroll:SetPoint("TOPLEFT", 10, -40)
        f.scroll:SetPoint("BOTTOMRIGHT", -30, 40)
        
        -- Edit box
        f.editBox = CreateFrame("EditBox", nil, f.scroll)
        f.editBox:SetMultiLine(true)
        f.editBox:SetFontObject(GameFontNormalSmall)
        f.editBox:SetWidth(550)
        f.editBox:SetAutoFocus(false)
        f.editBox:SetScript("OnEscapePressed", function(self) self:ClearFocus() end)
        
        f.scroll:SetScrollChild(f.editBox)
        
        -- Instructions
        f.instructions = f:CreateFontString(nil, "OVERLAY", "GameFontNormal")
        f.instructions:SetPoint("BOTTOM", 0, 20)
        f.instructions:SetText("Ctrl+A to select all, Ctrl+C to copy")
        
        -- Close button
        f.closeButton = CreateFrame("Button", nil, f, "UIPanelCloseButton")
        f.closeButton:SetPoint("TOPRIGHT", -5, -5)
    end
    
    QuestieDataCollectorExportFrame.editBox:SetText(export)
    QuestieDataCollectorExportFrame.editBox:HighlightText()
    QuestieDataCollectorExportFrame:Show()
    
    DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[Data Collector]|r Quest data exported. Copy from the window and submit to GitHub.", 0, 1, 0)
end

function QuestieDataCollector:ShowStatus()
    DEFAULT_CHAT_FRAME:AddMessage("|cFF00FFFF=== Questie Data Collector Status ===|r", 0, 1, 1)
    DEFAULT_CHAT_FRAME:AddMessage("Version: " .. CURRENT_VERSION, 1, 1, 1)
    
    if Questie.db.profile.dataCollectionDevMode then
        DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[DEV MODE ACTIVE] Collecting ALL quests|r", 1, 0, 0)
    end
    
    local questCount = 0
    local missingCount = 0
    local inDatabaseCount = 0
    
    for questId in pairs(QuestieDataCollection.quests) do
        questCount = questCount + 1
        if IsQuestInDatabase(questId) then
            inDatabaseCount = inDatabaseCount + 1
        else
            missingCount = missingCount + 1
        end
    end
    
    DEFAULT_CHAT_FRAME:AddMessage("Total quests tracked: " .. questCount, 1, 1, 1)
    DEFAULT_CHAT_FRAME:AddMessage("Missing from database: " .. missingCount, 1, 1, 0)
    DEFAULT_CHAT_FRAME:AddMessage("Now in database (skipped): " .. inDatabaseCount, 0.7, 0.7, 0.7)
    
    local activeCount = 0
    for _ in pairs(_activeTracking) do
        activeCount = activeCount + 1
    end
    DEFAULT_CHAT_FRAME:AddMessage("Currently tracking: " .. activeCount .. " quests", 0, 1, 0)
    
    local mismatchCount = 0
    for _ in pairs(_dataMismatches) do
        mismatchCount = mismatchCount + 1
    end
    if mismatchCount > 0 then
        DEFAULT_CHAT_FRAME:AddMessage("Database mismatches detected: " .. mismatchCount, 1, 0.5, 0)
    end
    
    local serviceNPCCount = 0
    for _ in pairs(QuestieDataCollection.serviceNPCs) do
        serviceNPCCount = serviceNPCCount + 1
    end
    if serviceNPCCount > 0 then
        DEFAULT_CHAT_FRAME:AddMessage("Service NPCs tracked: " .. serviceNPCCount, 0.5, 0.5, 1)
    end
    
    local mailboxCount = 0
    for _ in pairs(QuestieDataCollection.mailboxes) do
        mailboxCount = mailboxCount + 1
    end
    if mailboxCount > 0 then
        DEFAULT_CHAT_FRAME:AddMessage("Mailboxes discovered: " .. mailboxCount, 0.5, 0.5, 1)
    end
    
    if Questie.db.profile.enableDataCollection then
        DEFAULT_CHAT_FRAME:AddMessage("Status: |cFF00FF00ENABLED|r", 0, 1, 0)
    else
        DEFAULT_CHAT_FRAME:AddMessage("Status: |cFFFF0000DISABLED|r", 1, 0, 0)
    end
end

function QuestieDataCollector:ShowTrackedQuests()
    local count = 0
    DEFAULT_CHAT_FRAME:AddMessage("|cFF00FFFF=== Tracked Missing Quests ===|r", 0, 1, 1)
    
    for questId, questData in pairs(QuestieDataCollection.quests) do
        if not IsQuestInDatabase(questId) then
            count = count + 1
            local status = ""
            if questData.turnedIn then
                status = "|cFF00FF00[COMPLETE]|r"
            elseif _activeTracking[questId] then
                status = "|cFFFFFF00[IN PROGRESS]|r"
            else
                status = "|cFFAAAAAA[PARTIAL DATA]|r"
            end
            
            DEFAULT_CHAT_FRAME:AddMessage(string.format("%s %s (ID: %d) %s", 
                status,
                questData.name or "Unknown",
                questId,
                questData.wasAlreadyAccepted and "|cFFFF8800[INCOMPLETE]|r" or ""
            ), 1, 1, 1)
        end
    end
    
    if count == 0 then
        DEFAULT_CHAT_FRAME:AddMessage("No missing quests being tracked.", 1, 1, 1)
    else
        DEFAULT_CHAT_FRAME:AddMessage("Total: " .. count .. " missing quests", 1, 1, 0)
    end
end

function QuestieDataCollector:ManualTurnIn(questId)
    local questData = QuestieDataCollection.quests[questId]
    if not questData then
        DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[Data Collector]|r No data for quest " .. questId, 1, 0, 0)
        return
    end
    
    -- Capture turn-in NPC from current target
    local guid = UnitGUID("target")
    if guid then
        local npcId = ExtractNpcIdFromGuid(guid)
        if npcId then
            local npcName = UnitName("target")
            local coords = QuestieDataCollector:GetPlayerCoordinates()
            
            questData.turnInNpc = {
                id = npcId,
                name = npcName,
                coords = coords
            }
            DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[Data Collector]|r Turn-in NPC captured: " .. npcName .. " (ID: " .. npcId .. ")", 0, 1, 0)
        end
    end
    
    -- Mark as turned in
    questData.turnedIn = true
    questData.turnInTimestamp = time()
    questData.turnInDate = date("%Y-%m-%d %H:%M:%S")
    
    -- If we have pending XP, assign it
    if _pendingXPReward and _pendingXPReward > 0 then
        questData.xpReward = _pendingXPReward
        DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[Data Collector]|r XP reward captured: " .. _pendingXPReward, 0, 1, 0)
        _pendingXPReward = nil
    end
    
    -- Remove from active tracking
    _activeTracking[questId] = nil
    
    DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[Data Collector]|r Quest marked as turned in: " .. (questData.name or "Unknown"), 0, 1, 0)
end

function QuestieDataCollector:CaptureQuestGiver(questId)
    local questData = QuestieDataCollection.quests[questId]
    if not questData then
        DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[Data Collector]|r No data for quest " .. questId, 1, 0, 0)
        return
    end
    
    -- Capture quest giver NPC from current target
    local guid = UnitGUID("target")
    if not guid then
        DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[Data Collector]|r No target selected", 1, 0, 0)
        return
    end
    
    local npcId = ExtractNpcIdFromGuid(guid)
    if npcId then
        local npcName = UnitName("target")
        local coords = QuestieDataCollector:GetPlayerCoordinates()
        
        questData.questGiver = {
            id = npcId,
            name = npcName,
            coords = coords
        }
        DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[Data Collector]|r Quest giver captured: " .. npcName .. " (ID: " .. npcId .. ")", 0, 1, 0)
    else
        DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[Data Collector]|r Could not extract NPC ID from target", 1, 0, 0)
    end
end

function QuestieDataCollector:RescanQuestLog()
    DEFAULT_CHAT_FRAME:AddMessage("|cFF00FFFF[Data Collector]|r Rescanning quest log for missing data...", 0, 1, 1)
    
    local scannedCount = 0
    local updatedCount = 0
    
    -- Scan through the quest log
    for i = 1, GetNumQuestLogEntries() do
        local title, level, tag, isHeader, _, _, _, _, questId = GetQuestLogTitle(i)
        
        if not isHeader and questId and questId > 0 then
            scannedCount = scannedCount + 1
            
            -- Check if we're tracking this quest
            if QuestieDataCollection.quests[questId] then
                local questData = QuestieDataCollection.quests[questId]
                local updated = false
                
                -- Update basic info if missing
                if not questData.name then
                    questData.name = title
                    updated = true
                end
                
                if not questData.level then
                    questData.level = level
                    updated = true
                end
                
                -- Always update objectives to get current progress
                SelectQuestLogEntry(i)
                local numObjectives = GetNumQuestLeaderBoards(i)
                
                -- If objectives don't exist, create them
                if not questData.objectives or #questData.objectives == 0 then
                    questData.objectives = {}
                    for j = 1, numObjectives do
                        table.insert(questData.objectives, {
                            index = j,
                            text = "",
                            type = "",
                            finished = false,
                            progress = {}
                        })
                    end
                    updated = true
                end
                
                -- Update current objective state
                for j = 1, numObjectives do
                    local text, objectiveType, finished = GetQuestLogLeaderBoard(j, i)
                    if text and questData.objectives[j] then
                        -- Update the current state
                        questData.objectives[j].text = text
                        questData.objectives[j].type = objectiveType
                        questData.objectives[j].finished = finished
                        
                        -- Add to progress history if changed
                        local lastProgress = nil
                        if questData.objectives[j].progress and #questData.objectives[j].progress > 0 then
                            lastProgress = questData.objectives[j].progress[#questData.objectives[j].progress]
                        end
                        
                        if not lastProgress or lastProgress.text ~= text then
                            table.insert(questData.objectives[j].progress, {
                                text = text,
                                finished = finished,
                                timestamp = time(),
                                coords = QuestieDataCollector:GetPlayerCoordinates()
                            })
                            updated = true
                        end
                    end
                end
                
                if updated and numObjectives > 0 then
                    DebugMessage("|cFF00FF00[DATA]|r Updated " .. numObjectives .. " objectives for quest " .. questId, 0, 1, 0)
                end
                
                -- Get quest text if missing
                if not questData.objectivesText then
                    SelectQuestLogEntry(i)
                    local objectivesText = GetQuestLogQuestText()
                    if objectivesText and objectivesText ~= "" then
                        questData.objectivesText = objectivesText
                        updated = true
                    end
                end
                
                if updated then
                    updatedCount = updatedCount + 1
                    DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[DATA]|r Updated: " .. title .. " (ID: " .. questId .. ")", 0, 1, 0)
                end
            end
        end
    end
    
    DEFAULT_CHAT_FRAME:AddMessage("|cFF00FFFF[Data Collector]|r Rescan complete. Scanned " .. scannedCount .. " quests, updated " .. updatedCount, 0, 1, 1)
end

function QuestieDataCollector:ClearData()
    QuestieDataCollection.quests = {}
    QuestieDataCollection.mismatches = {}
    QuestieDataCollection.serviceNPCs = {}
    QuestieDataCollection.mailboxes = {}
    _activeTracking = {}
    _dataMismatches = {}
    _serviceNPCs = {}
    _mailboxes = {}
    DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[Data Collector]|r All collected data cleared. Use /reload to save.", 1, 0, 0)
end

-- Slash command handler
SLASH_QUESTIEDATACOLLECTOR1 = "/qdc"
SlashCmdList["QUESTIEDATACOLLECTOR"] = function(msg)
    local args = {strsplit(" ", msg)}
    local cmd = args[1] and string.lower(args[1]) or ""
    
    if cmd == "enable" then
        Questie.db.profile.enableDataCollection = true
        QuestieDataCollector:Initialize()
        DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[Data Collector]|r Enabled", 0, 1, 0)
    elseif cmd == "disable" then
        Questie.db.profile.enableDataCollection = false
        QuestieDataCollector:RestoreTooltipSettings()
        DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[Data Collector]|r Disabled", 1, 0, 0)
    elseif cmd == "status" then
        QuestieDataCollector:ShowStatus()
    elseif cmd == "show" then
        QuestieDataCollector:ShowTrackedQuests()
    elseif cmd == "export" then
        local questId = tonumber(args[2])
        if questId then
            -- Export specific quest if ID provided
            QuestieDataCollector:ExportQuest(questId)
        else
            -- Export all tracked quests
            QuestieDataCollector:ShowExportWindow()
        end
    elseif cmd == "clear" then
        QuestieDataCollector:ClearData()
    elseif cmd == "rescan" then
        QuestieDataCollector:RescanQuestLog()
    elseif cmd == "questgiver" then
        local questId = tonumber(args[2])
        if questId then
            QuestieDataCollector:CaptureQuestGiver(questId)
        else
            DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[Data Collector]|r Usage: /qdc questgiver <questId> (target NPC first)", 1, 0, 0)
        end
    elseif cmd == "turnin" then
        local questId = tonumber(args[2])
        if questId then
            QuestieDataCollector:ManualTurnIn(questId)
        else
            DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[Data Collector]|r Usage: /qdc turnin <questId> (target NPC first)", 1, 0, 0)
        end
    elseif cmd == "debug" then
        Questie.db.profile.debugDataCollector = not Questie.db.profile.debugDataCollector
        if Questie.db.profile.debugDataCollector then
            DEFAULT_CHAT_FRAME:AddMessage("|cFF00FF00[Data Collector]|r Debug messages enabled", 0, 1, 0)
        else
            DEFAULT_CHAT_FRAME:AddMessage("|cFFFF0000[Data Collector]|r Debug messages disabled", 1, 0, 0)
        end
    else
        DEFAULT_CHAT_FRAME:AddMessage("|cFF00FFFF=== Questie Data Collector Commands ===|r", 0, 1, 1)
        DEFAULT_CHAT_FRAME:AddMessage("/qdc status - Show collection status", 1, 1, 1)
        DEFAULT_CHAT_FRAME:AddMessage("/qdc enable - Enable data collection", 1, 1, 1)
        DEFAULT_CHAT_FRAME:AddMessage("/qdc disable - Disable data collection", 1, 1, 1)
        DEFAULT_CHAT_FRAME:AddMessage("/qdc show - Show all tracked quests", 1, 1, 1)
        DEFAULT_CHAT_FRAME:AddMessage("/qdc export <questId> - Export quest data", 1, 1, 1)
        DEFAULT_CHAT_FRAME:AddMessage("/qdc questgiver <questId> - Manually capture quest giver (target NPC first)", 1, 1, 1)
        DEFAULT_CHAT_FRAME:AddMessage("/qdc turnin <questId> - Manually capture turn-in NPC (target NPC first)", 1, 1, 1)
        DEFAULT_CHAT_FRAME:AddMessage("/qdc clear - Clear all collected data", 1, 1, 1)
        DEFAULT_CHAT_FRAME:AddMessage("/qdc rescan - Re-scan quest log for missing data", 1, 1, 1)
        DEFAULT_CHAT_FRAME:AddMessage("/qdc debug - Toggle debug messages", 1, 1, 1)
    end
end