-- Test WorldMapButton visibility
local function TestWorldMap()
    print("=== WorldMap Test ===")
    if WorldMapButton then
        print("WorldMapButton exists: YES")
        print("  IsShown: " .. tostring(WorldMapButton:IsShown()))
        print("  IsVisible: " .. tostring(WorldMapButton:IsVisible()))
        print("  Alpha: " .. WorldMapButton:GetAlpha())
        local parent = WorldMapButton:GetParent()
        if parent then
            print("  Parent: " .. (parent:GetName() or "unnamed"))
            print("  Parent IsShown: " .. tostring(parent:IsShown()))
        end
    else
        print("WorldMapButton: MISSING")
    end
    
    if WorldMapFrame then
        print("WorldMapFrame:")
        print("  IsShown: " .. tostring(WorldMapFrame:IsShown()))
        print("  IsVisible: " .. tostring(WorldMapFrame:IsVisible()))
    end
    
    print("=== End Test ===")
end

SLASH_WORLDMAPTEST1 = "/wmtest"
SlashCmdList["WORLDMAPTEST"] = TestWorldMap

print("|cFFFFFF00WorldMap test loaded. Open map and type /wmtest|r")