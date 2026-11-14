"""D* Lite (Koenig & Likhachev, 2002) on an 8-connected grid.

Cells are flat indices (row * width + col). Edge costs are directed:
costs[d][u] is the cost of moving from cell u in direction MOVES[d],
float("inf") when the move is blocked or leaves the grid.
"""
import heapq

INF = float("inf")
MOVES = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


class DStarLite:
    def __init__(self, costs, width, start, goal, min_step_cost):
        """min_step_cost: lowest cost of any straight (non-diagonal) move;
        diagonal moves must cost at least sqrt(2) times that."""
        self.costs = costs
        self.width = width
        self.n = len(costs[0])
        self.off = [dr * width + dc for dr, dc in MOVES]
        self.start = self.last = start
        self.goal = goal
        self.hmin = min_step_cost
        self.km = 0.0
        self.g = [INF] * self.n
        self.rhs = [INF] * self.n
        self.rhs[goal] = 0.0
        self.heap = []
        self.queued = {}
        self._push(goal)
        self._compute()

    def _h(self, a, b):
        dr = abs(a // self.width - b // self.width)
        dc = abs(a % self.width - b % self.width)
        return self.hmin * (max(dr, dc) + 0.41421356 * min(dr, dc))

    def _key(self, u):
        m = min(self.g[u], self.rhs[u])
        return (m + self._h(self.start, u) + self.km, m)

    def _push(self, u):
        k = self._key(u)
        self.queued[u] = k
        heapq.heappush(self.heap, (k, u))

    def _preds(self, u):
        for d, off in enumerate(self.off):
            v = u - off
            if 0 <= v < self.n and self.costs[d][v] < INF:
                yield v

    def _update(self, u):
        if u != self.goal:
            best = INF
            for d, off in enumerate(self.off):
                c = self.costs[d][u]
                if c < INF and c + self.g[u + off] < best:
                    best = c + self.g[u + off]
            self.rhs[u] = best
        if self.g[u] != self.rhs[u]:
            self._push(u)
        else:
            self.queued.pop(u, None)

    def _compute(self):
        g, rhs, heap, queued = self.g, self.rhs, self.heap, self.queued
        while heap:
            k, u = heap[0]
            if queued.get(u) != k:  # stale entry
                heapq.heappop(heap)
                continue
            if not (k < self._key(self.start) or rhs[self.start] != g[self.start]):
                break
            heapq.heappop(heap)
            del queued[u]
            if k < self._key(u):
                self._push(u)
            elif g[u] > rhs[u]:
                g[u] = rhs[u]
                for p in self._preds(u):
                    self._update(p)
            else:
                preds = list(self._preds(u))
                g[u] = INF
                self._update(u)
                for p in preds:
                    self._update(p)

    def cost(self):
        """Cost from the current start to the goal (inf if unreachable)."""
        return self.g[self.start]

    def path(self):
        """Cells from the current start to the goal, or None if unreachable."""
        if self.g[self.start] == INF:
            return None
        u, out = self.start, [self.start]
        while u != self.goal:
            u = min(
                (u + off for d, off in enumerate(self.off) if self.costs[d][u] < INF),
                key=lambda v, u=u: self.costs[self.off.index(v - u)][u] + self.g[v],
            )
            out.append(u)
        return out

    def replan(self, start, blocked):
        """Move the rover to `start`, mark newly seen `blocked` cells, repair the plan."""
        self.km += self._h(self.last, start)
        self.start = self.last = start
        for b in blocked:
            sources = list(self._preds(b))
            for d, off in enumerate(self.off):
                self.costs[d][b] = INF
                v = b - off
                if 0 <= v < self.n:
                    self.costs[d][v] = INF
            self._update(b)
            for v in sources:
                self._update(v)
        self._compute()
