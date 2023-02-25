import arcade


def get_object_map_position(obj: arcade.Sprite):
    return int((obj.center_x - 24) / 48), int((obj.center_y - 24) / 48)
