-- Test map zoom functionality
local function TestZoom()
    print("=== Testing Map Zoom ===")
    
    if WorldMapFrame then
        print("WorldMapFrame exists: YES")
        
        -- Check if mouse wheel is enabled
        if WorldMapFrame:IsMouseWheelEnabled() then
            print("Mouse wheel enabled on WorldMapFrame: YES")
        else
            print("Mouse wheel enabled on WorldMapFrame: NO")
            print("Attempting to enable...")
            WorldMapFrame:EnableMouseWheel(true)
            print("Mouse wheel now: " .. tostring(WorldMapFrame:IsMouseWheelEnabled()))
        end
        
        -- Check for zoom functions
        if WorldMapFrame.ScrollContainer then
            print("ScrollContainer exists: YES")
        else
            print("ScrollContainer exists: NO")
        end
        
        -- Check WorldMapButton
        if WorldMapButton then
            if WorldMapButton:IsMouseWheelEnabled() then
                print("Mouse wheel enabled on WorldMapButton: YES")
            else
                print("Mouse wheel enabled on WorldMapButton: NO")
                print("Attempting to enable...")
                WorldMapButton:EnableMouseWheel(true)
                print("Mouse wheel now: " .. tostring(WorldMapButton:IsMouseWheelEnabled()))
            end
        end
        
        -- Check for ElvUI
        if ElvUI then
            print("ElvUI detected: YES")
            -- Check if ElvUI has map module
            local E = ElvUI[1]
            if E and E.MapInfo then
                print("ElvUI MapInfo module: YES")
            end
        else
            print("ElvUI detected: NO")
        end
        
        -- Check zoom level functions (3.3.5)
        if GetCurrentMapZone then
            print("Current map zone: " .. (GetCurrentMapZone() or "nil"))
        end
        if GetCurrentMapContinent then
            print("Current map continent: " .. (GetCurrentMapContinent() or "nil"))
        end
    end
    
    print("=== End Test ===")
end

-- Try to hook mouse wheel
local function EnableZoom()
    print("=== Enabling Map Zoom ===")
    
    if WorldMapFrame then
        WorldMapFrame:EnableMouseWheel(true)
        WorldMapFrame:SetScript("OnMouseWheel", function(self, delta)
            print("WorldMapFrame wheel: " .. delta)
            -- In 3.3.5, we need to manually handle zoom
            if delta > 0 then
                -- Zoom in
                print("Zooming in...")
                -- Try to zoom to player position
                if SetMapToCurrentZone then
                    SetMapToCurrentZone()
                end
            else
                -- Zoom out  
                print("Zooming out...")
                -- Try to zoom to continent
                if SetMapZoom then
                    SetMapZoom(-1)
                elseif GetCurrentMapContinent then
                    local continent = GetCurrentMapContinent()
                    if continent and continent > 0 then
                        SetMapZoom(continent)
                    end
                end
            end
        end)
        print("Mouse wheel handler set on WorldMapFrame")
    end
    
    if WorldMapButton then
        WorldMapButton:EnableMouseWheel(true)
        WorldMapButton:SetScript("OnMouseWheel", function(self, delta)
            print("WorldMapButton wheel: " .. delta)
            -- Forward to parent
            if WorldMapFrame then
                local script = WorldMapFrame:GetScript("OnMouseWheel")
                if script then
                    script(WorldMapFrame, delta)
                end
            end
        end)
        print("Mouse wheel handler set on WorldMapButton")
    end
    
    print("=== Zoom Enabled ===")
end

SLASH_TESTZOOM1 = "/testzoom"
SlashCmdList["TESTZOOM"] = TestZoom

SLASH_ENABLEZOOM1 = "/enablezoom"
SlashCmdList["ENABLEZOOM"] = EnableZoom

print("|cFFFFFF00Map zoom test loaded|r")
print("|cFF00FF00Type /testzoom to check zoom status|r")
print("|cFF00FF00Type /enablezoom to enable mouse wheel zoom|r")