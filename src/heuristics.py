import math
from heapq import heappush, heappop

def heuristic(state, choice, goals, columns):
    if choice == 'w':
        return bipartite(state, columns, goals)
    if choice == 'g':
        return greedy_barpartite(state, columns, goals)
    if choice == 'h':
        return hungarian(state, columns, goals)
    nearest = 0
    for box in state.boxes:
        val = []
        for goal in goals:
            if choice == 'e':
                # find euclidean distance from one box to one goal
                val.append(euclidean(box, goal, columns))

            elif choice == 'm':
                # calculate manhattan distance from one box to one goal
                val.append(manhattan(box, goal, columns))

            elif choice == 'm2':
                val.append(manhattan2(box, goal, columns, state.player))

            elif choice == 'e2':
                val.append(euclidean2(box, goal, columns, state.player))

        # for each box, determine the nearest goal
        nearest += min(val)

    # return min of all calculated distances
    return nearest


def manhattan(x_pos,y_pos,columns):
    x = (x_pos // columns, x_pos % columns)
    y = (y_pos // columns, y_pos % columns)
    return abs(y[0]-x[0])+abs(y[1]-x[1])


def euclidean(x_pos,y_pos,columns):
    x = (x_pos // columns, x_pos % columns)
    y = (y_pos // columns, y_pos % columns)
    return math.ceil(math.sqrt((x[0]-y[0])**2+(x[1]-y[1])**2))


def manhattan2(box,goal,columns, player_pos):
    x = (box // columns, box % columns)
    y = (goal // columns, goal % columns)
    player = (player_pos // columns, player_pos % columns)
    return abs(y[0]-x[0])+abs(y[1]-x[1]) + abs(player[0]-x[0]) + abs(player[1]-x[1])


def euclidean2(x_pos,y_pos,columns, player_pos):
    x = (x_pos // columns, x_pos % columns)
    y = (y_pos // columns, y_pos % columns)
    player = (player_pos // columns, player_pos % columns)
    return math.ceil(math.sqrt((x[0]-y[0])**2+(x[1]-y[1])**2) + math.sqrt((x[0]-player[0])**2+(x[1]-player[1])**2))


def bipartite(state, columns, goals):
    # generate all possible combinations of goals for each block
    solutions = []  # matrix
    for b in state.boxes:
        solution = []
        for g in goals:
            sol = (b, g, manhattan(b, g, columns))
            solution.append(sol)
        solutions.append(solution)

    # for sol in solutions:
    #     print sol
    # print "------"

    # Select the best
    best = float('inf')
    for s in solutions[0]:
        used_goal = set([])
        used_block = set([])
        solution = []

        used_goal.add(s[1]) # goal
        used_block.add(s[0]) # box
        solution.append(s)
        h = s[2] # manhattan distance
        for lin in solutions:
            for col in lin:
                if col[1] not in used_goal and col[0] not in used_block:
                    solution.append(col)
                    used_goal.add(col[1])
                    used_block.add(col[0])
                    h = h + col[2]
                    break
        if h < best:
            best = h
            result = solution

    # print "-------"
    # print(result)
    # print(best)

    w = state.player
    d = float('inf')
    v = None

    for x in state.boxes:
        if x not in goals:
            if manhattan(w, x, columns) < d:
                d = manhattan(w, x, columns)
                v = x
    if v is not None:
        best = best + d

    return best

def greedy_barpartite(state, columns, goals): # best for now
    # generate all possible combinations of goals for each block
    edges = []
    for b in state.boxes:
        if b not in goals:
            for g in goals:
                if g not in state.boxes:
                    heappush(edges, (manhattan(b, g, columns), b, g))

    #Find the sum of the top 3 pairings
    heuristic_val = 0
    used_goal = set([])
    used_box = set([])
    while edges:
        val, box, goal = heappop(edges)

        if (box not in used_box) and (goal not in used_goal):
            used_box.add(box)
            used_goal.add(goal)
            heuristic_val +=  val

    return heuristic_val

def hungarian(state, columns, goals): # best for now
    # generate all possible combinations of goals for each block
    heuristic_val = 0
    for b in state.boxes:
        if b not in goals:
            for g in goals:
                if g not in state.boxes:
                    heuristic_val += (manhattan(b, g, columns))
    return heuristic_val


