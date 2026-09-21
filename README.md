_This project has been created as part of the 42 curriculum by ldreger, mimeyer._

# Description

https://projects.intra.42.fr/projects/pac-man
https://github.com/42school/mlx_CLXV
https://www.spriters-resource.com/arcade/pacman/

# Instructions

# Resources

https://github.com/SaraFreitas-dev/MinilibX-42-Pyhton-Documentation/blob/main/MLX_DOCUMENTATION.md

# Details

```mermaid
flowchart TD
    start([Start Program])
    start_screen[Start Screen]
    level[Playable Level]
    win_screen[Win Screen]
    lose_screen[Lose Screen]
    finish([End Program])

    start --> start_screen
    start_screen -->|Enter| level
    level -->|Loads new level| level
    level -->|All levels beaten| win_screen
    level -->|Ran out of lives| lose_screen
    level -->|Esc| finish
    win_screen -->|Enter| start_screen
    win_screen -->|Esc| finish
    lose_screen -->|Enter| start_screen
    lose_screen -->|Esc| finish
    start_screen -->|Esc| finish
```


## Configuration

## Highscore

## Maze Generation

## Implementation

## General Software Architecture

## Project Management
