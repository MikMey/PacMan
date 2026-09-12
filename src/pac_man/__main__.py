from mlx import Mlx
import os


def on_key(key, param):
    if key == 65307:  # ESC
        os._exit(0)


def main() -> int:
    mlx = Mlx()
    mlx_ptr = mlx.mlx_init()
    win_ptr = mlx.mlx_new_window(mlx_ptr, 800, 800, "My Window")

    mlx.mlx_key_hook(win_ptr, on_key, None)
    mlx.mlx_hook(win_ptr, 33, 0, lambda p: os._exit(0), None)  # close button

    mlx.mlx_loop(mlx_ptr)

    return 0


if __name__ == "__main__":
    main()
