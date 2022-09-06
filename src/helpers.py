def read_input(file_name):
    file = open(file_name, 'r')
    lines = file.readlines()
    [columns, rows] = [int(x) for x in lines[0].strip().split(' ')]

    wall_array = lines[1].strip().split(' ')
    walls = set([(int(wall_array[i]) - 1)*columns + (int(wall_array[i + 1]) - 1) for i in range(1, len(wall_array), 2)])

    box_array = lines[2].strip().split(' ')
    boxes = set([(int(box_array[i]) - 1)*columns + (int(box_array[i + 1]) - 1) for i in range(1, len(box_array), 2)])

    goals_array = lines[3].strip().split(' ')
    goals = set([(int(goals_array[i]) - 1)*columns + (int(goals_array[i + 1]) - 1) for i in range(1, len(goals_array), 2)])

    player = [int(x)-1 for x in lines[4].strip().split(' ')]
    player = player[0]*columns + player[1]
    unplaced_boxes = 0
    for box_p in boxes:
        if box_p not in goals:
            unplaced_boxes += 1

    return {
        'columns': columns,
        'rows': rows,
        'walls': walls,
        'boxes': boxes,
        'player': player,
        'goals': goals,
        'unplaced_boxes': unplaced_boxes
    }


def read_map(file_name):
    file = open('./input/{}.txt'.format(file_name), 'r')
    lines = file.readlines()
    walls = set()
    boxes = set()
    goals = set()
    player = 0
    columns = max([len(x.strip()) for x in lines])
    unplaced_boxes = 0
    for r in range(len(lines)):
        line = lines[r]
        for c in range(len(line)):
            char = line[c]
            int_post = get_int_position((r, c), columns)
            if char == '#':
                walls.add(int_post)
            elif char == '$':
                boxes.add(int_post)
                unplaced_boxes += 1
            elif char == '.':
                goals.add(int_post)
            elif char == '@':
                player = int_post
            elif char == '*':
                boxes.add(int_post)
                goals.add(int_post)

    return {
        'columns': columns,
        'rows': len(lines),
        'walls': walls,
        'boxes': boxes,
        'player': player,
        'goals': goals,
        'unplaced_boxes': unplaced_boxes
    }


def add_tuples(t0, t1):
    return t0[0] + t1[0], t0[1] + t1[1]


def get_int_position(pos, c):
    """converts tuple position to integer position"""
    return pos[0] * c + pos[1]


def get_new_position(pos, step, c):
    """returns an integer position given old position pos (int), step(tuple) and columns size c"""
    return pos + step[0]*c + step[1]
