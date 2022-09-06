from copy import deepcopy

import pygame
from pygame.locals import *

from src.game_world import ACTION_DICT
from src.helpers import get_new_position


def to_game_coor(pos, columns):
    return pos % columns * 32, pos // columns * 32


# for visual representation and simaluting the game with user actions
class GameEngine:
    screen = None
    state = None

    def init_env(self, game_world):
        pygame.init()
        self.screen = pygame.display.set_mode((game_world.columns * 32, game_world.rows * 32))
        self.state = deepcopy(game_world.initial_state)
        self.draw(game_world)

    def draw(self, game_world):
        self.screen.fill((245, 235, 192))
        for w in game_world.walls:
            self.screen.blit(pygame.image.load('./assets/wall.png'), to_game_coor(w, game_world.columns))

        for s in game_world.goals:
            self.screen.blit(pygame.image.load('./assets/spot.png'), to_game_coor(s, game_world.columns))
        for b in self.state.boxes:
            if b in game_world.goals:
                self.screen.blit(pygame.image.load('./assets/box_s.png'), to_game_coor(b, game_world.columns))
            else:
                self.screen.blit(pygame.image.load('./assets/box.png'), to_game_coor(b, game_world.columns))
        # comment out to display tunnel squares
        # for t in game_world.tunnels:
        #     c = to_game_coor(t, game_world.columns)
        #     self.screen.fill((157, 157, 157), (c[0], c[1], 32, 32))

        # comment out to display dead squares
        # for t in game_world.deadlocks:
        #     c = to_game_coor(t, game_world.columns)
        #     self.screen.fill((195, 40, 40), (c[0], c[1], 32, 32))

        player = pygame.image.load('./assets/groot.png')
        self.screen.blit(player, to_game_coor(self.state.player, game_world.columns))
        pygame.display.update()

    def start_game(self, game_world):
        self.init_env(game_world)
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # if it is quit the game
                    pygame.quit()
                if event.type == pygame.KEYDOWN:
                    new_state = None
                    if event.key == K_UP:
                        new_state = self.move(self.state, game_world, 'UP')
                    elif event.key == K_LEFT:
                        new_state = self.move(self.state, game_world, 'LEFT')
                    elif event.key == K_DOWN:
                        new_state = self.move(self.state, game_world, 'DOWN')
                    elif event.key == K_RIGHT:
                        new_state = self.move(self.state, game_world, 'RIGHT')
                    self.complete_move(game_world, new_state)

    def simulate_actions(self, game_world, action_list):
        self.init_env(game_world)
        for action in action_list:
            pygame.time.wait(50)
            new_state = None
            if action == 'U':
                new_state = self.move(self.state, game_world, 'UP')
            elif action == 'L':
                new_state = self.move(self.state, game_world, 'LEFT')
            elif action == 'D':
                new_state = self.move(self.state, game_world, 'DOWN')
            elif action == 'R':
                new_state = self.move(self.state, game_world, 'RIGHT')
            self.complete_move(game_world, new_state)

    def move(self, state, world, action):
        """Returns a new state given action, returns None if the action is not legal"""
        new_pos = get_new_position(state.player, ACTION_DICT[action], world.columns)
        if new_pos in world.walls:
            return
        if new_pos in state.boxes:
            new_box_pos = get_new_position(new_pos, ACTION_DICT[action], world.columns)
            if new_box_pos in world.walls:
                return
            if new_box_pos in state.boxes:
                return
            state.boxes.remove(new_pos)
            state.boxes.add(new_box_pos)
            if new_pos in world.goals:  # moving box out of goal state
                state.unplaced_boxes = state.unplaced_boxes + 1
            if new_box_pos in world.goals:
                state.unplaced_boxes = state.unplaced_boxes - 1

        state.player = new_pos
        return state

    def complete_move(self, game_world, new_state):
        if not new_state:
            return
        self.state = new_state
        self.draw(game_world)
        if self.state.is_solution():
            font = pygame.font.Font('freesansbold.ttf', 15)
            text = font.render('CONGRATS', True, (0, 0, 0))
            text_rect = text.get_rect()
            text_rect.center = (game_world.columns * 16, game_world.rows * 16)
            self.screen.blit(text, text_rect)
            pygame.display.update()
            pygame.time.wait(2000)
            pygame.quit()
