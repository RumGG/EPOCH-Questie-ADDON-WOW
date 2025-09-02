-- Test if the database file is valid Lua syntax
-- Run with: lua test_lua_validity.lua

local function testFile(filename)
    print("Testing " .. filename .. "...")
    
    -- Try to load the file
    local func, err = loadfile(filename)
    if not func then
        print("ERROR: Failed to load file!")
        print(err)
        return false
    end
    
    -- Try to execute it
    local success, result = pcall(func)
    if not success then
        print("ERROR: Failed to execute file!")
        print(result)
        return false
    end
    
    -- Check if the expected table exists
    if epochQuestDataMerged then
        local count = 0
        for k,v in pairs(epochQuestDataMerged) do
            count = count + 1
        end
        print("SUCCESS: Found epochQuestDataMerged with " .. count .. " entries")
        
        -- Test a few random entries to make sure they're accessible
        local testIds = {11, 76, 26107, 28901}
        for _, id in ipairs(testIds) do
            if epochQuestDataMerged[id] then
                local quest = epochQuestDataMerged[id]
                if quest[1] then
                    print("  Quest " .. id .. ": " .. quest[1])
                else
                    print("  Quest " .. id .. ": [No name]")
                end
            end
        end
        
        return true
    else
        print("ERROR: epochQuestDataMerged table not found!")
        return false
    end
end

-- Test the file
local filename = arg and arg[1] or "epochQuestDB_FINAL.lua"
if testFile(filename) then
    print("\nDatabase is valid and can be loaded!")
else
    print("\nDatabase has errors and cannot be loaded!")
    os.exit(1)
end