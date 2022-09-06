class State:
    player = ()
    boxes = set()
    unplaced_boxes = 0
    action_list = ''
    ancestors = set([])
    penalty = 0
  
    def __init__(self, player, boxes, unplaced_boxes):
        self.player = player
        self.boxes = boxes
        self.unplaced_boxes = unplaced_boxes
        self.action_list = ''

    def is_solution(self):
        return self.unplaced_boxes == 0

    def is_equal(self, other_state):
        if self.player != other_state.player:
            return False
        if self.unplaced_boxes != other_state.unplaced_box:
            return False
        return sorted(self.boxes) == sorted(other_state.boxes)

    # Put box representation into a tuple for fast loop checking - Mason K.
    def compressed_rep(self):
        return self.player, tuple(sorted(list(self.boxes)))

    def inherit_ancestors(self, node, cmp_rep):
        self.ancestors = node.ancestors.copy()
        self.ancestors.add(cmp_rep)

    def is_loop(self):
        if self.compressed_rep() in self.ancestors:
            return True
        return False

    # added for priority queue comparison
    def __lt__(self, other):
        return True
