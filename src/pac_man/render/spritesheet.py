import pathlib
from typing import Optional, Any

from pydantic import BaseModel, Field, PrivateAttr, ConfigDict, ValidationError
from pydantic_core import InitErrorDetails
import pygame


DEFAULT_FILE_PATH = "./data/spritesheet.bmp"
SHEET_OFFSET_X = 200
SHEET_OFFSET_Y = 186


class SpriteRect(BaseModel):
    """Defines a bounding box of a sprite in a spitesheet.

    Parameters
    ----------
    x : int
        Horizontal top-left pixel position of sprite.
    y : int
        Vertical top-left pixel position of sprite.
    w : int
        Horizontal pixel height of sprite.
    h : int
        Vertical pixel height of sprite.

    """
    x: int = Field(ge=0)
    y: int = Field(ge=0)
    w: int = Field(gt=0)
    h: int = Field(gt=0)


class AssetSource(BaseModel):
    """Defines Asset type and resources. Can be static or animated.

    Parameters
    ----------
    name : str
        Identifiable Name for an asset. Will be the key in :obj:`AssetCache`.
    is_animated : bool
        True if sprite is animated, False if static. Defaults to False.
    frames : list[:obj:`SpriteRect`]
        List of all sprite frame locations and sizes.
    scale : tuple[float, float], optional
        Rescaling factor when drawing. Defaults to None.

    """
    name: str
    is_animated: bool = False
    frames: list[SpriteRect]
    scale: Optional[tuple[float, float]] = None
    flip_x: bool = False
    flip_y: bool = False

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SpriteSheetCache(BaseModel):
    """Caches AssetSource under their name.
    This does save scale but not in-window location.

    Parameters
    ----------
    sheet_surface : pygame.Surface
        The surface instance of the entire sprite sheet.

    Attributes
    ----------
    reg_static : dict[str, pygame.Surface]
        Dictionary of all non-moving assets. Empty on initialization.
    reg_anim : dict[str, list[pygame.Surface]]
        Dictionary of all moving assets. Empty on initialization.

    """
    sheet_surface: pygame.Surface
    scale_factor: float

    reg_static: dict[str, pygame.Surface] = Field(default_factory=dict)
    reg_anim: dict[str, list[pygame.Surface]] = Field(default_factory=dict)

    text_color_offset: int = 9
    tile_color_offset: int = 8

    _text_scale_factor: float = PrivateAttr()

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes default cache."""
        super().__init__(*args, **kwargs)

        self._text_scale_factor = self.scale_factor * 0.8

        self._init_default_cache()

    @classmethod
    def from_default_file_path(cls, scale_factor: float) -> "SpriteSheetCache":
        """Creates class from default spritesheet (DEFAULT_FILE_PATH).

        Parameters
        ----------
        scale_factor : float
            global scaling factor to be baked into cache.

        Raises
        ------
        ValidationError
            When default spritesheet cannot be opened is is invalid.

        """
        git_root = pathlib.Path.cwd()
        absolute_sheet_path = (git_root / DEFAULT_FILE_PATH).resolve()

        try:
            raw_sheet_image = pygame.image.load(
                str(absolute_sheet_path)
            ).convert_alpha()
        except (OSError, pygame.error) as e:
            raise ValidationError.from_exception_data(
                title=cls.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=("DEFAULT_FILE_PATH",),
                        input=DEFAULT_FILE_PATH,
                        ctx={"error": str(e)}
                    )
                ]
            )

        return cls(sheet_surface=raw_sheet_image, scale_factor=scale_factor)

    def _init_default_cache(self) -> None:
        """Caches known assets when initializing."""

        # === STATIC TILES === #

        # Tiles (Walls and Borders)
        self.bake_tile_offset(self.tile_color_offset)

        # Tile Items
        self.cache_new("PACGUM", 136, 10, 8)
        self.cache_new("SUPER-PACGUM", 136, 28, 8)

        # Fruits
        self.cache_new("FRUIT-0", 401, 489, 16)  # Cherry
        self.cache_new("FRUIT-1", 618, 489, 16)  # Strawberry
        self.cache_new("FRUIT-2", 835, 489, 16)  # Orange
        self.cache_new("FRUIT-3", 452, 489, 16)  # Apple
        self.cache_new("FRUIT-4", 69, 675, 16)  # Melon
        self.cache_new("FRUIT-5", 286, 675, 16)  # Starship
        self.cache_new("FRUIT-6", 503, 675, 16)  # Bell
        self.cache_new("FRUIT-7", 520, 675, 16)  # Key

        # Numbers, Letters and Special Characters
        self.bake_text_offset(self.text_color_offset)

        # === ANIMATED TILES === #

        # Pacman Sprites
        self.cache_new_anim(
            "PACMAN-RIGHT",
            [(103, 168), (103, 151), (103, 134), (103, 151)],
            size=16
        )
        self.cache_new_anim(
            "PACMAN-LEFT",
            [(103, 168), (103, 151), (103, 134), (103, 151)],
            size=16, flip_x=True
        )
        self.cache_new_anim(
            "PACMAN-BOTTOM",
            [(103, 168), (120, 151), (120, 134), (120, 151)],
            size=16
        )
        self.cache_new_anim(
            "PACMAN-TOP",
            [(103, 168), (120, 151), (120, 134), (120, 151)],
            size=16, flip_y=True
        )
        self.cache_new_anim(
            "PACMAN-DEATH",
            [(1, 134), (18, 134), (35, 134), (52, 134), (69, 134), (86, 134),
             (1, 151), (18, 151), (35, 151), (52, 151), (69, 151), (86, 151)],
            size=16
        )

        # Shadow / Blinky (Red)
        self.cache_new_anim("GHOST-1-RIGHT", [(1, 83), (18, 83)], size=16)
        self.cache_new_anim("GHOST-1-LEFT", [(69, 83), (86, 83)], size=16)
        self.cache_new_anim("GHOST-1-BOTTOM", [(35, 83), (52, 83)], size=16)
        self.cache_new_anim("GHOST-1-TOP", [(103, 83), (120, 83)], size=16)
        self.cache_new_anim("GHOST-1-SCARED",
                            [(1, 168), (18, 168)], size=16)

        # Speedy / Pinky (Pink)
        self.cache_new_anim("GHOST-2-RIGHT", [(201, 83), (218, 83)], size=16)
        self.cache_new_anim("GHOST-2-LEFT", [(269, 83), (286, 83)], size=16)
        self.cache_new_anim("GHOST-2-BOTTOM", [(235, 83), (252, 83)], size=16)
        self.cache_new_anim("GHOST-2-TOP", [(303, 83), (320, 83)], size=16)
        self.cache_new_anim("GHOST-2-SCARED",
                            [(201, 168), (218, 168)], size=16)

        # Bashful / Inky (Cyan)
        self.cache_new_anim("GHOST-3-RIGHT", [(401, 83), (418, 83)], size=16)
        self.cache_new_anim("GHOST-3-LEFT", [(469, 83), (486, 83)], size=16)
        self.cache_new_anim("GHOST-3-BOTTOM", [(435, 83), (452, 83)], size=16)
        self.cache_new_anim("GHOST-3-TOP", [(503, 83), (520, 83)], size=16)
        self.cache_new_anim("GHOST-3-SCARED",
                            [(401, 168), (418, 168)], size=16)

        # Pokey / Clyde (Orange)
        self.cache_new_anim("GHOST-4-RIGHT", [(601, 83), (618, 83)], size=16)
        self.cache_new_anim("GHOST-4-LEFT", [(669, 83), (686, 83)], size=16)
        self.cache_new_anim("GHOST-4-BOTTOM", [(635, 83), (652, 83)], size=16)
        self.cache_new_anim("GHOST-4-TOP", [(703, 83), (720, 83)], size=16)
        self.cache_new_anim("GHOST-4-SCARED",
                            [(601, 168), (618, 168)], size=16)

        # Dead Ghost (Invisisble)
        self.cache_new_anim("GHOST-DEAD-RIGHT", [(201, 269)], size=16)
        self.cache_new_anim("GHOST-DEAD-LEFT", [(269, 269)], size=16)
        self.cache_new_anim("GHOST-DEAD-BOTTOM", [(235, 269)], size=16)
        self.cache_new_anim("GHOST-DEAD-TOP", [(303, 269)], size=16)

    def bake_tile_offset(self, offset: int) -> None:

        def cache_tile(name: str, x: int, y: int) -> None:
            self.cache_new(
                name,
                x + SHEET_OFFSET_X * (offset % 5),
                y + SHEET_OFFSET_Y * (offset // 5),
                8
            )

        cache_tile("BORDER-TOP", 181, 19)
        cache_tile("BORDER-RIGHT", 172, 10)
        cache_tile("BORDER-BOTTOM", 181, 1)
        cache_tile("BORDER-LEFT", 190, 10)
        cache_tile("BORDER-TOP-RIGHT", 172, 28)
        cache_tile("BORDER-TOP-LEFT", 145, 28)
        cache_tile("BORDER-BOTTOM-RIGHT", 172, 55)
        cache_tile("BORDER-BOTTOM-LEFT", 145, 55)

        cache_tile("BORDER-TOP-WALL-RIGHT", 154, 28)
        cache_tile("BORDER-TOP-WALL-LEFT", 163, 28)
        cache_tile("BORDER-RIGHT-WALL-TOP", 172, 46)
        cache_tile("BORDER-RIGHT-WALL-BOTTOM", 172, 37)
        self.cache_new(
            "BORDER-BOTTOM-WALL-RIGHT",
            154 + SHEET_OFFSET_X * (offset % 5),
            28 + SHEET_OFFSET_Y * (offset // 5),
            8,
            flip_y=True
        )
        self.cache_new(
            "BORDER-BOTTOM-WALL-LEFT",
            163 + SHEET_OFFSET_X * (offset % 5),
            28 + SHEET_OFFSET_Y * (offset // 5),
            8,
            flip_y=True
        )
        cache_tile("BORDER-LEFT-WALL-TOP", 145, 46)
        cache_tile("BORDER-LEFT-WALL-BOTTOM", 145, 37)

        cache_tile("WALL-TOP", 154, 19)
        cache_tile("WALL-RIGHT", 145, 10)
        cache_tile("WALL-BOTTOM", 154, 1)
        cache_tile("WALL-LEFT", 163, 10)
        cache_tile("WALL-TOP-RIGHT", 154, 46)
        cache_tile("WALL-TOP-LEFT", 163, 46)
        cache_tile("WALL-BOTTOM-RIGHT", 154, 37)
        cache_tile("WALL-BOTTOM-LEFT", 163, 37)

        cache_tile("CORNER-TOP-RIGHT", 145, 19)
        cache_tile("CORNER-TOP-LEFT", 163, 19)
        cache_tile("CORNER-BOTTOM-RIGHT", 145, 1)
        cache_tile("CORNER-BOTTOM-LEFT", 163, 1)

    def bake_text_offset(self, offset: int) -> None:
        """Pick a global text and number color.

        Parameters
        ----------
        offset : int
            Offset in the tile sheet (0-19).

        """
        text_scale = self._text_scale_factor

        def cache_text(name: str, x: int, y: int) -> None:
            """Helper to cache the text with correct offset"""
            self.cache_new(
                name,
                x + SHEET_OFFSET_X * (offset % 5),
                y + SHEET_OFFSET_Y * (offset // 5),
                8,
                scale_factor=text_scale
            )

        cache_text("CHAR-0", 1, 19)
        cache_text("CHAR-1", 10, 19)
        cache_text("CHAR-2", 19, 19)
        cache_text("CHAR-3", 28, 19)
        cache_text("CHAR-4", 37, 19)
        cache_text("CHAR-5", 46, 19)
        cache_text("CHAR-6", 55, 19)
        cache_text("CHAR-7", 64, 19)
        cache_text("CHAR-8", 73, 19)
        cache_text("CHAR-9", 82, 19)

        cache_text("CHAR-A", 1, 28)
        cache_text("CHAR-B", 10, 28)
        cache_text("CHAR-C", 19, 28)
        cache_text("CHAR-D", 28, 28)
        cache_text("CHAR-E", 37, 28)
        cache_text("CHAR-F", 46, 28)
        cache_text("CHAR-G", 55, 28)
        cache_text("CHAR-H", 64, 28)
        cache_text("CHAR-I", 73, 28)
        cache_text("CHAR-J", 82, 28)
        cache_text("CHAR-K", 91, 28)
        cache_text("CHAR-L", 100, 28)
        cache_text("CHAR-M", 109, 28)
        cache_text("CHAR-N", 1, 37)
        cache_text("CHAR-O", 10, 37)
        cache_text("CHAR-P", 19, 37)
        cache_text("CHAR-Q", 37, 37)
        cache_text("CHAR-R", 37, 37)
        cache_text("CHAR-S", 46, 37)
        cache_text("CHAR-T", 55, 37)
        cache_text("CHAR-U", 64, 37)
        cache_text("CHAR-V", 73, 37)
        cache_text("CHAR-W", 82, 37)
        cache_text("CHAR-X", 91, 37)
        cache_text("CHAR-Y", 100, 37)
        cache_text("CHAR-Z", 109, 37)

        cache_text("CHAR-/", 91, 10)
        cache_text("CHAR--", 100, 10)
        cache_text("CHAR-.", 109, 10)
        cache_text("CHAR-\"", 91, 19)
        cache_text("CHAR-!", 109, 19)

        cache_text("CHAR-COPYRIGHT", 100, 19)

    def cache_new(self, name: str, x: int, y: int, size: int,
                  flip_x: bool = False, flip_y: bool = False,
                  scale: float = 1.0,
                  scale_factor: Optional[float] = None) -> None:
        """Cache a non-moving sprite asset under a name.

        Parameters
        ----------
        name : str
            Name of the asset.
        x : int
            Horizontal top-left pixel position of sprite.
        y : int
            Vertical top-left pixel position of sprite.
        size : int
            Width and height of the sprite.
        flip_x : bool, optional
            True if it should be flipped horizontally. Default to False.
        flip_y : bool, optional
            True if it should be flipped vertically. Default to False.
        scale : float, optional
            Scale to be added on top of scale_factor. Default to 1.0.

        """
        self.cache_asset(AssetSource(
            name=name,
            frames=[SpriteRect(x=x, y=y, w=size, h=size)],
            flip_x=flip_x,
            flip_y=flip_y,
            scale=(scale * (scale_factor if scale_factor is not
                            None else self.scale_factor),
                   scale * (scale_factor if scale_factor is not
                            None else self.scale_factor))
        ))

    def cache_new_anim(self, name: str,
                       pos: list[tuple[int, int]], size: int,
                       flip_x: bool = False, flip_y: bool = False,
                       scale: float = 1.0) -> None:
        """Cache a moving sprite asset under a name.

        Parameters
        ----------
        name : str
            Name of the asset.
        pos : list[tuple[int, int]]
            List of (x,y) coordinates of all frames.
        size : int
            Width and height of all sprites.
        flip_x : bool, optional
            True if it should be flipped horizontally. Default to False.
        flip_y : bool, optional
            True if it should be flipped vertically. Default to False.
        scale : float, optional
            Scale to be added on top of scale_factor. Default to 1.0.

        """
        frames = []
        for p in pos:
            frames.append(SpriteRect(x=p[0], y=p[1], w=size, h=size))

        self.cache_asset(AssetSource(
            name=name,
            frames=frames,
            is_animated=True,
            flip_x=flip_x,
            flip_y=flip_y,
            scale=(self.scale_factor * scale,
                   self.scale_factor * scale)
        ))

    def cache_asset(self, asset_source: AssetSource) -> None:
        """Creates Surface from :obj:`AssetSource` and saves it in reg.

        Added to `reg_static` if not animated or `reg_anim` is animated.

        Parameters
        ----------
        asset_source : :obj:`AssetSource`
            AssetSource to be added as a Surface to registry.

        """
        surfaces = []

        for frame in asset_source.frames:
            rect = pygame.Rect(frame.x, frame.y, frame.w, frame.h)
            sprite_surface = self.sheet_surface.subsurface(rect)

            if asset_source.scale:
                new_size = (int(frame.w * asset_source.scale[0]),
                            int(frame.h * asset_source.scale[1]))
                sprite_surface = pygame.transform.scale(sprite_surface,
                                                        new_size)

            if asset_source.flip_x or asset_source.flip_y:
                sprite_surface = pygame.transform.flip(
                    sprite_surface,
                    asset_source.flip_x,
                    asset_source.flip_y
                )

            surfaces.append(sprite_surface)

        if asset_source.is_animated:
            self.reg_anim[asset_source.name] = surfaces
        else:
            self.reg_static[asset_source.name] = surfaces[0]

    def get_static(self, name: str) -> pygame.Surface:
        """Gets Surface of non-animated asset."""
        return self.reg_static[name]

    def get_anim(self, name: str) -> list[pygame.Surface]:
        """Gets Surface of animated asset."""
        return self.reg_anim[name]