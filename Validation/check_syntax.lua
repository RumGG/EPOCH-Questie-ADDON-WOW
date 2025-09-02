#!/usr/bin/env lua

-- Simple syntax checker for epochQuestDB.lua
local function check_syntax(filename)
    local file = io.open(filename, "r")
    if not file then
        print("Error: Could not open file " .. filename)
        return false
    end
    
    local content = file:read("*all")
    file:close()
    
    -- Try to load the file as Lua code
    local func, err = load(content, filename)
    
    if func then
        print("✅ Syntax check passed! No Lua syntax errors found.")
        
        -- Try to actually run it to check for runtime errors
        local success, runtime_err = pcall(func)
        if success then
            print("✅ File executed successfully without runtime errors.")
        else
            print("⚠️  Runtime error (this might be expected if the file needs WoW environment):")
            print("   " .. tostring(runtime_err))
        end
        return true
    else
        print("❌ Syntax error found:")
        print(err)
        
        -- Try to extract line number from error
        local line_num = err:match(":(%d+):")
        if line_num then
            print("\n📍 Error is around line " .. line_num)
            
            -- Try to show the problematic line
            local lines = {}
            for line in content:gmatch("[^\n]+") do
                table.insert(lines, line)
            end
            
            local line_idx = tonumber(line_num)
            if line_idx and lines[line_idx] then
                print("\nLine " .. line_num .. ":")
                print(lines[line_idx])
            end
        end
        return false
    end
end

-- Check the database file
local db_path = "../Database/Epoch/epochQuestDB.lua"
print("Checking syntax of " .. db_path .. "...")
print("")
check_syntax(db_path)