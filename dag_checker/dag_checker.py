from collections import deque
from typing import List, Tuple, Dict

def is_acyclic(commit_list: List[Tuple[str, List[str]]]) -> bool:
    parent_map: Dict[str, List[str]] = {}
    for commit_id, parents in commit_list:
        parent_map[commit_id] = parents.copy()

    if not parent_map:
        return True

    id_to_index: Dict[str, int] = {}
    for idx, cid in enumerate(parent_map.keys()):
        id_to_index[cid] = idx

    n = len(id_to_index)
    adj: List[List[int]] = [[] for _ in range(n)]
    in_degree: List[int] = [0] * n

    for cid, parents in parent_map.items():
        u = id_to_index[cid]
        for pid in parents:
            v = id_to_index[pid]
            adj[u].append(v)
            in_degree[v] += 1

    queue = deque()
    for idx in range(n):
        if in_degree[idx] == 0:
            queue.append(idx)

    visited_count = 0
    while queue:
        node = queue.popleft()
        visited_count += 1
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    return (visited_count == n)

