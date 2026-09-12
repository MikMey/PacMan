from .structures import Position, Size
from .screenbuffer import ScreenBuffer
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

    spritesheet = SpriteSheet(mlx=mlx, mlx_ptr=mlx_ptr,
                              file_path="data/spritesheet.xpm")

    screen = ScreenBuffer(mlx=mlx, mlx_ptr=mlx_ptr, win_ptr=win_ptr,
                          size=win_size, spritesheet=spritesheet)

    spritesheet.define("0", Position(1, 1), Size(8, 8))
    spritesheet.define("1", Position(10, 1), Size(8, 8))

    screen.draw("0", Position(100, 100), 4)
    screen.draw("1", Position(50, 100), 4)

    screen.render()

    mlx.mlx_loop(mlx_ptr)

    return 0


if __name__ == "__main__":
    main()
