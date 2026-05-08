-- gamemode/cl_nav_editor.lua
-- ============================================================================
-- EFT NAV EDITOR -- Client
-- ============================================================================
-- Receives the nav graph from the server and draws an in-world overlay.
-- Enable with:  eft_nav_draw 1  (or toggle via the convar)
--
-- Overlay legend:
--   Blue sphere   = node (ID shown as text within 800 u)
--   Cyan line     = walk link
--   Yellow line   = jump link
--   (x) text      = number of connections on that node
-- ============================================================================

local cvarDraw = CreateClientConVar("eft_nav_draw", "0", false, false,
    "Draw EFT nav graph overlay. 1 = on, 0 = off.")

-- ============================================================================
-- Network receive
-- ============================================================================

-- Small graphs: single uncompressed JSON string (backwards compatible)
net.Receive("EFTNav_Sync", function()
    local str = net.ReadString()
    EFTNav.Deserialize(str)
end)

-- Large graphs: compressed + chunked
local _chunkBuffer = {}
local _chunkExpected = 0
local _chunkTotalLen = 0

net.Receive("EFTNav_SyncChunk", function()
    local chunkIdx    = net.ReadUInt(8)
    local totalChunks = net.ReadUInt(8)
    local totalLen    = net.ReadUInt(32)
    local chunkLen    = net.ReadUInt(16)
    local chunkData   = net.ReadData(chunkLen)

    -- Reset buffer if this is a new transmission
    if chunkIdx == 1 then
        _chunkBuffer = {}
        _chunkExpected = totalChunks
        _chunkTotalLen = totalLen
    end

    _chunkBuffer[chunkIdx] = chunkData

    -- Check if all chunks arrived
    local received = 0
    for _ in pairs(_chunkBuffer) do received = received + 1 end

    if received >= _chunkExpected then
        -- Reassemble in order
        local parts = {}
        for i = 1, _chunkExpected do
            parts[i] = _chunkBuffer[i] or ""
        end
        local compressed = table.concat(parts)
        local json = util.Decompress(compressed)

        if json then
            EFTNav.Deserialize(json)
            chat.AddText(Color(100, 200, 255), "[EFTNav] Graph received (" .. table.Count(EFTNav.Nodes) .. " nodes)")
        else
            chat.AddText(Color(255, 100, 100), "[EFTNav] ERROR: Failed to decompress graph data")
        end

        _chunkBuffer = {}
    end
end)

net.Receive("EFTNav_Msg", function()
    local msg = net.ReadString()
    chat.AddText(Color(100, 200, 255), msg)
end)

-- ============================================================================
-- Rendering
-- ============================================================================

local COL_NODE_FILL = Color(50,  140, 255, 200)
local COL_WALK      = Color(60,  220, 255)
local COL_JUMP      = Color(255, 200,  50)
local COL_LABEL     = Color(255, 255, 255)
local COL_LABEL_BG  = Color(0,   0,   0,  140)

local NODE_RADIUS  = 10
local DRAW_DIST    = 3000   -- nodes farther than this aren't rendered
local LABEL_DIST   = 900    -- node IDs shown only within this distance

hook.Add("PostDrawOpaqueRenderables", "EFTNav_Draw3D", function()
    if not cvarDraw:GetBool() then return end
    if not EFTNav.IsLoaded() then return end

    local eyePos  = EyePos()
    local distSq  = DRAW_DIST * DRAW_DIST
    local mat     = Material("sprites/light_glow02_add")

    render.SetColorMaterialIgnoreZ()

    for _, node in pairs(EFTNav.Nodes) do
        local nodeWorld = node.pos + Vector(0, 0, 18)
        if nodeWorld:DistToSqr(eyePos) > distSq then continue end

        -- Sphere
        render.DrawSphere(nodeWorld, NODE_RADIUS, 12, 12, COL_NODE_FILL)

        -- Links (draw only once per pair: lower-ID side draws it)
        for neighborId, link in pairs(node.links) do
            if node.id > neighborId then continue end  -- avoid double-draw
            local neighbor = EFTNav.Nodes[neighborId]
            if not neighbor then continue end

            local col = link.jump and COL_JUMP or COL_WALK
            render.DrawLine(nodeWorld, neighbor.pos + Vector(0, 0, 18), col, true)
        end
    end
end)

-- Node ID labels (2D, drawn in HUD pass to get text rendering)
hook.Add("HUDPaint", "EFTNav_Labels", function()
    if not cvarDraw:GetBool() then return end
    if not EFTNav.IsLoaded() then return end

    local eyePos  = EyePos()
    local distSq  = LABEL_DIST * LABEL_DIST

    for _, node in pairs(EFTNav.Nodes) do
        local worldPos = node.pos + Vector(0, 0, 32)
        if worldPos:DistToSqr(eyePos) > distSq then continue end

        local screen = worldPos:ToScreen()
        if not screen.visible then continue end

        local linkCount = table.Count(node.links)
        local label     = "#" .. node.id .. " (" .. linkCount .. ")"

        -- Tiny background pill for readability
        local tw = string.len(label) * 4 + 6
        draw.RoundedBox(3, screen.x - tw * 0.5, screen.y - 8, tw, 14, COL_LABEL_BG)
        draw.SimpleText(label, "DermaDefault", screen.x, screen.y,
            COL_LABEL, TEXT_ALIGN_CENTER, TEXT_ALIGN_CENTER)
    end
end)

-- ============================================================================
-- Toggle command (convenience shortcut — the convar eft_nav_draw 0/1 also works directly)
-- ============================================================================
concommand.Add("eft_nav_toggle", function(_, _, args)
    local cur = cvarDraw:GetBool()
    RunConsoleCommand("eft_nav_draw", cur and "0" or "1")
    chat.AddText(Color(100, 200, 255), "[EFTNav] Overlay " .. (cur and "OFF" or "ON"))
end)
