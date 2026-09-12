from .structures import Position, Size

from mlx import Mlx
from pydantic import (BaseModel, Field, PrivateAttr, ConfigDict,
                      model_validator, ValidationError)


class Sprite(BaseModel):

    ptr: int
    size: Size


class SpriteSheet(BaseModel):

    mlx: Mlx
    mlx_ptr: int
    file_path: str

    sprites: dict[str, Sprite] = Field(default_factory=dict)

    _ptr: int = PrivateAttr()
    _size: Size = PrivateAttr()
    _data: memoryview[int] = PrivateAttr()
    _size_line: int = PrivateAttr()

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="after")
    def validate_sheet(self) -> "SpriteSheet":

        try:
            with open(self.file_path, 'r', encoding="utf-8"):
                tmp_ptr, tmp_w, tmp_h = self.mlx.mlx_xpm_file_to_image(
                    self.mlx_ptr,
                    self.file_path
                )

                if tmp_ptr is None:
                    raise MemoryError("Sprite Sheet pointer is None")
                self._ptr = tmp_ptr
                self._size = Size(width=tmp_w, height=tmp_h)

                tmp_ptr, _, tmp_w, _ = self.mlx.mlx_get_data_addr(self._ptr)

                if tmp_ptr is None:
                    raise MemoryError("Sprite Sheet data pointer is None")
                self._data = tmp_ptr
                self._size_line = tmp_w

        except (OSError, MemoryError) as e:
            raise ValidationError.from_exception_data(
                title="reading sprite sheet failed",
                line_errors=[
                    {
                        "type": "value_error",
                        "loc": ("SpriteSheet",),
                        "input": self.file_path,
                        "ctx": {"error": str(e)}
                    }
                ]
            )

        return self

    def define(self, name: str, src_pos: Position, src_size: Size) -> Sprite:

        tile_ptr = self.mlx.mlx_new_image(self.mlx_ptr, *src_size)
        if tile_ptr is None:
            raise MemoryError("New Sprite could not be defined")

        tile_data, _, tile_sl, _ = self.mlx.mlx_get_data_addr(tile_ptr)
        if tile_data is None:
            raise MemoryError("New Sprite data could not be defined")

        bytes_per_pixel = 4
        row_size_bytes = src_size.width * bytes_per_pixel

        for y in range(src_size.height):
            src_start = (((src_pos.y + y) * self._size_line) +
                         (src_pos.x * bytes_per_pixel))
            src_end = src_start + row_size_bytes

            dest_start = y * tile_sl
            dest_end = dest_start + row_size_bytes

            tile_data[dest_start:dest_end] = self._data[src_start:src_end]

        self.sprites[name] = Sprite(ptr=tile_ptr, size=src_size)

        return self.sprites[name]

    def get(self, name: str) -> Sprite:
        return self.sprites[name]
