-- Test WorldMapButton and frame parenting
local function TestWorldMapFrames()
    print("=== WorldMap Frame Test ===")
    
    -- Check WorldMapButton
    if WorldMapButton then
        print("WorldMapButton exists: YES")
        print("  IsShown: " .. tostring(WorldMapButton:IsShown()))
        print("  IsVisible: " .. tostring(WorldMapButton:IsVisible()))
        print("  Width: " .. WorldMapButton:GetWidth())
        print("  Height: " .. WorldMapButton:GetHeight())
        print("  Scale: " .. WorldMapButton:GetScale())
        local parent = WorldMapButton:GetParent()
        if parent then
            print("  Parent: " .. (parent:GetName() or "unnamed"))
            print("  Parent IsShown: " .. tostring(parent:IsShown()))
        end
    else
        print("WorldMapButton: MISSING")
    end
    
    -- Check WorldMapFrame
    if WorldMapFrame then
        print("WorldMapFrame:")
        print("  IsShown: " .. tostring(WorldMapFrame:IsShown()))
        print("  IsVisible: " .. tostring(WorldMapFrame:IsVisible()))
    end
    
    -- Test creating a frame parented to WorldMapButton
    local testFrame = CreateFrame("Frame", "QuestieTestWorldMapFrame", WorldMapButton)
    testFrame:SetWidth(20)
    testFrame:SetHeight(20)
    testFrame:SetPoint("CENTER", WorldMapButton, "CENTER", 0, 0)
    
    local texture = testFrame:CreateTexture(nil, "OVERLAY")
    texture:SetTexture("Interface\\Icons\\INV_Misc_QuestionMark")
    texture:SetAllPoints(testFrame)
    
    testFrame:Show()
    
    print("\nTest Frame Created:")
    print("  Parent: " .. (testFrame:GetParent():GetName() or "unnamed"))
    print("  IsShown: " .. tostring(testFrame:IsShown()))
    print("  IsVisible: " .. tostring(testFrame:IsVisible()))
    
    -- Try with different frame levels and strata
    testFrame:SetFrameStrata("TOOLTIP")
    testFrame:SetFrameLevel(9999)
    
    print("After setting TOOLTIP strata:")
    print("  IsShown: " .. tostring(testFrame:IsShown()))
    print("  IsVisible: " .. tostring(testFrame:IsVisible()))
    
    print("=== End Test ===")
end

SLASH_WORLDMAPFRAMETEST1 = "/wmftest"
SlashCmdList["WORLDMAPFRAMETEST"] = TestWorldMapFrames

print("|cFFFFFF00WorldMap frame test loaded. Open map and type /wmftest|r")