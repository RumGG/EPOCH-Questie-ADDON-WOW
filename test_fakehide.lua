-- Test FakeHide/FakeShow state
local function TestFakeHide()
    print("=== Testing FakeHide State ===")
    
    -- Check if Questie is enabled
    if Questie and Questie.db then
        print("Questie enabled: " .. tostring(Questie.db.profile.enabled))
        print("Map icons enabled: " .. tostring(Questie.db.profile.enableMapIcons))
        print("Minimap icons enabled: " .. tostring(Questie.db.profile.enableMiniMapIcons))
    end
    
    -- Check HBDPins
    local HBDPins = QuestieCompat and QuestieCompat.HBDPins
    if not HBDPins then
        print("ERROR: HBDPins not found!")
        return
    end
    
    -- Check worldmap pins for FakeHide status
    local worldmapPins = HBDPins.worldmapPins
    if not worldmapPins then
        print("No worldmap pins table")
        return
    end
    
    local totalCount = 0
    local hiddenCount = 0
    local fakeHiddenCount = 0
    local hasShowFunc = 0
    local has_showFunc = 0
    
    for icon, data in pairs(worldmapPins) do
        totalCount = totalCount + 1
        if icon.hidden then
            fakeHiddenCount = fakeHiddenCount + 1
        end
        if not icon:IsShown() then
            hiddenCount = hiddenCount + 1
        end
        if icon.Show then
            hasShowFunc = hasShowFunc + 1
        end
        if icon._show then
            has_showFunc = has_showFunc + 1
        end
    end
    
    print(string.format("Pins: %d total", totalCount))
    print(string.format("  %d are FakeHidden (icon.hidden=true)", fakeHiddenCount))
    print(string.format("  %d are not shown (IsShown=false/nil)", hiddenCount))
    print(string.format("  %d have Show function", hasShowFunc))
    print(string.format("  %d have _show function (FakeHidden)", has_showFunc))
    
    -- Try to FakeShow a sample of pins
    local sampleCount = 0
    for icon, data in pairs(worldmapPins) do
        if sampleCount < 3 and icon.hidden then
            print(string.format("\nAttempting to FakeShow pin %d:", sampleCount + 1))
            print("  Before: hidden=" .. tostring(icon.hidden) .. ", IsShown=" .. tostring(icon:IsShown()))
            
            if icon.FakeShow then
                icon:FakeShow()
                print("  After FakeShow: hidden=" .. tostring(icon.hidden) .. ", IsShown=" .. tostring(icon:IsShown()))
            else
                print("  No FakeShow function!")
            end
            
            sampleCount = sampleCount + 1
        end
        if sampleCount >= 3 then
            break
        end
    end
    
    print("=== End Test ===")
end

SLASH_TESTFAKEHIDE1 = "/testfake"
SlashCmdList["TESTFAKEHIDE"] = TestFakeHide

print("|cFFFFFF00FakeHide test loaded. Type /testfake to check FakeHide status|r")