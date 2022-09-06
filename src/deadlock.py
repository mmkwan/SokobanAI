from copy import deepcopy

from src.helpers import get_new_position

ACTION_DICT = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1)
}


def is_blocked_axis(state, box_pos, pos1, pos2, walls, deadlocks, goals, columns, frozen_boxes):
    if pos1 in walls or pos2 in walls:  # there is a wall on at least one direction
        return True
    if pos1 in deadlocks and pos2 in deadlocks:  # both directions are dead squares
        return True
    if pos1 in state.boxes:  # check if there is a box in pos1 and if it's blocked
        walls.add(box_pos)
        return recursive_frozen_box_detection(state, pos1, walls, deadlocks, goals, columns, frozen_boxes)
    if pos2 in state.boxes:  # check if there is a box in pos2 and if it's blocked
        walls.add(box_pos)
        return recursive_frozen_box_detection(state, pos2, walls, deadlocks, goals, columns, frozen_boxes)
    return False


def recursive_frozen_box_detection(state, box_pos, walls, deadlocks, goals, columns, frozen_boxes):
    """marks a box frozen if it's blocked both vertically and horizontally"""
    [up, down, left, right] = [get_new_position(box_pos, ACTION_DICT[step], columns) for step in ACTION_DICT]
    if not is_blocked_axis(state, box_pos, left, right, walls, deadlocks, goals, columns, frozen_boxes):  # check horizontal axis
        return False
    if not is_blocked_axis(state, box_pos, up, down, walls, deadlocks, goals, columns, frozen_boxes):  # check vertical axis
        return False
    frozen_boxes.add(box_pos)
    return True


class DeadlockDetection:
    """A static class to run deadlock detection algorithms"""

    @staticmethod
    def detect_dead_squares(walls, goals, rows, columns):
        """Detects dead squares, runs as a preprocessor when the map is loaded"""
        visited_squares = set()  # stores integer positions of visited squares
        for goal in goals:
            lifo = [goal]
            while len(lifo) > 0:
                square = lifo.pop()
                visited_squares.add(square)
                for direction in ACTION_DICT:
                    action = ACTION_DICT[direction]
                    new_box_pos = get_new_position(square, action, columns)
                    new_player_pos = get_new_position(new_box_pos, action, columns)
                    if new_player_pos < 0 or new_player_pos >= rows*columns:
                        continue
                    if new_box_pos in walls or new_player_pos in walls:
                        continue
                    if new_box_pos not in visited_squares:
                        lifo.append(new_box_pos)
        deadlocks = set()
        for square in range(0, rows*columns):
            if not (square in walls or square in visited_squares):
                deadlocks.add(square)
        return deadlocks

    @staticmethod
    def detect_frozen_boxes(state, box_pos, walls, deadlocks, goals, columns):
        frozen_boxes = set()
        walls_copy = deepcopy(walls)  # create a copy of walls so we don't change actual map
        potential_deadlock = recursive_frozen_box_detection(state, box_pos, walls_copy, deadlocks, goals, columns, frozen_boxes)
        if potential_deadlock:
            for b in frozen_boxes:
                if b not in goals:
                    return True
            return False
        return False




