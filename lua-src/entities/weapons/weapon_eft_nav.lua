-- entities/weapons/weapon_eft_nav.lua
-- ============================================================================
-- EFT NAV EDITOR SWEP
-- ============================================================================
-- Point-and-click nav graph editor for superadmins.
-- Obtain with the console command:  eft_nav_tool
--
-- Controls:
--   LMB             Place a node at your crosshair. Auto-links to the last
--                   placed node using the current link type (walk or jump).
--   RMB             Click a node to select it (green glow).
--                   Click a second node to link them.
--                   Click the same node again, or empty space, to deselect.
--   R (Reload)      Delete the node nearest your crosshair.
--   eft_nav_jumpmode   Toggle WALK / JUMP mode for the next link.
--   eft_nav_draw 1     Enable the nav overlay (blue spheres + coloured lines).
--   eft_nav_save       Write the finished graph to disk.
-- ============================================================================
AddCSLuaFile()

SWEP.PrintName           = "EFT Nav Tool"
SWEP.Author              = "EFT"
SWEP.Purpose             = "Nav graph editing"
SWEP.Slot                = 1
SWEP.SlotPos             = 99

SWEP.Primary.ClipSize    = -1
SWEP.Primary.DefaultClip = -1
SWEP.Primary.Automatic   = false
SWEP.Primary.Ammo        = "none"
SWEP.Primary.Delay       = 0

SWEP.Secondary.ClipSize    = -1
SWEP.Secondary.DefaultClip = -1
SWEP.Secondary.Automatic   = false
SWEP.Secondary.Ammo        = "none"
SWEP.Secondary.Delay       = 0

SWEP.ShowViewModel       = false
SWEP.ShowWorldModel      = false
SWEP.ViewModel           = "models/weapons/c_arms_citizen.mdl"
SWEP.WorldModel          = ""

-- How close (HU) a crosshair hit must be to a node to target it.
local PICK_RADIUS = 150

-- ============================================================================
-- Helper: nearest node within radius of a world position.
-- Shared (used on both client and server).
-- ============================================================================
local function NearestNodeTo(pos, radius)
    if not EFTNav or not EFTNav.Nodes then return nil end
    local best, bestSq = nil, radius * radius
    for _, node in pairs(EFTNav.Nodes) do
        local d = node.pos:DistToSqr(pos)
        if d < bestSq then best, bestSq = node, d end
    end
    return best
end

-- ============================================================================
-- Server-side: place, select/link, delete
-- ============================================================================

function SWEP:PrimaryAttack()
    self:SetNextPrimaryFire(CurTime() + 0.25)   -- throttle on both sides
    if not SERVER then return end

    local owner = self.Owner
    if not IsValid(owner) or not owner:IsSuperAdmin() then return end

    local tr = owner:GetEyeTrace()
    if not tr.Hit then return end

    local pos     = tr.HitPos
    local ts      = EFTNav.GetToolState(owner)
    local oldLast = ts.lastNodeId

    -- Place node
    local id = EFTNav.NextId
    EFTNav.NextId        = EFTNav.NextId + 1
    EFTNav.Nodes[id]     = { id = id, pos = pos, links = {} }

    -- Auto-link to last placed node (bidirectional)
    if oldLast and EFTNav.Nodes[oldLast] then
        EFTNav.Nodes[oldLast].links[id] = { jump = ts.jumpMode }
        EFTNav.Nodes[id].links[oldLast] = { jump = ts.jumpMode }
        EFTNav.NavMsg(owner, "Placed #" .. id .. " ↔ #" .. oldLast
            .. (ts.jumpMode and " [jump]" or " [walk]"))
    else
        EFTNav.NavMsg(owner, "Placed #" .. id .. " (no auto-link — no previous node)")
    end

    ts.lastNodeId = id
    EFTNav.BroadcastGraph()
    EFTNav.SendToolStatus(owner)
end

function SWEP:SecondaryAttack()
    self:SetNextSecondaryFire(CurTime() + 0.25)
    if not SERVER then return end

    local owner = self.Owner
    if not IsValid(owner) or not owner:IsSuperAdmin() then return end

    local tr     = owner:GetEyeTrace()
    local ts     = EFTNav.GetToolState(owner)
    local target = tr.Hit and NearestNodeTo(tr.HitPos, PICK_RADIUS) or nil

    if not target then
        -- Clicked empty space — deselect
        if ts.pendingLinkId then
            ts.pendingLinkId = nil
            EFTNav.NavMsg(owner, "Deselected.")
            EFTNav.SendToolStatus(owner)
        end
        return
    end

    if not ts.pendingLinkId then
        -- First click: select this node
        ts.pendingLinkId = target.id
        EFTNav.NavMsg(owner, "Selected #" .. target.id .. " — RMB another node to link.")

    elseif ts.pendingLinkId == target.id then
        -- Clicked same node: deselect
        ts.pendingLinkId = nil
        EFTNav.NavMsg(owner, "Deselected.")

    else
        -- Second click on a different node: link them
        local n1 = EFTNav.Nodes[ts.pendingLinkId]
        if n1 then
            n1.links[target.id]           = { jump = ts.jumpMode }
            target.links[ts.pendingLinkId] = { jump = ts.jumpMode }
            EFTNav.NavMsg(owner, "Linked #" .. ts.pendingLinkId .. " ↔ #" .. target.id
                .. (ts.jumpMode and " [jump]" or " [walk]"))
            EFTNav.BroadcastGraph()
        end
        ts.pendingLinkId = nil
    end

    EFTNav.SendToolStatus(owner)
