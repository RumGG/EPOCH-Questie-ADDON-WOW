#!/usr/bin/env lua
-- Syntax checker for Questie database files
-- Checks for common Lua table syntax errors

local function check_file(filename)
    local file = io.open(filename, "r")
    if not file then
        print("Error: Cannot open " .. filename)
        return false
    end
    
    local content = file:read("*all")
    file:close()
    
    -- Try to load the file as Lua code
    local func, err = loadstring(content)
    if not func then
        print("SYNTAX ERROR in " .. filename)
        print(err)
        return false
    else
        print("✓ " .. filename .. " - No syntax errors found")
        return true
    end
end

-- Check both database files
print("Checking Questie database files for syntax errors...\n")

local files = {
    "Database/Epoch/epochNpcDB.lua",
    "Database/Epoch/epochQuestDB.lua"
}

local all_good = true
for _, file in ipairs(files) do
    if not check_file(file) then
        all_good = false
    end
end

if all_good then
    print("\n✅ All files are syntactically correct!")
else
    print("\n❌ Syntax errors found - fix them before proceeding")
end