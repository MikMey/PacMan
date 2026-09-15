
from pydantic import BaseModel, Field, ValidationError, model_validator
from pydantic_core import InitErrorDetails
from typing import Any, Optional
import sys
import json
# from rich import print


class LevelMetadata(BaseModel):

    width: int = Field(ge=1, default=10)
    height: int = Field(ge=1, default=10)
    lives: int = Field(ge=1, default=10)
    pacgums: int = Field(ge=1, default=10)
    super_pacgums: int = Field(ge=1, default=10)
    timer: int = Field(ge=1, default=10)


class HighscoreMetadata(BaseModel):

    name: str = Field(default="TEST")
    score: int = Field(ge=0, default=-1)


class Config(BaseModel):

    file_path: Optional[str] = None
    file_content: Optional[str] = None

    highscore_filename: str
    level_count: int = Field(ge=1)

    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: Optional[int] = None

    default_level: LevelMetadata = Field(default_factory=LevelMetadata)
    levels: list[LevelMetadata] = Field(default_factory=list)
    highscores: list[HighscoreMetadata] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def parse_file_content(cls, data: Any) -> Any:

        if not isinstance(data, dict) or not data.get("file_content"):
            return data

        errors: list[InitErrorDetails] = []

        raw_content: str = data["file_content"]
        content_str = Config._strip_config_comments(raw_content)

        try:
            content = json.loads(content_str)
        except json.JSONDecodeError as e:
            raise ValidationError.from_exception_data(
                title=cls.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=("file_content", "_strip_config_comments"),
                        input=content_str,
                        ctx={"error": e}
                    )
                ]
            )

        if "levels" not in data:
            data["levels"] = []
        if "highscores" not in data:
            data["highscores"] = []

        default_level_dict = (
            data["default_level"].model_dump() if "default_level" in data
            and isinstance(data["default_level"], LevelMetadata)else {}
        )
        levels_overwrite = []

        for k, v in content.items():
            match k:
                case "highscore_filename":
                    data[k] = v
                case "level_count":
                    if isinstance(v, int):
                        data[k] = v
                    else:
                        errors.append(InitErrorDetails(
                            type="value_error",
                            loc=("file_content", k),
                            input=v,
                            ctx={"error": ValueError(
                                "incorrect type. "
                                "Usage: Check README.md "
                                "for key information"
                            )}
                        ))
                case "points":
                    if isinstance(v, dict):
                        for k2, v2 in v.items():
                            match k2:
                                case "pacgum":
                                    data["points_per_pacgum"] = v2
                                case "super_pacgum":
                                    data["points_per_super_pacgum"] = v2
                                case "ghost":
                                    data["points_per_ghost"] = v2
                                case _:
                                    errors.append(InitErrorDetails(
                                        type="value_error",
                                        loc=("file_content", k, k2),
                                        input=v2,
                                        ctx={"error": ValueError(
                                            "unknown configuration key. "
                                            "Usage: Check README.md "
                                            "for allowed keys"
                                        )}
                                    ))
                case "seed":
                    data[k] = v
                case ("width" | "height" | "lives" | "pacgums" |
                      "super_pacgums" | "timer"):
                    default_level_dict[k] = v
                case "levels":
                    if isinstance(v, list):
                        levels_overwrite = v
                case _:
                    errors.append(InitErrorDetails(
                        type="value_error",
                        loc=("file_content", k),
                        input=v,
                        ctx={"error": ValueError(
                            "unknown configuration key. "
                            "Usage: Check README.md for allowed keys"
                        )}
                    ))

        try:
            data["default_level"] = (LevelMetadata.model_validate
                                     (default_level_dict))
        except ValidationError as e:
            for error in e.errors():
                field_name = error["loc"][0] if error["loc"] else "unknown"
                errors.append(InitErrorDetails(
                    type="value_error",
                    loc=("file_content", str(field_name)),
                    input=error.get("input"),
                    ctx={"error": ValueError(error["msg"])}
                ))
            data["default_level"] = LevelMetadata()

        if "level_count" in data and isinstance(data["level_count"], int):
            base_defaults = data["default_level"].model_dump()

            for i in range(data["level_count"]):
                level_dict = base_defaults.copy()

                if i < len(levels_overwrite):
                    for k, v in levels_overwrite[i].items():
                        if k in LevelMetadata.model_fields:
                            level_dict[k] = v
                        else:
                            errors.append(InitErrorDetails(
                                type="value_error",
                                loc=("file_content", f"level_{i}", k),
                                input=v,
                                ctx={"error": ValueError(
                                    "unknown configuration key. "
                                    "Usage: Check README.md "
                                    "for allowed keys"
                                )}
                            ))

                try:
                    validated = LevelMetadata.model_validate(level_dict)
                    data["levels"].append(validated)
                except ValidationError as e:
                    for error in e.errors():
                        field_name = (error["loc"][0] if error["loc"]
                                      else "unknown")

                        errors.append(InitErrorDetails(
                            type="value_error",
                            loc=("file_content", f"level_{i}",
                                 str(field_name)),
                            input=error.get("input"),
                            ctx={"error": ValueError(error["msg"])}
                        ))

        if errors:
            raise ValidationError.from_exception_data(
                title=cls.__name__,
                line_errors=errors
            )

        return data

    @model_validator(mode="after")
    def validate_config(self) -> "Config":

        try:
            with open(self.highscore_filename, 'r', encoding="utf-8") as f:
                content = f.read()
                if not content:
                    scores = []
                else:
                    scores = json.loads(content)
        except (OSError, json.JSONDecodeError):
            return self

        if type(scores) is dict:
            scores = [scores]

        for score_metadata in scores:
            name = None
            score = None

            for k, v in score_metadata.items():
                match k:
                    case "name":
                        name = v
                    case "score":
                        score = v
                    case _:
                        continue

            try:
                if isinstance(name, str) and isinstance(score, int):
                    self.highscores.append(
                        HighscoreMetadata(name=name, score=score)
                    )
            except ValidationError:
                pass

        return self

    @classmethod
    def from_argv_file(cls) -> "Config":
        if len(sys.argv) < 2:
            raise ValidationError.from_exception_data(
                title=cls.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=("sys.argv",),
                        input=sys.argv,
                        ctx={"error": ValueError(
                            "missing CLI argument. "
                            "Usage: uv run python -m src <path_to_config_file>"
                        )}
                    )
                ]
            )
        if len(sys.argv) > 2:
            raise ValidationError.from_exception_data(
                title=cls.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=("sys.argv",),
                        input=sys.argv,
                        ctx={"error": ValueError(
                            "unexpected CLI argument. "
                            "Usage: uv run python -m src <path_to_config_file>"
                        )}
                    )
                ]
            )

        path = sys.argv[1]
        try:
            with open(path, 'r', encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            raise ValidationError.from_exception_data(
                title=cls.__name__,
                line_errors=[
                    InitErrorDetails(
                        type="value_error",
                        loc=("sys.argv", sys.argv[1]),
                        input=sys.argv[1],
                        ctx={"error": e}
                    )
                ]
            )

        return cls(file_path=path, file_content=content)  # type: ignore

    @staticmethod
    def _strip_config_comments(raw_content: str):

        lines: list[str] = raw_content.splitlines()
        is_multiline = False

        for line_idx, line in enumerate(lines):
            comment_idx: Optional[int] = None

            if is_multiline:
                close_idx = line.find("*/")
                if close_idx >= 0:
                    lines[line_idx] = line[close_idx + 2:]
                    is_multiline = False
                else:
                    lines[line_idx] = ""
                    continue

            tag_idx = line.find('#')
            if tag_idx >= 0:
                if comment_idx is None or tag_idx < comment_idx:
                    comment_idx = tag_idx

            slash_idx = line.find("//")
            if slash_idx >= 0:
                if comment_idx is None or slash_idx < comment_idx:
                    comment_idx = slash_idx

            open_idx = line.find("/*")
            if open_idx >= 0:
                if comment_idx is None or open_idx < comment_idx:
                    comment_idx = open_idx
                    is_multiline = True

            if is_multiline:
                close_idx = line.find("*/")
                if close_idx >= 0:
                    lines[line_idx] = line[close_idx + 2:]
                    is_multiline = False
                else:
                    lines[line_idx] = ""

            if comment_idx is not None:
                lines[line_idx] = line[:comment_idx]

        return ''.join(lines)
