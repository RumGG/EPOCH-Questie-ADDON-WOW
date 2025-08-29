-- Check what's creating that mailbox icon
local function CheckOtherAddons()
    print("=== Checking for Non-Questie Icons ===")
    
    -- Check if HandyNotes is adding it
    if HandyNotes then
        print("HandyNotes is loaded")
    end
    
    -- Check if Carbonite is adding it
    if Nx then
        print("Carbonite is loaded")
    end
    
    -- Check all frames on WorldMapButton
    if WorldMapButton then
        local kids = {WorldMapButton:GetChildren()}
        print("Found " .. #kids .. " child frames on WorldMapButton")
        
        for i, child in ipairs(kids) do
            local name = child:GetName()
            if name and (string.find(name:lower(), "mail") or string.find(name:lower(), "icon")) then
                print("  Frame: " .. name)
                if child:IsVisible() then
                    local x, y = child:GetCenter()
                    local mapX, mapY = WorldMapButton:GetCenter()
                    local width = WorldMapButton:GetWidth()
                    local height = WorldMapButton:GetHeight()
                    
                    if x and y and mapX and mapY then
                        local relX = ((x - mapX) / width + 0.5) * 100
                        local relY = (-(y - mapY) / height + 0.5) * 100
                        print(string.format("    Position: %.1f, %.1f", relX, relY))
                    end
                end
            end
        end
    end
    
    -- Check what addon owns the frame under the cursor
    print("\nHover over the mailbox icon and type /framestack")
    print("This will show what addon created that frame")
    
    print("=== End Check ===")
end

SLASH_CHECKADDONS1 = "/checkaddons"
SlashCmdList["CHECKADDONS"] = CheckOtherAddons

print("|cFFFFFF00Type /checkaddons to see what might be creating that mailbox|r")