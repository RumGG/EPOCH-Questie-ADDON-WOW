-- Debug script for checking map pin issues
local function QuestiePinDebug()
    print("=== Questie Pin Debug ===")
    
    -- Check if Questie and HBD are loaded
    if not Questie then
        print("ERROR: Questie not loaded!")
        return
    end
    
    -- Get HBD and HBDPins
    local HBD = QuestieCompat and QuestieCompat.HBD
    local HBDPins = QuestieCompat and QuestieCompat.HBDPins
    
    if not HBD then
        print("ERROR: HBD not loaded!")
        return
    end
    
    if not HBDPins then
        print("ERROR: HBDPins not loaded!")
        return
    end
    
    print("HBD loaded: YES")
    print("HBDPins loaded: YES")
    
    -- Check if worldmapPins exists
    if HBDPins.worldmapPins then
        local count = 0
        for icon, data in pairs(HBDPins.worldmapPins) do
            count = count + 1
            if count <= 3 then  -- Show first 3 pins as examples
                print(string.format("  Pin %d: x=%.2f, y=%.2f, uiMapID=%s", 
                    count, data.x or 0, data.y or 0, tostring(data.uiMapID)))
            end
        end
        print("Total worldmap pins: " .. count)
    else
        print("worldmapPins table doesn't exist or not accessible")
    end
    
    -- Check if UpdateWorldMap function exists
    if HBDPins.UpdateWorldMap then
        print("UpdateWorldMap function: EXISTS")
        -- Try to call it
        local success, err = pcall(HBDPins.UpdateWorldMap)
        if success then
            print("UpdateWorldMap call: SUCCESS")
        else
            print("UpdateWorldMap call: FAILED - " .. tostring(err))
        end
    else
        print("UpdateWorldMap function: MISSING")
    end
    
    -- Check WorldMapButton status
    if WorldMapButton then
        print("WorldMapButton: EXISTS")
        print("  Width: " .. WorldMapButton:GetWidth())
        print("  Height: " .. WorldMapButton:GetHeight())
        print("  Scale: " .. WorldMapButton:GetScale())
        print("  Visible: " .. tostring(WorldMapButton:IsVisible()))
    else
        print("WorldMapButton: MISSING")
    end
    
    -- Check if WorldMapFrame is visible
    if WorldMapFrame then
        print("WorldMapFrame visible: " .. tostring(WorldMapFrame:IsVisible()))
    end
    
    -- Check QuestieMap
    local QuestieMap = QuestieLoader and QuestieLoader:ImportModule("QuestieMap")
    if QuestieMap then
        print("QuestieMap module: LOADED")
    else
        print("QuestieMap module: NOT LOADED")
    end
    
    -- Check available quests
    local AvailableQuests = QuestieLoader and QuestieLoader:ImportModule("AvailableQuests")
    if AvailableQuests then
        print("AvailableQuests module: LOADED")
        -- Check if there are any available quests cached
        if AvailableQuests.availableQuests then
            local questCount = 0
            for questId, _ in pairs(AvailableQuests.availableQuests) do
                questCount = questCount + 1
                if questCount <= 3 then
                    print("  Available quest ID: " .. questId)
                end
            end
            print("Total available quests: " .. questCount)
        else
            print("No availableQuests table found")
        end
    else
        print("AvailableQuests module: NOT LOADED")
    end
    
    -- Check QuestieFramePool
    local QuestieFramePool = QuestieLoader and QuestieLoader:ImportModule("QuestieFramePool") 
    if QuestieFramePool then
        print("QuestieFramePool: LOADED")
        if QuestieFramePool._unusedFrames then
            print("  Unused frames: " .. #QuestieFramePool._unusedFrames)
        end
        if QuestieFramePool._usedFrames then
            local usedCount = 0
            for _, _ in pairs(QuestieFramePool._usedFrames) do
                usedCount = usedCount + 1
            end
            print("  Used frames: " .. usedCount)
        end
    else
        print("QuestieFramePool: NOT LOADED")
    end
    
    print("=== End Debug ===")
end

-- Create slash command
SLASH_QPINDEBUG1 = "/qpindebug"
SlashCmdList["QPINDEBUG"] = QuestiePinDebug

print("|cFFFFFF00Questie Pin Debug loaded. Type /qpindebug to run diagnostics.|r")