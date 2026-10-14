
from typing import ClassVar, Any, Optional, Annotated
import sys
import json
import logging
from pydantic import (BaseModel, Field, ValidationError,
                      TypeAdapter, model_validator)


class LevelMetadata(BaseModel):
    """Metadata of a given level config."""
    width: int = Field(ge=3, le=70, default=10)
    height: int = Field(ge=3, le=70, default=10)
    pacgums: int = Field(ge=0, default=0)
    super_pacgums: int = Field(ge=0, default=4)
    timer: int = Field(ge=20, default=90)

    @staticmethod
    def validate_attr(name: str, data: Any) -> Any:
        field = LevelMetadata.model_fields[name]
        annotation = field.annotation or Any

        if field.metadata:
            adapter = TypeAdapter(Annotated[annotation, *field.metadata])
        else:
            adapter = TypeAdapter(annotation)

        try:
            adapter.validate_python(data, strict=True)
        except ValidationError as e:
            for error in e.errors():
                error_type = error.get("type")

                if any(kw in error_type for kw in
                        ["greater_than", "less_than", "range"]):
                    min_val = max_val = None

                    for meta in field.metadata:
                        if hasattr(meta, "ge"):
                            min_val = meta.ge
                        elif hasattr(meta, "gt"):
                            min_val = meta.gt + 1
                        if hasattr(meta, "le"):
                            max_val = meta.le
                        elif hasattr(meta, "lt"):
                            max_val = meta.lt + 1

                    if isinstance(data, (int, float)):
                        clamp = data
                        if min_val is not None:
                            clamp = max(clamp, min_val)
                        if max_val is not None:
                            clamp = min(clamp, max_val)

                        Config._log.warning(f"Field '{name}' is out of bounds."
                                            f" Clamping to {clamp}.")
                        return clamp

                fallback = field.get_default()
                Config._log.warning(f"Error parsing '{name}': "
                                    f"{error.get("type")}. Using "
                                    f"default {fallback}.")
                return fallback

        return data


class HighscoreMetadata(BaseModel):
    """Required keys of the highscore file."""
    name: str = ""
    score: int = Field(ge=0, default=-1)


