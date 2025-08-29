-- Final test to check if pins are working
local function FinalTest()
    print("=== FINAL PIN TEST ===")
    
    -- Check enabled state
    if Questie and Questie.db and Questie.db.profile then
        print("Questie.db.profile.enabled = " .. tostring(Questie.db.profile.enabled))
        print("enableMapIcons = " .. tostring(Questie.db.profile.enableMapIcons))
        print("enableMiniMapIcons = " .. tostring(Questie.db.profile.enableMiniMapIcons))
    end
    
    -- Check for QuestieQuest module
    if QuestieLoader then
        local QuestieQuest = QuestieLoader:ImportModule("QuestieQuest")
        if QuestieQuest then
            print("QuestieQuest module: LOADED")
        else
            print("QuestieQuest module: NOT LOADED")
        end
    end
    
    -- Check HBDPins
    local HBDPins = QuestieCompat and QuestieCompat.HBDPins
    if HBDPins and HBDPins.worldmapPins then
        local totalPins = 0
        local shownPins = 0
        for icon, data in pairs(HBDPins.worldmapPins) do
            totalPins = totalPins + 1
            if icon:IsShown() then
                shownPins = shownPins + 1
            end
        end
        print(string.format("World Map Pins: %d total, %d shown", totalPins, shownPins))
    else
        print("No world map pins found")
    end
    
    -- Check if map is open
    if WorldMapFrame and WorldMapFrame:IsShown() then
        print("World Map is OPEN")
    else
        print("World Map is CLOSED - open it to see pins")
    end
    
    print("=== END TEST ===")
end

SLASH_FINALTEST1 = "/ftest"
SlashCmdList["FINALTEST"] = FinalTest

-- Also try to force refresh
local function ForceRefresh()
    print("=== FORCING REFRESH ===")
    
    -- Try multiple ways to refresh
    if QuestieLoader then
        local QuestieQuest = QuestieLoader:ImportModule("QuestieQuest")
        if QuestieQuest and QuestieQuest.ToggleNotes then
            print("Toggling notes OFF then ON...")
            QuestieQuest:ToggleNotes(false)
            QuestieQuest:ToggleNotes(true)
            print("Notes toggled")
        end
    end
    
    -- Try updating world map
    local HBDPins = QuestieCompat and QuestieCompat.HBDPins
    if HBDPins and HBDPins.UpdateWorldMap then
        print("Calling HBDPins:UpdateWorldMap()...")
        HBDPins:UpdateWorldMap()
        print("World map updated")
    end
    
    print("=== REFRESH COMPLETE ===")
    print("Open your map to check for pins")
end

SLASH_FORCEREFRESH1 = "/refresh"
SlashCmdList["FORCEREFRESH"] = ForceRefresh

print("|cFFFFFF00Final test loaded.|r")
print("|cFF00FF00Type /ftest to check pin status|r")
print("|cFF00FF00Type /refresh to force refresh all pins|r")