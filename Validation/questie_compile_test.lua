#!/usr/bin/env lua

-- This script mimics how Questie actually loads the quest database
-- It's closer to how WoW Lua works than standard Lua

local function test_questie_compile()
    -- Create a minimal WoW-like environment
    local env = {
        -- WoW globals that Questie expects
        QuestieDB = {},
        epochQuestDB = {},
        QuestieLoader = {
            ImportModule = function() return {} end
        },
        -- Basic Lua functions
        pairs = pairs,
        ipairs = ipairs,
        type = type,
        tostring = tostring,
        tonumber = tonumber,
        print = print,
        -- Allow setting values
        rawset = rawset,
        rawget = rawget,
        setmetatable = setmetatable,
        getmetatable = getmetatable,
    }
    
    -- Read the database file
    local file = io.open("../Database/Epoch/epochQuestDB.lua", "r")
    if not file then
        print("Error: Could not open database file")
        return false
    end
    
    local content = file:read("*all")
    file:close()
    
    -- Skip the first few lines that import modules and just get the table
    content = content:gsub("^.-epochQuestDB = {", "local epochQuestDB = {")
    content = content .. "\nreturn epochQuestDB"
    
    -- Try to compile it
    local func, err = load(content, "epochQuestDB.lua", "t", env)
    
    if not func then
        print("❌ Compilation error:")
        print(err)
        
        -- Try to extract line number
        local line_num = err:match(":(%d+):")
        if line_num then
            print("\n📍 Error is around line " .. (tonumber(line_num) - 1)) -- Subtract 1 because we added a line
        end
        return false
    end
    
    -- Try to execute it
    local success, result = pcall(func)
    if not success then
        print("❌ Runtime error:")
        print(result)
        
        -- Try to extract line number
        local line_num = result:match(":(%d+):")
        if line_num then
            print("\n📍 Error is around line " .. (tonumber(line_num) - 1))
        end
        return false
    end
    
    -- Check the result
    if type(result) ~= "table" then
        print("❌ Database didn't return a table")
        return false
    end
    
    -- Count quests
    local quest_count = 0
    for k, v in pairs(result) do
        if type(k) == "number" and type(v) == "table" then
            quest_count = quest_count + 1
            
            -- Basic structure validation
            if #v < 30 then
                print("⚠️  Quest " .. k .. " has only " .. #v .. " fields (expected 30)")
            end
            
            -- Check objectives field (position 10)
            local objectives = v[10]
            if objectives and type(objectives) == "table" then
                if #objectives ~= 6 then
                    print("⚠️  Quest " .. k .. " objectives has " .. #objectives .. " elements (expected 6)")
                end
            end
        end
    end
    
    print("✅ Database compiled successfully!")
    print("📊 Found " .. quest_count .. " quests")
    
    return true
end

-- Run the test
print("Testing Questie database compilation...")
print("")
test_questie_compile()