class Config(BaseModel):
    """Deals with parsing values from the config.json.

    Parameters
    ----------
    highscore_filename : str
        Path of the highscore.json file.
    level_count : int
        Amount of levels to be played.
    points_per_pacgum : int
        Amount of points gained per pacgum eaten.
    points_per_super_pacgum : int
        Amount of points gained per super pacgum eaten.
    points_per_ghost : int
        Amount of points gained per ghost eaten.
    points_per_ghost : int
        Amount of points gained per ghost eaten.
    default_level : LevelMetadata
        Defaults of level configurations if none are set.

    Attributes
    ----------
    levels : list[LevelMetadata]
        Level configurations per stage.
    highscores : list[HighscoreMetadata]
        List of all highscores.

    Raises
    ------
    ValidationError
        When config.json cannot be read or has invalid syntax.

    """
    file_path: Optional[str] = None
    file_content: Optional[str] = None

    highscore_filename: Optional[str] = None
    level_count: int = Field(ge=10, le=200, default=10)
    lives: int = Field(ge=1, le=100, default=3)
    seed: int = Field(ge=0, default=67)

    points_per_pacgum: int = Field(ge=0, default=10)
    points_per_super_pacgum: int = Field(ge=0, default=50)
    points_per_ghost: int = Field(ge=0, default=200)

    default_level: LevelMetadata = Field(default_factory=LevelMetadata)
    levels: list[LevelMetadata] = Field(default_factory=list)
    highscores: list[HighscoreMetadata] = Field(default_factory=list)

    _log: ClassVar[logging.Logger] = logging.getLogger('PacMan')

    @model_validator(mode="before")
    @classmethod
    def parse_file_content(cls, data: Any) -> Any:
        """Attempts to parse data from file_content if set.

        Raises
        ------
        ValidationError
            When config.json cannot be read or has invalid syntax.

        """
        if not isinstance(data, dict) or not data.get("file_content"):
            return Config.abort_before_validator(data)

        raw_content: str = data["file_content"]
        content_str = Config._strip_config_comments(raw_content)

        try:
            content = json.loads(content_str)
        except json.JSONDecodeError as e:
            Config._log.warning(f"Error parsing config: {e}. "
                                "Fallback to default.")
            return Config.abort_before_validator(data)

        if not isinstance(content, dict):
            Config._log.warning("Error parsing config: Data must be a dict. "
                                "Fallback to default.")
            return Config.abort_before_validator(data)

        if "levels" not in data:
            data["levels"] = []
        if "highscores" not in data:
            data["highscores"] = []

        default_level_dict = {}
        levels_overwrite = []

        # Attempt to parse all recognized from config.json
        for k, v in content.items():
            match k:
                case "highscore_filename" | "level_count" | "lives" | "seed":
                    data[k] = Config.validate_attr(k, v)
                case "points":
                    if not isinstance(v, dict):
                        Config._log.warning("'points' does not "
                                            "match type dict.")
                        continue

                    for k2, v2 in v.items():
                        match k2:
                            case "pacgum":
                                data["points_per_pacgum"] =\
                                    Config.validate_attr(
                                        "points_per_pacgum", v2)
                            case "super_pacgum":
                                data["points_per_super_pacgum"] =\
                                    Config.validate_attr(
                                        "points_per_super_pacgum", v2)
                            case "ghost":
                                data["points_per_ghost"] =\
                                    Config.validate_attr(
                                        "points_per_ghost", v2)
                            case _:
                                Config._log.warning("Skipping unrecognized "
                                                    f"key: {k2} in {k}.")
                case ("width" | "height" | "pacgums" |
                        "super_pacgums" | "timer"):
                    # default_level_dict[k] = v
                    default_level_dict[k] = LevelMetadata.validate_attr(k, v)
                case "levels":
                    if not isinstance(v, list):
                        Config._log.warning("Unrecognized type for "
                                            f"'{k}': {type(v)}")
                        continue

                    for i, level in enumerate(v):
                        meta = LevelMetadata()

                        if not isinstance(level, dict):
                            Config._log.warning("Unrecognized type for "
                                                f"level {i+1}: {type(v)}")
                            levels_overwrite.append(meta)
                            continue

                        for k2, v2 in level.items():
                            if k2 not in LevelMetadata.model_fields:
                                Config._log.warning("Skipping unrecognized "
                                                    "key for level "
                                                    f"{i+1}: '{k2}'.")
                                continue
                            setattr(meta, k2,
                                    LevelMetadata.validate_attr(k2, v2))

                        levels_overwrite.append(meta)
                case _:
                    Config._log.warning(f"Skipping unrecognized key: {k}.")

        for attr in ("highscore_filename", "level_count",
                     "lives", "seed", "points_per_pacgum",
                     "points_per_super_pacgum", "points_per_ghost"):
            if attr not in data:
                fallback = Config.model_fields[attr].get_default()
                Config._log.warning(f"Key '{attr}' not found. "
                                    f"Using default {fallback}.")
                data[attr] = fallback

        for attr in ("width", "height", "pacgums",
                     "super_pacgums", "timer"):
            if attr not in default_level_dict:
                fallback = LevelMetadata.model_fields[attr].get_default()
                Config._log.warning(f"Key '{attr}' not found. "
                                    f"Using default {fallback}.")
                default_level_dict[attr] = fallback

        try:
            data["default_level"] = (LevelMetadata.model_validate
                                     (default_level_dict))
        except ValidationError as e:
            Config._log.warning(f"Improper default level data: {e}. "
                                "Picking default.")
            data["default_level"] = LevelMetadata()

        base_defaults = data["default_level"].model_dump()

        for i in range(data["level_count"]):
            if i < len(levels_overwrite):
                level_dict = levels_overwrite[i]
            else:
                level_dict = base_defaults.copy()

            try:
                validated = LevelMetadata.model_validate(level_dict)
                data["levels"].append(validated)
            except ValidationError as e:
                Config._log.warning(f"Error parsing level data: {e}. "
                                    "Picking default.")

        return data

    @classmethod
    def abort_before_validator(cls, data: Any) -> Any:
        data["levels"] = [LevelMetadata()] * 10
        return data

    @staticmethod
    def validate_attr(name: str, data: Any) -> Any:
        field = Config.model_fields[name]
        annotation = field.annotation or Any

        if field.metadata:
            adapter = TypeAdapter(Annotated[annotation, *field.metadata])
        else:
            adapter = TypeAdapter(annotation)

        try:
            adapter.validate_python(data, strict=True)
        except ValidationError as e:
            error_type = e.errors()[0].get("type")

            if any(kw in error_type for kw in
                    ["greater_than", "less_than", "range"]):
                min_val = max_val = None

                for meta in field.metadata:
                    if hasattr(meta, "ge"):
                        min_val = meta.ge
                    elif hasattr(meta, "gt"):
                        min_val = meta.gt + 1
                    if hasattr(meta, "le"):
                        max_val = meta.le
                    elif hasattr(meta, "lt"):
                        max_val = meta.lt + 1

                if isinstance(data, (int, float)):
                    clamp = data
                    if min_val is not None:
                        clamp = max(clamp, min_val)
                    if max_val is not None:
                        clamp = min(clamp, max_val)

                    Config._log.warning(f"Field '{name}' is out of bounds:"
                                        f" Clamping to {clamp}.")
                    return clamp

            fallback = field.get_default()
            Config._log.warning(f"Error parsing '{name}': "
                                f"{e.errors()[0].get("type")}. Using "
                                f"default {fallback}.")
            return fallback

        return data

    @classmethod
    def from_argv_file(cls) -> "Config":
        """Reads config.json from CLI argument or picks default."""

        if len(sys.argv) < 2:
            Config._log.warning("No CLI argument provided.")
            return Config.default_config()

        if len(sys.argv) > 2:
            Config._log.warning("Unexpected CLI argument provided.")
            return Config.default_config()

        path = sys.argv[1]
        try:
            with open(path, 'r', encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            Config._log.warning(f"Error reading config '{path}': {e}.")
            return Config.default_config()

        return cls(file_path=path, file_content=content)  # type: ignore

    @classmethod
    def default_config(cls) -> "Config":
        Config._log.warning("Choosing default configurations...")

        return cls(highscore_filename=None,
                   level_count=10,
                   points_per_pacgum=10,
                   points_per_super_pacgum=50,
                   points_per_ghost=200,
                   lives=3,
                   seed=67,
                   default_level=LevelMetadata(),
                   levels=[LevelMetadata()] * 10,
                   highscores=[])

    @staticmethod
    def _strip_config_comments(raw_content: str) -> str:
        """Removes all comments (#, //) from string.

        Parameters
        ----------
        raw_content : str
            Raw string to have its comments removed.

        Returns
        -------
        str
            String with comments removed.

        """
        lines: list[str] = raw_content.splitlines()
        # is_multiline = False

        for line_idx, line in enumerate(lines):
            comment_idx: Optional[int] = None

            # if is_multiline:
            #     close_idx = line.find("*/")
            #     if close_idx >= 0:
            #         lines[line_idx] = line[close_idx + 2:]
            #         is_multiline = False
            #     else:
            #         lines[line_idx] = ""
            #         continue

            tag_idx = line.find('#')
            if tag_idx >= 0:
                if comment_idx is None or tag_idx < comment_idx:
                    comment_idx = tag_idx

            slash_idx = line.find("//")
            if slash_idx >= 0:
                if comment_idx is None or slash_idx < comment_idx:
                    comment_idx = slash_idx

            # open_idx = line.find("/*")
            # if open_idx >= 0:
            #     if comment_idx is None or open_idx < comment_idx:
            #         comment_idx = open_idx
            #         is_multiline = True

            # if is_multiline:
            #     close_idx = line.find("*/")
            #     if close_idx >= 0:
            #         lines[line_idx] = line[close_idx + 2:]
            #         is_multiline = False
            #     else:
            #         lines[line_idx] = ""

            if comment_idx is not None:
                lines[line_idx] = line[:comment_idx]

        return ''.join(lines)
