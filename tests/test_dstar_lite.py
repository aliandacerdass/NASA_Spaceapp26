import heapq
import random

from route.dstar_lite import INF, MOVES, DStarLite

W = H = 30


def random_costs(rng):
    """Directed costs on a W x H grid with ~20% blocked cells."""
    blocked = {i for i in range(W * H) if rng.random() < 0.2}
    costs = []
    for dr, dc in MOVES:
        step = 1.0 if dr == 0 or dc == 0 else 2 ** 0.5
        layer = []
        for u in range(W * H):
            r, c = u // W + dr, u % W + dc
            ok = 0 <= r < H and 0 <= c < W and u not in blocked and r * W + c not in blocked
            layer.append(step * rng.uniform(1.0, 5.0) if ok else INF)
        costs.append(layer)
    return costs, blocked


def dijkstra(costs, start, goal):
    off = [dr * W + dc for dr, dc in MOVES]
    dist = {start: 0.0}
    heap = [(0.0, start)]
    while heap:
        d, u = heapq.heappop(heap)
        if u == goal:
            return d
        if d > dist[u]:
            continue
        for i, o in enumerate(off):
            c = costs[i][u]
            if c < INF and d + c < dist.get(u + o, INF):
                dist[u + o] = d + c
                heapq.heappush(heap, (d + c, u + o))
    return INF


def path_cost(costs, path):
    off = [dr * W + dc for dr, dc in MOVES]
    return sum(costs[off.index(b - a)][a] for a, b in zip(path, path[1:]))


def test_matches_dijkstra_and_replans():
    for seed in range(25):
        rng = random.Random(seed)
        costs, blocked = random_costs(rng)
        free = [i for i in range(W * H) if i not in blocked]
        start, goal = rng.sample(free, 2)
        want = dijkstra(costs, start, goal)

        planner = DStarLite(costs, W, start, goal, min_step_cost=1.0)
        assert abs(planner.cost() - want) < 1e-6 or planner.cost() == want == INF
        path = planner.path()
        if path is None:
            continue
        assert abs(path_cost(costs, path) - want) < 1e-6

        # Drive along the path, discovering a hidden obstacle a few times.
        for _ in range(4):
            path = planner.path()
            if path is None or len(path) < 4:
                break
            here = path[len(path) // 3]
            hidden = [c for c in path[len(path) // 3 + 1 : -1]][:2]
            planner.replan(here, hidden)
            want = dijkstra(costs, here, goal)  # costs were updated in place
            assert planner.cost() == want == INF or abs(planner.cost() - want) < 1e-6
            new_path = planner.path()
            if new_path is not None:
                assert not set(hidden) & set(new_path)
                assert abs(path_cost(costs, new_path) - want) < 1e-6
