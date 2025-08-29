-- Fix map zoom for WoW 3.3.5
local function FixMapZoom()
    print("=== Fixing Map Zoom ===")
    
    -- Store the current map level
    local currentContinent = nil
    local currentZone = nil
    
    -- Create zoom functions
    local function ZoomIn()
        -- Get current location
        local continent = GetCurrentMapContinent()
        local zone = GetCurrentMapZone()
        
        if continent == -1 then
            -- We're at world map, zoom to player's continent
            SetMapToCurrentZone()
        elseif zone == 0 then
            -- We're at continent level, try to zoom to player's zone
            SetMapToCurrentZone()
        else
            -- Already zoomed in, do nothing or zoom to player
            SetMapToCurrentZone()
        end
    end
    
    local function ZoomOut()
        local continent = GetCurrentMapContinent()
        local zone = GetCurrentMapZone()
        
        if zone > 0 then
            -- Zoomed into a zone, go back to continent
            SetMapZoom(continent, 0)
        elseif continent > 0 then
            -- At continent level, go to world
            SetMapZoom(-1)
        end
    end
    
    -- Hook the mouse wheel
    if WorldMapFrame then
        WorldMapFrame:EnableMouseWheel(true)
        WorldMapFrame:SetScript("OnMouseWheel", function(self, delta)
            if IsControlKeyDown() then
                -- Control key changes zoom speed/behavior
                if delta > 0 then
                    SetMapToCurrentZone()
                else
                    SetMapZoom(-1) -- Go to world map
                end
            else
                if delta > 0 then
                    ZoomIn()
                else
                    ZoomOut()
                end
            end
        end)
    end
    
    if WorldMapButton then
        WorldMapButton:EnableMouseWheel(true)
        WorldMapButton:SetScript("OnMouseWheel", function(self, delta)
            local script = WorldMapFrame:GetScript("OnMouseWheel")
            if script then
                script(WorldMapFrame, delta)
            end
        end)
    end
    
    -- Also add keyboard shortcuts
    WorldMapFrame:SetScript("OnKeyDown", function(self, key)
        if key == "NUMPADPLUS" or key == "PLUS" or key == "=" then
            ZoomIn()
        elseif key == "NUMPADMINUS" or key == "MINUS" then
            ZoomOut()
        end
    end)
    
    print("Map zoom fixed!")
    print("Use mouse wheel to zoom in/out")
    print("Hold Ctrl + wheel for quick world/current zone")
    print("Use +/- keys to zoom")
end

-- Auto-fix on load
local frame = CreateFrame("Frame")
frame:RegisterEvent("ADDON_LOADED")
frame:SetScript("OnEvent", function(self, event, addon)
    if addon == "Questie" then
        -- Wait a moment for map to be ready
        local C_Timer = QuestieCompat and QuestieCompat.C_Timer
        if C_Timer then
            C_Timer.After(1, FixMapZoom)
        else
            FixMapZoom()
        end
    end
end)

-- Manual command
SLASH_FIXZOOM1 = "/fixzoom"
SlashCmdList["FIXZOOM"] = FixMapZoom

print("|cFFFFFF00Map zoom fix loaded. Type /fixzoom if zoom doesn't work|r")