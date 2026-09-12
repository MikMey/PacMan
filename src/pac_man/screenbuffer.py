from .structures import Position, Size
from .spritesheet import SpriteSheet

from mlx import Mlx
from pydantic import BaseModel, PrivateAttr, ConfigDict, model_validator


class ScreenBuffer(BaseModel):

    mlx: Mlx
    mlx_ptr: int
    win_ptr: int
    spritesheet: SpriteSheet

    size: Size

    _ptr: int = PrivateAttr()
    _data: memoryview[int] = PrivateAttr()
    _size_line: int = PrivateAttr()

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def validate_sheet(self) -> "ScreenBuffer":

        tmp_ptr = self.mlx.mlx_new_image(self.mlx_ptr, *self.size)
        if tmp_ptr is None:
            raise MemoryError("Screen Buffer pointer is None")
        self._ptr = tmp_ptr

        tmp_data, _, tmp_sl, _ = self.mlx.mlx_get_data_addr(self._ptr)
        if tmp_data is None:
            raise MemoryError("Screen Buffer data pointer is None")
        self._data = tmp_data
        self._size_line = tmp_sl

        return self

    def clear(self) -> None:

        canvas_bytes = self._data.cast("B")
        black_pixel_bytes = b'\x00\x00\x00\xFF'
        total_pixels = len(canvas_bytes) // 4
        canvas_bytes[:] = black_pixel_bytes * total_pixels

    def draw(self, name: str, target_pos: Position, scale: int) -> None:

        sprite = self.spritesheet.get(name)
        sprite_data, _, sprite_sl, _ = self.mlx.mlx_get_data_addr(sprite.ptr)
        bytes_per_pixel = 4

        for src_y in range(sprite.size.height):
            src_row_offset = src_y * sprite_sl

            for s_y in range(scale):
                target_y = target_pos.y + (src_y * scale) + s_y

                if target_y < 0 or target_y >= self.size.height:
                    continue
                canvas_row_start = target_y * self._size_line

                for src_x in range(sprite.size.width):
                    src_pixel = src_row_offset + (src_x * bytes_per_pixel)

                    for s_x in range(scale):
                        target_x = target_pos.x + (src_x * scale) + s_x

                        if target_x < 0 or target_x >= self.size.width:
                            continue

                        canvas_pixel = (canvas_row_start +
                                        (target_x * bytes_per_pixel))

                        self._data[canvas_pixel:canvas_pixel + 4] = \
                            sprite_data[src_pixel:src_pixel + 4]

    def render(self) -> None:
        self.mlx.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr,
                                         self._ptr, 0, 0)
