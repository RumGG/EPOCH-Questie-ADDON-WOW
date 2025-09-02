# Modular Fix System for Questie Database

## Problem Analysis

The pfQuest converter created multiple levels of over-nesting in quest objectives:

1. **Quadruple braces**: `{{{{id,count}}}}` 
2. **Triple braces**: `{{{id,count}}}`
3. **Double braces in wrong position**: `{{id,count}}` not wrapped in 6-element structure

## Correct Structure

Quest objectives (field 10) should be:
```lua
{creatures, objects, items, reputation, killCredit, spells}
```

Where each sub-field is either `nil` or a table:
- Creatures: `{{id,count,"name"}, {id,count,"name"}}`
- Objects: `{{id,count}}`  
- Items: `{{id,count}}`

## Fix Modules

### Module 1: Fix Quadruple Braces
- Removes one level of nesting from quadruple patterns
- Handles wrapped objectives structures

### Module 2: Fix Triple Braces  
- Fixes triple-braced items/objects
- Preserves proper 6-element structures

### Module 3: Fix Double Braces
- Wraps loose double-brace objectives in proper structure
- **ISSUE**: Can create new quadruple braces if content is already triple-braced

### Module 4: Validation
- Checks brace balance
- Identifies remaining issues
- Provides detailed report

## Running the Fix

```bash
cd modular_fixes
python3 master_fix.py
```

## Current Issues

1. Module 3 needs to check if content is already triple-braced before wrapping
2. Some triple-brace patterns are legitimate (proper 6-element structures)
3. Need smarter pattern matching to avoid over-correction

## Manual Fixes Required

After running the modules, some quests still need manual fixes:
- Complex nested structures
- Mixed patterns in same quest
- Edge cases not covered by patterns