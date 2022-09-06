import time

from heapq import heappush, heappop
from copy import deepcopy

from timeout_decorator import timeout_decorator

from src.heuristics import heuristic
from src.deadlock import DeadlockDetection
from src.helpers import read_input, read_map, get_new_position
from src.state import State

ACTION_DICT = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1)
}

CONFIG = {
    'tunnelmacro': True,
    'deadsquares': True,
    'frozenboxes': True
}


class GameWorld:
    initial_state = None
    walls = set()  # wall locations
    goals = set()  # goal locations
    deadlocks = set()  # dead squares
    tunnels = set()  # tunnel squares
    columns = 0  # width of the map
    rows = 0  # height of the map
    expand_count = 0

    def init(self, file_name, input_type='text'):
        if input_type == 'text':
            s = read_input(file_name)
        else:
            s = read_map(file_name)
        self.walls = s['walls']
        self.goals = s['goals']
        self.columns = s['columns']
        self.rows = s['rows']
        self.initial_state = State(s['player'], s['boxes'], s['unplaced_boxes'])
        if CONFIG['deadsquares']:
            self.deadlocks = DeadlockDetection.detect_dead_squares(self.walls, self.goals, self.rows, self.columns)
        if CONFIG['tunnelmacro']:
            self.find_tunnels()

    def print_state(self, state):  # char matrix representation of a state
        res = [[' ' for c in range(1, self.columns + 1)] for r in range(1, self.rows + 1)]
        columns = self.columns
        for wall in self.walls:
            res[wall // columns][wall % columns] = '#'
        for box in state.boxes:
            if box in self.goals:
                res[box // columns][box % columns] = '*'  # box is on goal cell
            else:
                res[box // columns][box % columns] = '$'
        for g in self.goals:
            if g not in state.boxes:
                if g == state.player:
                    res[g // columns][g % columns] = '+'  # player is on goal state
                else:
                    res[g // columns][g % columns] = '.'
        if res[state.player // columns][state.player % columns] == ' ':
            res[state.player // columns][state.player % columns] = '@'
        print('\n'.join([''.join(i) for i in res]))

    def get_legal_children(self, state):
        """Returns a state's legal child states"""
        children = []
        for action in ACTION_DICT:
            new_state = self.move(state, action)
            if new_state:
                children.append(new_state)
        return children

    def move(self, state, action):
        """Returns a new state given action, returns None if the action is not legal"""
        new_pos = get_new_position(state.player, ACTION_DICT[action], self.columns)
        if new_pos in self.walls:
            return
        pushing = False
        new_box_pos = None
        if new_pos in state.boxes:
            new_box_pos = get_new_position(new_pos, ACTION_DICT[action], self.columns)
            if new_box_pos in self.walls:
                return
            if new_box_pos in self.deadlocks:
                return
            if new_box_pos in state.boxes:
                return
            pushing = True
        new_state = deepcopy(state)
        new_state.unplaced_boxes = state.unplaced_boxes
        if pushing:  # handle box pushing
            # move box and player
            new_state.boxes.remove(new_pos)
            new_state.boxes.add(new_box_pos)

            if new_pos in self.goals:  # moving box out of goal state
                new_state.unplaced_boxes = new_state.unplaced_boxes + 1
            if new_box_pos in self.goals:
                new_state.unplaced_boxes = new_state.unplaced_boxes - 1

        new_state.player = new_pos
        # add action to action list
        new_state.action_list = state.action_list + action[0:1]
        if new_state.unplaced_boxes != 0:  # run if it's not goal state
            # run frozen box detection only if we did a push
            if CONFIG['frozenboxes'] and pushing and DeadlockDetection.detect_frozen_boxes(new_state, new_box_pos, self.walls, self.deadlocks, self.goals, self.columns):
                # print('Pruning due to frozen box')
                return

            # run tunnel macro
            if CONFIG['tunnelmacro']:
                self.tunnel_macro(new_state, action, pushing)
        return new_state

    def tunnel_macro(self, state, action, pushing):
        if state.player not in self.tunnels:
            return
        step = ACTION_DICT[action]
        box_pos = get_new_position(state.player, step, self.columns)
        if pushing and box_pos not in self.tunnels:
            return
        # print('Entering tunnel')
        # self.print_state(state)
        pos = box_pos if pushing else state.player
        while pos in self.tunnels:
            new_pos = get_new_position(pos, step, self.columns)
            if new_pos in self.walls:
                break
            if new_pos in state.boxes or new_pos in self.goals:
                break
            pos = new_pos
            state.action_list += action[0:1]

        if pushing:
            state.boxes.remove(box_pos)
            state.boxes.add(pos)
            state.player = get_new_position(pos, (step[0]*-1, step[1]*-1), self.columns)
        else:
            state.player = pos
        # print('Exiting tunnel')
        # self.print_state(state)

    def find_tunnels(self):
        for i in range(self.columns*self.rows):
            if i in self.walls:
                continue
            if i in self.goals:
                continue
            [up, down, left, right] = [get_new_position(i, ACTION_DICT[step], self.columns) for step in ACTION_DICT]
            if up in self.walls and down in self.walls:
                self.tunnels.add(i)
                continue
            if left in self.walls and right in self.walls:
                self.tunnels.add(i)

    def run_dls(self, limit):
        lifo = [self.initial_state]
        result = 'fail'
        explored = []
        while len(lifo) > 0:
            node = lifo.pop()
            if node.is_solution():
                return node
            explored.append(node.compressed_rep())
            if len(node.action_list) > limit:
                result = 'cutoff'
            else:
                for child in self.get_legal_children(node):
                    # self.print_state(child)
                    if child.compressed_rep() not in explored:
                        lifo.append(child)
        return result


    def AStar(self, max_f, heuristic_choice):
        """Astar search algorithm"""
        pqueue = []
        heappush(pqueue, (0 + heuristic(self.initial_state, heuristic_choice, self.goals, self.columns), self.initial_state))
        depth = 0
        explored = set([])
        # start = time.process_time()
        # heuristic_time = 0
        while pqueue:
            cur_f, node = heappop(pqueue)
            explored.add(node.compressed_rep())
            if cur_f > depth:
                depth = cur_f
               # depth_end = time.process_time()
               # print("Time elapsed:", depth_end - start)
               # print("Time elapsed calculating the heuristic", heuristic_time)
               # print("Searching at depth: " + str(depth))
            children = self.get_legal_children(node)
            self.expand_count = self.expand_count + 1
            for child in children:
                if child.compressed_rep() not in explored:
                    if child.is_solution():
                        return "Success", child
                    # heuristic_start = time.process_time()
                    child_f = len(child.action_list) + heuristic(child, heuristic_choice, self.goals, self.columns)
                    # heuristic_end = time.process_time()
                    # heuristic_time += heuristic_end - heuristic_start
                    heappush(pqueue, (child_f, child))
        return "No Solution", None

    def IDAStar(self, max_f, heuristic_choice):
        """A single iteration of IDAstar"""
        lifo = [self.initial_state]
        next_max_f = float("inf")
        while lifo:
            node = lifo.pop()
            if node.is_solution():
                return "Success", node
            children = self.get_legal_children(node)
            for child in children:
                child.inherit_ancestors(node, node.compressed_rep())
                if not child.is_loop():
                    cur_f = len(child.action_list) + heuristic(child, heuristic_choice, self.goals, self.columns)
                    if cur_f > max_f:
                        next_max_f = min(next_max_f, cur_f)
                    else:
                        lifo.append(child)
        return "Failure", next_max_f

    @timeout_decorator.timeout(60*60)
    def search(self, choice):
        """Entry point for IDAStar or Astar"""
        depth = 0
        while True:
            # print("Searching at depth: " + str(depth))
            res = self.AStar(depth, choice)
            if res[0] == "Success":
                return res[1]
            if res[0] == "No Solution":
                return 'fail'
            else:
                depth = res[1]

