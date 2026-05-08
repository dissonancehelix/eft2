-- gamemode/sv_nav_editor.lua
-- ============================================================================
-- EFT NAV EDITOR -- Server
-- ============================================================================
-- Console commands for building per-map waypoint graphs for bot pathfinding.
-- Requires superadmin. Graph auto-loads on map start and is saved to
-- data/eft_nav/<mapname>.txt (JSON).
--
-- WORKFLOW:
--   1. In-game as superadmin, enable overlay:  eft_nav_draw 1  (client convar)
--   2. Walk to a spot and run:                  eft_nav_node
--      → Prints the new node's ID in chat.
--   3. Connect two nodes:                       eft_nav_link <id1> <id2>
--      Jump connection (bot will jump):         eft_nav_link <id1> <id2> jump
--      One-way connection:                      eft_nav_link <id1> <id2> [jump] one
--   4. Remove a bad connection:                 eft_nav_unlink <id1> <id2>
--   5. Move a node to your current position:    eft_nav_move <id>
--   6. Delete a node and all its links:         eft_nav_delete <id>
--   7. List all nodes:                          eft_nav_list
--   8. Save to disk:                            eft_nav_save
--      (auto-saved on clean map shutdown)
-- ============================================================================

local NAV_DIR = "eft_nav/"

local function NavFilePath()
    return NAV_DIR .. game.GetMap() .. ".txt"
end

-- ============================================================================
-- Network strings
-- ============================================================================
util.AddNetworkString("EFTNav_Sync")        -- server → all clients: full graph JSON (small graphs)
util.AddNetworkString("EFTNav_SyncChunk")   -- server → all clients: chunked graph data (large graphs)
util.AddNetworkString("EFTNav_Msg")         -- server → one client:  chat message
util.AddNetworkString("EFTNav_ToolStatus")  -- server → wielder:     nav tool state sync

local function NavMsg(ply, msg)
    if IsValid(ply) then
        net.Start("EFTNav_Msg")
            net.WriteString("[EFTNav] " .. msg)
        net.Send(ply)
    else
        print("[EFTNav] " .. msg)
    end
end
EFTNav.NavMsg = NavMsg   -- accessible from weapon_eft_nav SWEP

local CHUNK_SIZE = 60000 -- bytes per chunk (under 64KB net limit)

