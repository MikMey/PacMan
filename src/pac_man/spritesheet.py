from pydantic import BaseModel, Field, PrivateAttr, ConfigDict, ValidationError
from pydantic_core import InitErrorDetails
from typing import Optional, Any
import pygame
import pathlib


DEFAULT_FILE_PATH = "./data/spritesheet.bmp"


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
    reg_static : dict[str, list[pygame.Surface]]
        Dictionary of all moving assets. Empty on initialization.

    """
    sheet_surface: pygame.Surface
    scale_factor: float

    reg_static: dict[str, pygame.Surface] = Field(default_factory=dict)
    reg_anim: dict[str, list[pygame.Surface]] = Field(default_factory=dict)

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

        # Border Tiles
        self.cache_new("BORDER-TOP", 181, 19, 8)
        self.cache_new("BORDER-RIGHT", 172, 10, 8)
        self.cache_new("BORDER-BOTTOM", 181, 1, 8)
        self.cache_new("BORDER-LEFT", 190, 10, 8)
        self.cache_new("BORDER-TOP-RIGHT", 172, 28, 8)
        self.cache_new("BORDER-TOP-LEFT", 145, 28, 8)
        self.cache_new("BORDER-BOTTOM-RIGHT", 172, 55, 8)
        self.cache_new("BORDER-BOTTOM-LEFT", 145, 55, 8)

        # Border Tiles connectiong to Wall Tiles
        self.cache_new("BORDER-TOP-WALL-RIGHT", 154, 28, 8)
        self.cache_new("BORDER-TOP-WALL-LEFT", 163, 28, 8)
        self.cache_new("BORDER-RIGHT-WALL-TOP", 172, 46, 8)
        self.cache_new("BORDER-RIGHT-WALL-BOTTOM", 172, 37, 8)
        self.cache_new("BORDER-BOTTOM-WALL-RIGHT", 154, 28, 8, flip_y=True)
        self.cache_new("BORDER-BOTTOM-WALL-LEFT", 163, 28, 8, flip_y=True)
        self.cache_new("BORDER-LEFT-WALL-TOP", 145, 46, 8)
        self.cache_new("BORDER-LEFT-WALL-BOTTOM", 145, 37, 8)

        # Wall Tiles
        self.cache_new("WALL-TOP", 154, 19, 8)
        self.cache_new("WALL-RIGHT", 145, 10, 8)
        self.cache_new("WALL-BOTTOM", 154, 1, 8)
        self.cache_new("WALL-LEFT", 163, 10, 8)
        self.cache_new("WALL-TOP-RIGHT", 154, 46, 8)
        self.cache_new("WALL-TOP-LEFT", 163, 46, 8)
        self.cache_new("WALL-BOTTOM-RIGHT", 154, 37, 8)
        self.cache_new("WALL-BOTTOM-LEFT", 163, 37, 8)

        # Corner tiles (to round of ending walls)
        self.cache_new("CORNER-TOP-RIGHT", 145, 19, 8)
        self.cache_new("CORNER-TOP-LEFT", 163, 19, 8)
        self.cache_new("CORNER-BOTTOM-RIGHT", 145, 1, 8)
        self.cache_new("CORNER-BOTTOM-LEFT", 163, 1, 8)

        # Tile Items
        self.cache_new("PACGUM", 136, 10, 8)
        self.cache_new("SUPER-PACGUM", 136, 28, 8)

        # Fruits
        self.cache_new("FRUIT-0", 1, 117, 16)
        self.cache_new("FRUIT-1", 18, 117, 16)
        self.cache_new("FRUIT-2", 35, 117, 16)
        self.cache_new("FRUIT-3", 52, 117, 16)
        self.cache_new("FRUIT-4", 69, 117, 16)
        self.cache_new("FRUIT-5", 86, 117, 16)

        # Numbers, Letters and Special Characters
        text_scale = self._text_scale_factor
        self.cache_new("CHAR-0", 1, 19, 8, scale_factor=text_scale)
        self.cache_new("CHAR-1", 10, 19, 8, scale_factor=text_scale)
        self.cache_new("CHAR-2", 19, 19, 8, scale_factor=text_scale)
        self.cache_new("CHAR-3", 28, 19, 8, scale_factor=text_scale)
        self.cache_new("CHAR-4", 37, 19, 8, scale_factor=text_scale)
        self.cache_new("CHAR-5", 46, 19, 8, scale_factor=text_scale)
        self.cache_new("CHAR-6", 55, 19, 8, scale_factor=text_scale)
        self.cache_new("CHAR-7", 64, 19, 8, scale_factor=text_scale)
        self.cache_new("CHAR-8", 73, 19, 8, scale_factor=text_scale)
        self.cache_new("CHAR-9", 82, 19, 8, scale_factor=text_scale)

        self.cache_new("CHAR-A", 1, 28, 8, scale_factor=text_scale)
        self.cache_new("CHAR-B", 10, 28, 8, scale_factor=text_scale)
        self.cache_new("CHAR-C", 19, 28, 8, scale_factor=text_scale)
        self.cache_new("CHAR-D", 28, 28, 8, scale_factor=text_scale)
        self.cache_new("CHAR-E", 37, 28, 8, scale_factor=text_scale)
        self.cache_new("CHAR-F", 46, 28, 8, scale_factor=text_scale)
        self.cache_new("CHAR-G", 55, 28, 8, scale_factor=text_scale)
        self.cache_new("CHAR-H", 64, 28, 8, scale_factor=text_scale)
        self.cache_new("CHAR-I", 73, 28, 8, scale_factor=text_scale)
        self.cache_new("CHAR-J", 82, 28, 8, scale_factor=text_scale)
        self.cache_new("CHAR-K", 91, 28, 8, scale_factor=text_scale)
        self.cache_new("CHAR-L", 100, 28, 8, scale_factor=text_scale)
        self.cache_new("CHAR-M", 109, 28, 8, scale_factor=text_scale)
        self.cache_new("CHAR-N", 1, 37, 8, scale_factor=text_scale)
        self.cache_new("CHAR-O", 10, 37, 8, scale_factor=text_scale)
        self.cache_new("CHAR-P", 19, 37, 8, scale_factor=text_scale)
        self.cache_new("CHAR-Q", 28, 37, 8, scale_factor=text_scale)
        self.cache_new("CHAR-R", 37, 37, 8, scale_factor=text_scale)
        self.cache_new("CHAR-S", 46, 37, 8, scale_factor=text_scale)
        self.cache_new("CHAR-T", 55, 37, 8, scale_factor=text_scale)
        self.cache_new("CHAR-U", 64, 37, 8, scale_factor=text_scale)
        self.cache_new("CHAR-V", 73, 37, 8, scale_factor=text_scale)
        self.cache_new("CHAR-W", 82, 37, 8, scale_factor=text_scale)
        self.cache_new("CHAR-X", 91, 37, 8, scale_factor=text_scale)
        self.cache_new("CHAR-Y", 100, 37, 8, scale_factor=text_scale)
        self.cache_new("CHAR-Z", 109, 37, 8, scale_factor=text_scale)

        self.cache_new("CHAR-/", 91, 10, 8, scale_factor=text_scale)
        self.cache_new("CHAR--", 100, 10, 8, scale_factor=text_scale)
        self.cache_new("CHAR-.", 109, 10, 8, scale_factor=text_scale)
        self.cache_new("CHAR-\"", 91, 19, 8, scale_factor=text_scale)
        self.cache_new("CHAR-!", 109, 19, 8, scale_factor=text_scale)

        self.cache_new("CHAR-COPYRIGHT", 100, 19, 8, scale_factor=text_scale)

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
