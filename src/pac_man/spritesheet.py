from pydantic import BaseModel, Field, ConfigDict, ValidationError
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
        Vertical top-left pixel position of sprite.
    y : int
        Horizontal top-left pixel position of sprite.
    w : int
        Vertical pixel height of sprite.
    h : int
        Horizontal pixel height of sprite.

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
    scale_factor: float = Field(ge=1)

    reg_static: dict[str, pygame.Surface] = Field(default_factory=dict)
    reg_anim: dict[str, list[pygame.Surface]] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes default cache."""
        super().__init__(*args, **kwargs)

        self._init_cache()

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

    def _init_cache(self) -> None:
        """Caches known assets when initializing."""
        self.cache_asset(AssetSource(
            name="B-TL",
            frames=[SpriteRect(x=745, y=187, w=8, h=8)],
            scale=(self.scale_factor, self.scale_factor)
        ))
        self.cache_asset(AssetSource(
            name="B-T",
            frames=[SpriteRect(x=745, y=187, w=8, h=8)],
            scale=(self.scale_factor, self.scale_factor)
        ))
        self.cache_asset(AssetSource(
            name="B-TR",
            frames=[SpriteRect(x=745, y=187, w=8, h=8)],
            scale=(self.scale_factor, self.scale_factor)
        ))
        self.cache_asset(AssetSource(
            name="B-L",
            frames=[SpriteRect(x=745, y=187, w=8, h=8)],
            scale=(self.scale_factor, self.scale_factor)
        ))
        self.cache_asset(AssetSource(
            name="VOID",
            frames=[SpriteRect(x=745, y=187, w=8, h=8)],
            scale=(self.scale_factor, self.scale_factor)
        ))
        self.cache_asset(AssetSource(
            name="B-R",
            frames=[SpriteRect(x=745, y=187, w=8, h=8)],
            scale=(self.scale_factor, self.scale_factor)
        ))
        self.cache_asset(AssetSource(
            name="B-BL",
            frames=[SpriteRect(x=745, y=187, w=8, h=8)],
            scale=(self.scale_factor, self.scale_factor)
        ))
        self.cache_asset(AssetSource(
            name="B-B",
            frames=[SpriteRect(x=745, y=187, w=8, h=8)],
            scale=(self.scale_factor, self.scale_factor)
        ))
        self.cache_asset(AssetSource(
            name="B-BR",
            frames=[SpriteRect(x=745, y=187, w=8, h=8)],
            scale=(self.scale_factor, self.scale_factor)
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