end

function SWEP:Reload()
    -- R key: delete node nearest crosshair
    if not SERVER then return end

    local owner = self.Owner
    if not IsValid(owner) or not owner:IsSuperAdmin() then return end

    local tr = owner:GetEyeTrace()
    if not tr.Hit then return end

    local ts     = EFTNav.GetToolState(owner)
    local target = NearestNodeTo(tr.HitPos, PICK_RADIUS)

    if not target then
        EFTNav.NavMsg(owner, "No node within " .. PICK_RADIUS .. " HU of crosshair.")
        return
    end

    local id = target.id
    EFTNav.Nodes[id] = nil
    for _, node in pairs(EFTNav.Nodes) do node.links[id] = nil end

    -- Clear stale tool state references
    if ts.lastNodeId    == id then ts.lastNodeId    = nil end
    if ts.pendingLinkId == id then ts.pendingLinkId = nil end

    EFTNav.NavMsg(owner, "Deleted node #" .. id)
    EFTNav.BroadcastGraph()
    EFTNav.SendToolStatus(owner)
end

-- ============================================================================
-- Shared
-- ============================================================================

function SWEP:DrawWorldModel() end   -- hide world model

-- ============================================================================
-- Client-side: tool state sync, HUD panel, in-world highlights
-- ============================================================================
if not CLIENT then return end

-- Local mirror of server-side tool state, updated via EFTNav_ToolStatus.
local toolState = { lastNodeId = -1, pendingLinkId = -1, jumpMode = false }

net.Receive("EFTNav_ToolStatus", function()
    toolState.lastNodeId    = net.ReadInt(16)
    toolState.pendingLinkId = net.ReadInt(16)
    toolState.jumpMode      = net.ReadBool()
end)

function SWEP:DrawViewModel()        end
function SWEP:DrawWeaponSelection()  end
function SWEP:PreDrawViewModel(vm)   vm:SetMaterial("engine/occlusionproxy") end

-- ── HUD panel ───────────────────────────────────────────────────────────────

function SWEP:DrawHUD()
    local sw, sh = ScrW(), ScrH()
    local x = sw * 0.5
    local y = sh - 140

    local modeStr = toolState.pendingLinkId > 0
        and ("LINKING FROM #" .. toolState.pendingLinkId)
        or  "PLACE"
    local jumpStr  = toolState.jumpMode and "JUMP" or "WALK"
    local lastStr  = toolState.lastNodeId > 0 and ("#" .. toolState.lastNodeId) or "none"
    local jumpCol  = toolState.jumpMode and Color(255, 200, 50) or Color(60, 220, 255)

    draw.RoundedBox(6, x - 200, y, 400, 100, Color(0, 0, 0, 170))
    draw.SimpleText("EFT NAV EDITOR",          "DermaDefaultBold", x, y + 10, Color(100, 200, 255), TEXT_ALIGN_CENTER, TEXT_ALIGN_CENTER)
    draw.SimpleText("Mode: " .. modeStr,       "DermaDefault",     x, y + 28, Color(255, 255, 255), TEXT_ALIGN_CENTER, TEXT_ALIGN_CENTER)
    draw.SimpleText("Link type: " .. jumpStr,  "DermaDefault",     x, y + 44, jumpCol,              TEXT_ALIGN_CENTER, TEXT_ALIGN_CENTER)
    draw.SimpleText("Last node: " .. lastStr,  "DermaDefault",     x, y + 60, Color(200, 200, 200), TEXT_ALIGN_CENTER, TEXT_ALIGN_CENTER)
    draw.SimpleText(
        "LMB: place  |  RMB: select/link  |  R: delete  |  eft_nav_jumpmode: toggle jump  |  eft_nav_save: save",
        "DermaDefault", x, y + 80, Color(130, 130, 130), TEXT_ALIGN_CENTER, TEXT_ALIGN_CENTER)
end

-- ── In-world highlights ─────────────────────────────────────────────────────
-- Orange sphere  = node your crosshair is hovering (pick target)
-- Green sphere   = node selected for linking
-- Yellow line    = preview link from selected node to crosshair

hook.Add("PostDrawOpaqueRenderables", "EFTNavTool_Highlights", function()
    local lp = LocalPlayer()
    if not IsValid(lp) then return end
    local wep = lp:GetActiveWeapon()
    if not IsValid(wep) or wep:GetClass() ~= "weapon_eft_nav" then return end
    if not EFTNav or not EFTNav.IsLoaded() then return end

    local tr      = lp:GetEyeTrace()
    local hitPos  = tr.Hit and tr.HitPos or nil

    -- Nearest node to crosshair
    local hoverNode = hitPos and NearestNodeTo(hitPos, PICK_RADIUS) or nil

    render.SetColorMaterialIgnoreZ()

    -- Orange: hover target
    if hoverNode then
        render.DrawSphere(hoverNode.pos + Vector(0, 0, 18), 14, 12, 12, Color(255, 140, 0, 220))
    end

    -- Green: pending link node + yellow preview line
    if toolState.pendingLinkId > 0 then
        local pendNode = EFTNav.Nodes[toolState.pendingLinkId]
        if pendNode then
            local p = pendNode.pos + Vector(0, 0, 18)
            render.DrawSphere(p, 14, 12, 12, Color(50, 255, 100, 220))
            if hitPos then
                render.DrawLine(p, hitPos + Vector(0, 0, 18), Color(255, 220, 0, 200), true)
            end
        end
    end
end)