local function BroadcastGraph()
    local json = EFTNav.Serialize()
    local compressed = util.Compress(json)

    if not compressed then
        -- Fallback: try uncompressed if compression fails
        if #json < 60000 then
            net.Start("EFTNav_Sync")
                net.WriteString(json)
            net.Broadcast()
        else
            print("[EFTNav] ERROR: Graph too large and compression failed.")
        end
        return
    end

    local totalLen = #compressed
    local totalChunks = math.ceil(totalLen / CHUNK_SIZE)

    if totalChunks == 1 and totalLen < 60000 then
        -- Small enough: send as single message (backwards compatible)
        net.Start("EFTNav_Sync")
            net.WriteString(json)
        net.Broadcast()
        return
    end

    -- Large graph: send compressed chunks
    for i = 1, totalChunks do
        local startByte = (i - 1) * CHUNK_SIZE + 1
        local endByte = math.min(i * CHUNK_SIZE, totalLen)
        local chunk = string.sub(compressed, startByte, endByte)

        timer.Simple((i - 1) * 0.1, function() -- stagger to avoid net spam
            net.Start("EFTNav_SyncChunk")
                net.WriteUInt(i, 8)             -- chunk index (1-based)
                net.WriteUInt(totalChunks, 8)    -- total chunks
                net.WriteUInt(totalLen, 32)      -- total compressed length
                net.WriteUInt(#chunk, 16)        -- this chunk's length
                net.WriteData(chunk, #chunk)
            net.Broadcast()
        end)
    end

    print("[EFTNav] Broadcasting " .. totalLen .. " bytes in " .. totalChunks .. " chunks")
end
EFTNav.BroadcastGraph = BroadcastGraph   -- accessible from weapon_eft_nav SWEP

-- ============================================================================
-- Tool state  (used by weapon_eft_nav SWEP)
-- ============================================================================
EFTNav.ToolState = {}   -- [ply entity] -> { lastNodeId, pendingLinkId, jumpMode }

function EFTNav.GetToolState(ply)
    if not EFTNav.ToolState[ply] then
        EFTNav.ToolState[ply] = { lastNodeId = nil, pendingLinkId = nil, jumpMode = false }
    end
    return EFTNav.ToolState[ply]
end

function EFTNav.SendToolStatus(ply)
    if not IsValid(ply) then return end
    local ts = EFTNav.GetToolState(ply)
    net.Start("EFTNav_ToolStatus")
        net.WriteInt(ts.lastNodeId    or -1, 16)
        net.WriteInt(ts.pendingLinkId or -1, 16)
        net.WriteBool(ts.jumpMode)
    net.Send(ply)
end

-- ============================================================================
-- Load / Save
-- ============================================================================

function EFTNav.Load()
    local path = NavFilePath()
    if not file.Exists(path, "DATA") then
        EFTNav.Nodes  = {}
        EFTNav.NextId = 1
        print("[EFTNav] No graph for " .. game.GetMap() .. " — bots use NavMesh fallback.")
        return
    end
    local str = file.Read(path, "DATA")
    if EFTNav.Deserialize(str) then
        print("[EFTNav] Loaded " .. table.Count(EFTNav.Nodes) .. " nodes for " .. game.GetMap())
    else
        print("[EFTNav] Parse error for " .. game.GetMap() .. " — starting empty.")
        EFTNav.Nodes  = {}
        EFTNav.NextId = 1
    end
    BroadcastGraph()
end

function EFTNav.Save()
    file.CreateDir(NAV_DIR)
    file.Write(NavFilePath(), EFTNav.Serialize())
    print("[EFTNav] Saved " .. table.Count(EFTNav.Nodes) .. " nodes for " .. game.GetMap())
end

-- ============================================================================
-- Hooks
-- ============================================================================

-- Auto-load after world is ready (slight delay so all entities are spawned).
hook.Add("InitPostEntity", "EFTNav_Load", function()
    timer.Simple(1, EFTNav.Load)
end)

-- Sync graph to clients joining mid-session.
hook.Add("PlayerInitialSpawn", "EFTNav_LateJoin", function(ply)
    if not EFTNav.IsLoaded() then return end
    timer.Simple(3, function()
        if not IsValid(ply) then return end
        net.Start("EFTNav_Sync")
            net.WriteString(EFTNav.Serialize())
        net.Send(ply)
    end)
end)

-- ============================================================================
-- Admin guard
-- ============================================================================
local function RequireAdmin(ply)
    if IsValid(ply) and not ply:IsSuperAdmin() then
        NavMsg(ply, "Superadmin required.")
        return false
    end
    return true
end

-- ============================================================================
-- Console commands
-- ============================================================================

-- eft_nav_node [look]
-- Place a node at your feet. Pass "look" to snap to crosshair hit position.
concommand.Add("eft_nav_node", function(ply, _, args)
    if not RequireAdmin(ply) then return end

    local pos = IsValid(ply) and ply:GetPos() or Vector()
    if args[1] == "look" and IsValid(ply) then
        local tr = ply:GetEyeTrace()
        if tr.Hit then pos = tr.HitPos end
    end

    local id = EFTNav.NextId
    EFTNav.NextId = EFTNav.NextId + 1
    EFTNav.Nodes[id] = { id = id, pos = pos, links = {} }

    NavMsg(ply, "Added node #" .. id .. " at " .. math.Round(pos.x) .. " " .. math.Round(pos.y) .. " " .. math.Round(pos.z))
    BroadcastGraph()
end)

-- eft_nav_link <id1> <id2> [jump] [one]
-- Connect two nodes. "jump" marks the link as requiring a jump.
-- "one" makes it one-way (id1 → id2 only); default is bidirectional.
concommand.Add("eft_nav_link", function(ply, _, args)
    if not RequireAdmin(ply) then return end

    local id1, id2 = tonumber(args[1]), tonumber(args[2])
    if not id1 or not id2 then
        NavMsg(ply, "Usage: eft_nav_link <id1> <id2> [jump] [one]")
        return
    end

    local isJump = (args[3] == "jump" or args[4] == "jump")
    local oneWay = (args[3] == "one"  or args[4] == "one")

    local n1, n2 = EFTNav.Nodes[id1], EFTNav.Nodes[id2]
    if not n1 or not n2 then NavMsg(ply, "Node not found."); return end

    n1.links[id2] = { jump = isJump }
    if not oneWay then n2.links[id1] = { jump = isJump } end

    NavMsg(ply, "Linked #" .. id1 .. (oneWay and " → " or " ↔ ") .. "#" .. id2
        .. (isJump and " [jump]" or " [walk]"))
    BroadcastGraph()
end)

-- eft_nav_unlink <id1> <id2>
-- Remove the connection between two nodes (both directions).
concommand.Add("eft_nav_unlink", function(ply, _, args)
    if not RequireAdmin(ply) then return end

    local id1, id2 = tonumber(args[1]), tonumber(args[2])
    if not id1 or not id2 then
        NavMsg(ply, "Usage: eft_nav_unlink <id1> <id2>")
        return
    end

    local n1, n2 = EFTNav.Nodes[id1], EFTNav.Nodes[id2]
    if n1 then n1.links[id2] = nil end
    if n2 then n2.links[id1] = nil end

    NavMsg(ply, "Unlinked #" .. id1 .. " and #" .. id2)
    BroadcastGraph()
end)

-- eft_nav_delete <id>
-- Delete a node and remove all links pointing to it.
concommand.Add("eft_nav_delete", function(ply, _, args)
    if not RequireAdmin(ply) then return end

    local id = tonumber(args[1])
    if not id then NavMsg(ply, "Usage: eft_nav_delete <id>"); return end
    if not EFTNav.Nodes[id] then NavMsg(ply, "Node #" .. id .. " not found."); return end

    EFTNav.Nodes[id] = nil
    for _, node in pairs(EFTNav.Nodes) do
        node.links[id] = nil
    end

    NavMsg(ply, "Deleted node #" .. id)
    BroadcastGraph()
end)

-- eft_nav_move <id> [look]
-- Snap a node to your current position (or crosshair with "look").
concommand.Add("eft_nav_move", function(ply, _, args)
    if not RequireAdmin(ply) then return end

    local id = tonumber(args[1])
    if not id then NavMsg(ply, "Usage: eft_nav_move <id> [look]"); return end

    local node = EFTNav.Nodes[id]
    if not node then NavMsg(ply, "Node #" .. id .. " not found."); return end

    local pos = IsValid(ply) and ply:GetPos() or Vector()
    if args[2] == "look" and IsValid(ply) then
        local tr = ply:GetEyeTrace()
        if tr.Hit then pos = tr.HitPos end
    end

    node.pos = pos
    NavMsg(ply, "Moved node #" .. id .. " to " .. math.Round(pos.x) .. " " .. math.Round(pos.y) .. " " .. math.Round(pos.z))
    BroadcastGraph()
end)

-- eft_nav_save
-- Write graph to data/eft_nav/<mapname>.txt.
concommand.Add("eft_nav_save", function(ply, _, _)
    if not RequireAdmin(ply) then return end
    EFTNav.Save()
    NavMsg(ply, "Saved " .. table.Count(EFTNav.Nodes) .. " nodes.")
end)

-- eft_nav_load
-- Reload graph from disk (discards unsaved edits).
concommand.Add("eft_nav_load", function(ply, _, _)
    if not RequireAdmin(ply) then return end
    EFTNav.Load()
    NavMsg(ply, "Loaded " .. table.Count(EFTNav.Nodes) .. " nodes.")
end)

-- eft_nav_clear
-- Wipe the in-memory graph. Does NOT auto-save.
concommand.Add("eft_nav_clear", function(ply, _, _)
    if not RequireAdmin(ply) then return end
    EFTNav.Nodes  = {}
    EFTNav.NextId = 1
    NavMsg(ply, "Graph cleared. Run eft_nav_save to persist.")
    BroadcastGraph()
end)

-- eft_nav_list
-- Print all nodes and their connections to the requesting player's chat.
concommand.Add("eft_nav_list", function(ply, _, _)
    if not RequireAdmin(ply) then return end
    local count = table.Count(EFTNav.Nodes)
    NavMsg(ply, count .. " nodes for " .. game.GetMap() .. ":")
    for id, node in SortedPairs(EFTNav.Nodes) do
        local links = {}
        for nid, link in SortedPairs(node.links) do
            table.insert(links, "#" .. nid .. (link.jump and "[J]" or ""))
        end
        NavMsg(ply, "  #" .. id .. " → " .. (next(links) and table.concat(links, " ") or "(no links)"))
    end
end)

-- eft_nav_jumpmode
-- Toggle the nav tool's link type between WALK and JUMP.
concommand.Add("eft_nav_jumpmode", function(ply, _, _)
    if not RequireAdmin(ply) then return end
    if not IsValid(ply) then return end
    local ts = EFTNav.GetToolState(ply)
    ts.jumpMode = not ts.jumpMode
    NavMsg(ply, "Link mode: " .. (ts.jumpMode and "JUMP" or "WALK"))
    EFTNav.SendToolStatus(ply)
end)

-- eft_nav_tool
-- Equip the nav editor SWEP (point-and-click graph builder).
concommand.Add("eft_nav_tool", function(ply, _, _)
    if not RequireAdmin(ply) then return end
    if not IsValid(ply) then NavMsg(ply, "Must be in-game as a player."); return end
    ply:Give("weapon_eft_nav")
    ply:SelectWeapon("weapon_eft_nav")
    NavMsg(ply, "Nav tool equipped — LMB: place  RMB: select/link  R: delete  eft_nav_jumpmode: toggle jump  eft_nav_save: save")
end)

-- ============================================================================
-- NAV AUTO-GENERATOR
-- ============================================================================
-- Converts GMod's auto-generated NavMesh into EFTNav waypoint nodes.
-- Run: eft_nav_autogen           → clears existing graph and generates fresh
-- Run: eft_nav_autogen keepold   → preserves existing nodes, fills gaps only
-- Then tweak with the SWEP editor and eft_nav_save.
-- ============================================================================

local AUTOGEN_MERGE_RADIUS    = 200  -- Merge candidates within this distance
local AUTOGEN_LINK_MAX_DIST   = 1200 -- Max distance to consider linking two nodes
local AUTOGEN_MIN_AREA_SIZE   = 1500 -- Skip nav areas smaller than this (sq units)
local AUTOGEN_HULL_MINS       = Vector(-16, -16, 0)
local AUTOGEN_HULL_MAXS       = Vector(16, 16, 72)

concommand.Add("eft_nav_autogen", function(ply, _, args)
    if not RequireAdmin(ply) then return end
    if not navmesh.IsLoaded() then
        NavMsg(ply, "No NavMesh loaded — run nav_generate first.")
        return
    end

    local keepOld = args[1] == "keepold"

    -- Build hazard cache if not done
    if not BotPathfinder.HazardCacheBuilt then
        -- Inline hazard build (same logic as sv_bot_pathfinding.lua)
        BotPathfinder.HazardAreas = {}
        local HAZARD_CLASSES = { trigger_hurt = true, trigger_ballreset = true, trigger_kill = true }
        for _, area in pairs(navmesh.GetAllNavAreas()) do
            local c0, c1, c2, c3 = area:GetCorner(0), area:GetCorner(1), area:GetCorner(2), area:GetCorner(3)
            local minZ = math.min(c0.z, c1.z, c2.z, c3.z)
            local maxZ = math.max(c0.z, c1.z, c2.z, c3.z)
            local mins = Vector(
                math.min(c0.x, c1.x, c2.x, c3.x),
                math.min(c0.y, c1.y, c2.y, c3.y),
                minZ - 128
            )
            local maxs = Vector(
                math.max(c0.x, c1.x, c2.x, c3.x),
                math.max(c0.y, c1.y, c2.y, c3.y),
                maxZ + 64
            )
            for _, ent in pairs(ents.FindInBox(mins, maxs)) do
                if HAZARD_CLASSES[ent:GetClass()] then
                    BotPathfinder.HazardAreas[area:GetID()] = true
                    break
                end
            end
        end
        BotPathfinder.HazardCacheBuilt = true
    end

    NavMsg(ply, "Generating EFTNav from NavMesh...")

    -- ── Step 1: Collect candidate positions from NavMesh areas ─────────────
    local candidates = {} -- { {pos=Vector, areaSize=number, areaId=number}, ... }
    local allAreas = navmesh.GetAllNavAreas()
    local skippedHazard, skippedSmall = 0, 0

    for _, area in pairs(allAreas) do
        local areaId = area:GetID()

        -- Skip hazard zones
        if BotPathfinder.HazardAreas[areaId] then
            skippedHazard = skippedHazard + 1
            continue
        end

        -- Skip tiny areas (ledge trim, narrow strips)
        local areaSize = area:GetSizeX() * area:GetSizeY()
        if areaSize < AUTOGEN_MIN_AREA_SIZE then
            skippedSmall = skippedSmall + 1
            continue
        end

        -- Use the area center, snapped to the floor
        local center = area:GetCenter()
        -- Trace down to get actual floor position (area center Z can be off on slopes)
        local trFloor = util.TraceLine({
            start = center + Vector(0, 0, 50),
            endpos = center - Vector(0, 0, 200),
            mask = MASK_SOLID_BRUSHONLY,
        })
        local nodePos = trFloor.Hit and trFloor.HitPos or center

        table.insert(candidates, {
            pos = nodePos,
            areaSize = areaSize,
            areaId = areaId,
        })
    end

    NavMsg(ply, "  Areas: " .. #allAreas .. " total, " .. #candidates .. " candidates ("
        .. skippedHazard .. " hazard, " .. skippedSmall .. " small)")

    -- ── Step 2: Merge nearby candidates ────────────────────────────────────
    -- Sort by area size descending so larger areas survive merging.
    table.sort(candidates, function(a, b) return a.areaSize > b.areaSize end)

    local merged = {} -- surviving candidate positions
    local mergedSet = {} -- quick lookup: index → true if consumed

    for i, cand in ipairs(candidates) do
        if mergedSet[i] then continue end

        -- This candidate survives. Consume all candidates within merge radius.
        table.insert(merged, cand.pos)
        for j = i + 1, #candidates do
            if not mergedSet[j] and cand.pos:Distance(candidates[j].pos) < AUTOGEN_MERGE_RADIUS then
                mergedSet[j] = true
            end
        end
    end

    NavMsg(ply, "  Merged " .. #candidates .. " candidates → " .. #merged .. " nodes (radius=" .. AUTOGEN_MERGE_RADIUS .. ")")

    -- ── Step 3: If keepold, filter out positions near existing nodes ───────
    if keepOld and EFTNav.IsLoaded() then
        local filtered = {}
        for _, pos in ipairs(merged) do
            local tooClose = false
            for _, node in pairs(EFTNav.Nodes) do
                if pos:Distance(node.pos) < AUTOGEN_MERGE_RADIUS then
                    tooClose = true
                    break
                end
            end
            if not tooClose then
                table.insert(filtered, pos)
            end
        end
        NavMsg(ply, "  Keepold: " .. (#merged - #filtered) .. " positions near existing nodes skipped")
        merged = filtered
    end

    -- ── Step 4: Create EFTNav nodes ───────────────────────────────────────
    if not keepOld then
        EFTNav.Nodes = {}
        EFTNav.NextId = 1
    end

    local newNodes = {} -- track new node IDs for linking
    for _, pos in ipairs(merged) do
        local id = EFTNav.NextId
        EFTNav.NextId = EFTNav.NextId + 1
        EFTNav.Nodes[id] = { id = id, pos = pos, links = {} }
        table.insert(newNodes, id)
    end

    NavMsg(ply, "  Created " .. #newNodes .. " new nodes (total: " .. table.Count(EFTNav.Nodes) .. ")")

    -- ── Step 5: Auto-link nodes with hull trace verification ──────────────
    -- Build flat list of ALL node IDs (old + new) for linking.
    local allNodeIds = {}
    for id, _ in pairs(EFTNav.Nodes) do
        table.insert(allNodeIds, id)
    end

    local walkLinks, jumpLinks, failedLinks = 0, 0, 0

    for i = 1, #allNodeIds do
        for j = i + 1, #allNodeIds do
            local idA, idB = allNodeIds[i], allNodeIds[j]
            local nodeA, nodeB = EFTNav.Nodes[idA], EFTNav.Nodes[idB]
            if not nodeA or not nodeB then continue end

            -- Skip if already linked
            if nodeA.links[idB] then continue end

            local dist = nodeA.pos:Distance(nodeB.pos)
            if dist > AUTOGEN_LINK_MAX_DIST then continue end

            local posA = nodeA.pos + Vector(0, 0, 10) -- slightly above floor
            local posB = nodeB.pos + Vector(0, 0, 10)
            local heightDiff = math.abs(nodeA.pos.z - nodeB.pos.z)

            -- Hull trace: can a player walk between these two points?
            local tr = util.TraceHull({
                start  = posA,
                endpos = posB,
                mins   = AUTOGEN_HULL_MINS,
                maxs   = AUTOGEN_HULL_MAXS,
                mask   = MASK_SOLID_BRUSHONLY,
            })

            if not tr.Hit then
                -- Clear path → walk link
                nodeA.links[idB] = { jump = false }
                nodeB.links[idA] = { jump = false }
                walkLinks = walkLinks + 1
            elseif heightDiff > 40 and heightDiff < 120 then
                -- Height difference within jump range. Check if it's a
                -- ledge (needs jump) or a ramp (walkable slope).
                -- Trace at the midpoint downward to check surface normal.
                local midPos = (posA + posB) * 0.5 + Vector(0, 0, 50)
                local trMid = util.TraceLine({
                    start = midPos,
                    endpos = midPos - Vector(0, 0, 150),
                    mask = MASK_SOLID_BRUSHONLY,
                })

                local isRamp = trMid.Hit and trMid.HitNormal.z > 0.5

                if isRamp then
                    -- Walkable slope — try a less strict trace (at ground level only)
                    local trLow = util.TraceHull({
                        start  = posA,
                        endpos = posB,
                        mins   = Vector(-16, -16, 0),
                        maxs   = Vector(16, 16, 36), -- half-height hull
                        mask   = MASK_SOLID_BRUSHONLY,
                    })
                    if not trLow.Hit then
                        nodeA.links[idB] = { jump = false }
                        nodeB.links[idA] = { jump = false }
                        walkLinks = walkLinks + 1
                    else
                        -- Ramp but obstructed — walk link anyway, let wall avoidance handle it
                        nodeA.links[idB] = { jump = false }
                        nodeB.links[idA] = { jump = false }
                        walkLinks = walkLinks + 1
                    end
                else
                    -- Ledge — test if head is clear (jumpable)
                    local trHead = util.TraceHull({
                        start  = posA + Vector(0, 0, 72),
                        endpos = posB + Vector(0, 0, 72),
                        mins   = Vector(-16, -16, 0),
                        maxs   = Vector(16, 16, 10),
                        mask   = MASK_SOLID_BRUSHONLY,
                    })
                    if not trHead.Hit then
                        -- Up direction gets jump, down direction gets walk (drop)
                        local highId = nodeA.pos.z > nodeB.pos.z and idA or idB
                        local lowId  = nodeA.pos.z > nodeB.pos.z and idB or idA
                        EFTNav.Nodes[lowId].links[highId]  = { jump = true }   -- jump up
                        EFTNav.Nodes[highId].links[lowId]  = { jump = false }  -- drop down
                        jumpLinks = jumpLinks + 1
                    else
                        failedLinks = failedLinks + 1
                    end
                end
            else
                failedLinks = failedLinks + 1
            end
        end
    end

    NavMsg(ply, "  Links: " .. walkLinks .. " walk, " .. jumpLinks .. " jump, " .. failedLinks .. " blocked")

    -- ── Step 6: Detect isolated nodes (no links) ─────────────────────────
    local isolated = 0
    for _, id in ipairs(newNodes) do
        local node = EFTNav.Nodes[id]
        if node and not next(node.links) then
            isolated = isolated + 1
        end
    end

    if isolated > 0 then
        NavMsg(ply, "  WARNING: " .. isolated .. " isolated nodes (no links) — fix manually or delete")
    end

    -- ── Done ─────────────────────────────────────────────────────────────
    -- Auto-save to disk so the graph persists and loads on next map start.
    EFTNav.Save()
    NavMsg(ply, "Auto-generation complete. Graph saved to disk.")
    NavMsg(ply, "Run: changelevel " .. game.GetMap() .. "  to reload with the new graph.")
    NavMsg(ply, "Then: eft_nav_draw 1  to visualize and clean up with the nav SWEP.")

    -- Try to broadcast (may fail on very large graphs before chunked code is loaded)
    pcall(BroadcastGraph)
end)

