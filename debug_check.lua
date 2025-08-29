-- Debug check for Questie
local function QuestieDebugCheck()
    print("=== Questie Debug Check ===")
    
    -- Check if Questie is loaded
    if Questie then
        print("Questie loaded: YES")
        print("Questie started:", Questie.started)
    else
        print("Questie loaded: NO")
        return
    end
    
    -- Check HBD
    local HBD = QuestieCompat and QuestieCompat.HBD or LibStub and LibStub("HereBeDragonsQuestie-2.0", true)
    if HBD then
        print("HBD loaded: YES")
        -- Check HBDPins
        local HBDPins = QuestieCompat and QuestieCompat.HBDPins or LibStub and LibStub("HereBeDragonsQuestie-Pins-2.0", true)
        if HBDPins then
            print("HBDPins loaded: YES")
            local pinCount = 0
            if HBDPins.worldmapPins then
                for _ in pairs(HBDPins.worldmapPins) do
                    pinCount = pinCount + 1
                end
            end
            print("World map pins registered:", pinCount)
        else
            print("HBDPins loaded: NO")
        end
    else
        print("HBD loaded: NO")
    end
    
    -- Check if any quests are loaded
    local QuestieDB = QuestieLoader and QuestieLoader:ImportModule("QuestieDB")
    if QuestieDB then
        print("QuestieDB loaded: YES")
        -- Try to get a quest
        local testQuest = QuestieDB.GetQuest(26167)
        if testQuest then
            print("Test quest 26167 loaded:", testQuest.name or "unnamed")
        else
            print("Test quest 26167: NOT FOUND")
        end
    else
        print("QuestieDB loaded: NO")
    end
    
    -- Check map dimensions
    if WorldMapButton then
        print("WorldMapButton width:", WorldMapButton:GetWidth())
        print("WorldMapButton scale:", WorldMapButton:GetScale())
    end
    
    -- Check ElvUI
    if ElvUI then
        print("ElvUI detected: YES")
    else
        print("ElvUI detected: NO")
    end
    
    -- Check if quest log has any quests
    local questCount = GetNumQuestLogEntries()
    print("Quests in log:", questCount)
end

SLASH_QUESTIEDEBUG1 = "/qdebug"
SlashCmdList["QUESTIEDEBUG"] = QuestieDebugCheck