-- Test fix for GameTooltip not showing on map pins when Questie runs standalone
-- The issue: Tooltips work with ElvUI but not without it
-- 
-- Possible causes:
-- 1. GameTooltip parent not set properly
-- 2. GameTooltip frame strata issues
-- 3. GameTooltip not being shown after being populated
-- 4. GameTooltip being hidden by another addon hook

-- The fix should ensure GameTooltip:
-- 1. Has UIParent as parent (not nil)
-- 2. Has proper frame strata (TOOLTIP)
-- 3. Is explicitly shown after SetOwner and content addition
-- 4. Is not accidentally hidden

print("=== Tooltip Fix Analysis ===")
print("")
print("Problem: Map pin tooltips don't show with Questie standalone")
print("Works with: ElvUI enabled")
print("")
print("ElvUI likely does one of these:")
print("1. Sets GameTooltip:SetParent(UIParent) on initialization")
print("2. Ensures GameTooltip visibility in OnShow hooks")
print("3. Fixes frame strata/level issues")
print("")
print("Fix to apply in MapIconTooltip:Show():")
print("  -- Ensure tooltip has a parent (fixes standalone issue)")
print("  if not Tooltip:GetParent() then")
print("    Tooltip:SetParent(UIParent)")
print("  end")
print("  ")
print("  Tooltip:SetOwner(self, 'ANCHOR_CURSOR')")
print("  -- ... add content ...")
print("  Tooltip:SetFrameStrata('TOOLTIP')")
print("  Tooltip:Show()")
print("")
print("This ensures GameTooltip is properly parented even without ElvUI")