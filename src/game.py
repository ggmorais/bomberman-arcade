import arcade
import random

from src.sprites.bombs import Bomb, BombExplosion
from src.sprites.items import Item
from src.sprites.player import Player
from src.sprites.blocks import Block, DestructibleBlock, BlockDestroy, Ground
from src.constants import *


class Game(arcade.Window):
    """Main application class."""

    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        self.player = Player(self, 192, 190)
        self.game_objects = {
            Ground: arcade.SpriteList(),
            Bomb: arcade.SpriteList(),
            Item: arcade.SpriteList(),
            Block: arcade.SpriteList(),
            DestructibleBlock: arcade.SpriteList(),
            BombExplosion: arcade.SpriteList(),
            BlockDestroy: arcade.SpriteList(),
        }
        self.bombs_collision = arcade.SpriteList()
        self.objects_map = {}

        map_objects = list(reversed(DESIGN_MAP.split("\n")))

        for y, line in enumerate(map_objects):
            for x, block in enumerate(line.strip()):
                if block == "B":
                    self.add_game_object(Block(x, y))
                if block == " " and random.randint(0, 10) in range(4):
                    player_pos_x, player_pos_y = self.player.get_map_position()

                    if x not in (player_pos_x, player_pos_x - 1) or y not in (
                        player_pos_y,
                        player_pos_y + 1,
                    ):
                        self.add_game_object(DestructibleBlock(x, y))

                        if random.randint(0, 20) == 1:
                            self.add_game_object(Item(x, y))

        # Add background with shadow
        for y, line in enumerate(map_objects):
            for x, block in enumerate(line.strip()):
                self.add_game_object(
                    Ground(
                        self,
                        x,
                        y,
                        name="GroundShadow"
                        if self.get_game_object(x, y + 1, Block)
                        or self.get_game_object(x, y + 1, DestructibleBlock)
                        else "Ground",
                    )
                )

        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player,
            [
                self.game_objects[Block],
                self.game_objects[DestructibleBlock],
                self.bombs_collision,
            ],
        )
        self.keys_enabled = ("SPACE", "RIGHT", "LEFT", "UP", "DOWN")
        self.keys_pressed = set()

        arcade.enable_timings()
        self.graph = arcade.PerfGraph(100, 100)

    def add_game_object(self, game_object: arcade.Sprite):
        self.game_objects.setdefault(type(game_object), arcade.SpriteList()).append(game_object)
        self.objects_map.setdefault(game_object.position, []).append(game_object)
        game_object.center_x = game_object.center_x * 48 + 24
        game_object.center_y = game_object.center_y * 48 + 24

    def get_game_objects_by_type(self, object_type: arcade.Sprite):
        return self.game_objects[object_type]

    def get_all_game_objects(self):
        return self.game_objects.values()

    def get_game_object(self, x: int, y: int, object_type: arcade.Sprite):
        for item in self.objects_map.get((x, y), []):
            if isinstance(item, object_type):
                return item

    def get_object_map_position(self, game_object: arcade.Sprite):
        for pos, values in self.objects_map.items():
            if game_object in values:
                return pos

    def delete_game_object(self, game_object: arcade.Sprite):
        # Remove all bomb explosions from the same bomb origin together to avoid visual bugs
        if isinstance(game_object, BombExplosion):
            if game_object not in self.game_objects[BombExplosion]:
                return
            for item in self.game_objects[BombExplosion]:
                if item.bomb_origin == game_object.bomb_origin:
                    self.game_objects[BombExplosion].remove(item)
                    # self.objects_map[obj_pos].remove(game_object)

                    obj_pos = (int(item.center_x / 48), int(item.center_y / 48))

                    if item in self.objects_map[obj_pos]:
                        self.objects_map[obj_pos].remove(item)

            return

        obj_pos = (int(game_object.center_x / 48), int(game_object.center_y / 48))
        if game_object in self.objects_map[obj_pos]:
            self.objects_map[obj_pos].remove(game_object)

        self.game_objects[type(game_object)].remove(game_object)

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        pass

    def on_draw(self):
        """Render the screen."""

        self.clear()

        for obj in self.get_all_game_objects():
            obj.draw(pixelated=True)
            # obj.draw_hit_boxes()

        self.player.draw(pixelated=True)
        # self.player.draw_hit_box()

        self.graph.draw()

    def on_update(self, delta_time: float):
        self.player.on_update(delta_time, self.keys_pressed)
        # self.game_objects[Bomb].on_update(delta_time)

        for obj in self.get_all_game_objects():
            obj.on_update(delta_time)

        self.physics_engine.update()

        self.graph.update_graph(delta_time)
        self.graph.update()

    def on_key_press(self, symbol: int, modifiers: int):
        for key in self.keys_enabled:
            if symbol == getattr(arcade.key, key):
                self.keys_pressed.add(key)

    def on_key_release(self, symbol: int, modifiers: int):
        for key in self.keys_enabled:
            if symbol == getattr(arcade.key, key):
                self.keys_pressed.remove(key)
