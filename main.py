import sys
import time

# from src.game_engine import GameEngine
from src.game_world import GameWorld

world = GameWorld()


def run(filename, file_type, choice):
    world.init(filename, file_type)
    end_state = None
    try:
        end_state = world.search(choice)
    except Exception:
        print('Timeout on {}'.format(filename))
        exit(-1)
    if end_state and end_state != 'fail' and end_state != 'cutoff':
        print('{} {}'.format(len(end_state.action_list), ' '.join(end_state.action_list)))
    else:
        print(end_state)


def run_simulation(filename, file_type, choice):
    start = time.process_time()
    world.init(filename, file_type)
    end_state = None
    try:
        end_state = world.search(choice)
    except Exception:
        print('Timeout on {}'.format(filename))
        exit(-1)
    print('Time elapsed:', time.process_time() - start, ' seconds')
    print('Expand count:', world.expand_count)
    print('Solution length: ', len(end_state.action_list))
    print('Output: {} {}'.format(len(end_state.action_list), ''.join(end_state.action_list)))
    if end_state and end_state != 'fail' and end_state != 'cutoff':
        # engine = GameEngine()
        # engine.simulate_actions(world, end_state.action_list)
        print('{} {}'.format(len(end_state.action_list), ' '.join(end_state.action_list)))
    else:
        print(end_state)


def play_game(filename, file_type):
    world.init(filename, file_type)
    # engine = GameEngine()
    # engine.start_game(world)


def run_set(choice):
    start = time.process_time()
    for i in range(1, 11):
        world.init('set1/' + str(i), 'map')
        world.search(choice)
        print('Finished ' + str(i))
    print('Time elapsed:', time.process_time() - start, ' seconds')


def run_benchmark_set(choice, t):
    benchmark_files = ('00', '01', '02', '03', '04', '05a', '05b', '06a', '06b', '06c', '07a', '07b', '08', '09', '10')

    best_time = float('inf')
    total_time = 0
    for j in range(10):  # run 10 simulations for each map
        print('Running simulation {}'.format(j+1))
        time_elapsed = 0
        for file in benchmark_files:
            start = time.process_time()
            world.init('./input/benchmark/{}{}.txt'.format('input' if t == 'map' else 'sokoban', file), t)
            try:
                world.search(choice)
                time_elapsed += time.process_time() - start
                print('Time elapsed for input{} on simulation {}:'.format(file, j+1), '{:.4f}'.format(time.process_time() - start), ' seconds')
            except Exception:
                print('Timeout on input{}'.format(file))
        if time_elapsed < best_time:
            best_time = time_elapsed
        total_time += time_elapsed
        print('Total time elapsed on simulation {}:'.format(j + 1),
              '{:.4f}'.format(time_elapsed), ' seconds')
    print('Average time for benchmark set run is {:.4f}'.format(total_time/10))


# run_simulation('input07', 'map', 'h')
# play_game('benchmark/input06a', 'map')
# run_set('h')
# run_simulation('benchmark/input07b', 'map', 'h')
# run_benchmark_set('h', 'text')

if len(sys.argv) == 1:
    print('Please enter the pathname of the map as an argument')
    print('Example: python main.py path_to_file/sokoban.txt')
    exit(0)

filename = sys.argv[1]
run(filename, 'text', 'h')
