-- gamemode/sh_nav_graph.lua
-- ============================================================================
-- EFT NAV GRAPH -- Shared (client + server)
-- ============================================================================
-- Lightweight waypoint-based pathfinding for complex EFT maps.
-- Designed for arenas: ~20-40 nodes per map covering spawn zones, platforms,
-- ramps, jump pads, and goal approaches.
--
-- Node: { id=int, pos=Vector, links={ [neighborId]={jump=bool} } }
--
-- On the server, sv_nav_editor.lua populates EFTNav.Nodes and syncs to clients.
-- On the client, cl_nav_editor.lua receives the sync and draws the overlay.
-- sv_bot_pathfinding.lua queries EFTNav.FindPath() as the primary pathfinder.
--
-- Fallback chain: EFTNav graph -> GMod NavMesh A* -> direct LOS steering
-- ============================================================================

EFTNav = EFTNav or {}
EFTNav.Nodes  = {}   -- [id:int] -> { id, pos=Vector, links={ [neighborId]={jump=bool} } }
EFTNav.NextId = 1    -- next auto-assign ID

--- Returns true if any nodes are loaded for the current map.
function EFTNav.IsLoaded()
    return next(EFTNav.Nodes) ~= nil
end

--- Returns the nearest node within maxDist units of pos, or nil if none.
---@param pos Vector
---@param maxDist number|nil (default: unlimited)
---@return table|nil node
function EFTNav.GetNearestNode(pos, maxDist)
    local best, bestSq = nil, maxDist and (maxDist * maxDist) or math.huge
    for _, node in pairs(EFTNav.Nodes) do
        local d = pos:DistToSqr(node.pos)
        if d < bestSq then
            best, bestSq = node, d
        end
    end
    return best
end

--- A* over the EFT node graph.
--- Returns an ordered array of nodes from the node nearest startPos to the
--- node nearest endPos, or nil if no path exists or no graph is loaded.
---@param startPos Vector
---@param endPos   Vector
---@return table[]|nil path  Array of node tables, index 1 = start
function EFTNav.FindPath(startPos, endPos)
    local startNode = EFTNav.GetNearestNode(startPos, 500)
    local endNode   = EFTNav.GetNearestNode(endPos,   500)
    if not startNode or not endNode then return nil end
    if startNode.id == endNode.id   then return { startNode } end

    local openSet  = { startNode }
    local cameFrom = {}                                          -- [nodeId] -> parentNode
    local gScore   = { [startNode.id] = 0 }
    local fScore   = { [startNode.id] = startNode.pos:Distance(endNode.pos) }

    while #openSet > 0 do
        -- Pick the open node with the lowest f-score.
        local current, currentIdx, lowestF = nil, nil, math.huge
        for i, n in ipairs(openSet) do
            local f = fScore[n.id] or math.huge
            if f < lowestF then current, currentIdx, lowestF = n, i, f end
        end

        if current.id == endNode.id then
            -- Reconstruct path from cameFrom chain.
            local path, curr = {}, current
            while curr do
                table.insert(path, 1, curr)
                curr = cameFrom[curr.id]
            end
            return path
        end

        table.remove(openSet, currentIdx)

        for neighborId, _ in pairs(current.links) do
            local neighbor = EFTNav.Nodes[neighborId]
            if not neighbor then continue end

            local g = (gScore[current.id] or 0) + current.pos:Distance(neighbor.pos)
            if g < (gScore[neighborId] or math.huge) then
                cameFrom[neighborId] = current
                gScore[neighborId]   = g
                fScore[neighborId]   = g + neighbor.pos:Distance(endNode.pos)

                local inOpen = false
                for _, n in ipairs(openSet) do
                    if n.id == neighborId then inOpen = true; break end
                end
                if not inOpen then table.insert(openSet, neighbor) end
            end
        end
    end

    return nil -- no path found
end

--- Serialize EFTNav to a JSON string for file storage and net messages.
---@return string
function EFTNav.Serialize()
    local t = { nextId = EFTNav.NextId, nodes = {} }
    for id, node in pairs(EFTNav.Nodes) do
        local links = {}
        for nid, link in pairs(node.links) do
            links[tostring(nid)] = { jump = link.jump }
        end
        t.nodes[tostring(id)] = {
            id    = id,
            pos   = { x = node.pos.x, y = node.pos.y, z = node.pos.z },
            links = links,
        }
    end
    return util.TableToJSON(t, true)
end

--- Deserialize a JSON string into EFTNav.Nodes/NextId.
---@param str string
---@return boolean success
function EFTNav.Deserialize(str)
    local t = util.JSONToTable(str)
    if not t then return false end
    EFTNav.Nodes  = {}
    EFTNav.NextId = t.nextId or 1
    for _, nodeData in pairs(t.nodes or {}) do
        local id    = nodeData.id
        local links = {}
        for nidStr, linkData in pairs(nodeData.links or {}) do
            links[tonumber(nidStr)] = { jump = linkData.jump or false }
        end
        EFTNav.Nodes[id] = {
            id    = id,
            pos   = Vector(nodeData.pos.x, nodeData.pos.y, nodeData.pos.z),
            links = links,
        }
    end
    return true
end
