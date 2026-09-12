from .structures import Position, Size
from .spritesheet import SpriteSheet

from mlx import Mlx
import os


def on_key(key, param):
    if key == 65307:  # ESC
        os._exit(0)


def main() -> int:
    mlx = Mlx()
    mlx_ptr = mlx.mlx_init()
    if mlx_ptr is None:
        return 1

    win_size = Size(1000, 1000)
    win_ptr = mlx.mlx_new_window(mlx_ptr, win_size.width,
                                 win_size.height, "My Window")
    if win_ptr is None:
        return 1

    rc = mlx.mlx_key_hook(win_ptr, on_key, None)
    if rc != 0:
        return 1
    rc = mlx.mlx_hook(win_ptr, 33, 0, lambda p: os._exit(0), None)
    if rc != 0:
        return 1

    canvas_ptr = mlx.mlx_new_image(mlx_ptr, win_size.width, win_size.height)
    canvas_data, _, canvas_sl, _ = mlx.mlx_get_data_addr(canvas_ptr)

    SCALE = 3

    spritesheet = SpriteSheet(mlx=mlx,
                              mlx_ptr=mlx_ptr,
                              file_path="data/spritesheet.xpm")

    spritesheet.define("a", Position(50, 50), Size(100, 50))
    sprite = spritesheet.get("a")
    sprite_size = spritesheet.get_size("a")
    sprite_data, _, sprite_sl, _ = mlx.mlx_get_data_addr(sprite)

    dest_x, dest_y = 200, 200
    bytes_per_pixel = 4

    for src_y in range(sprite_size.height):
        src_row_offset = src_y * sprite_sl

        for s_y in range(SCALE):
            target_y = dest_y + (src_y * SCALE) + s_y
            canvas_row_start = target_y * canvas_sl

            for src_x in range(sprite_size.width):
                src_pixel = src_row_offset + (src_x * bytes_per_pixel)

                for s_x in range(SCALE):
                    target_x = dest_x + (src_x * SCALE) + s_x
                    canvas_pixel = (canvas_row_start +
                                    (target_x * bytes_per_pixel))

                    canvas_data[canvas_pixel:canvas_pixel + 4] = sprite_data[
                        src_pixel:src_pixel + 4]

    mlx.mlx_put_image_to_window(mlx_ptr, win_ptr, canvas_ptr, 200, 200)

    mlx.mlx_loop(mlx_ptr)

    return 0


if __name__ == "__main__":
    main()
