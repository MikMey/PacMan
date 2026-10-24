# Desired Workload Split

| ldreger | mimeyer |
| - | - |
| Sprite rendering | FSM architecture |
| Configuration file parsing | Highscore file reading and writing |
| MazeGenerator implementation | Main run loop implementation |
| General Character Movement Logic | Main Menu and Guide |
| HUD implementation and text rendering | Ghost AI with Super Pacgum logic |
| Pallet Generation | Logging |

# Git Log Observed Workload Split

#### ldreger

- Configuration logic and configuration safety.

- Level, player, and game-loading foundations.

- Score and life HUD.

- Maze generation, collectibles, and level-cycle features.

- Build rules, entry-point compliance, and README updates.

- Release-facing pause, victory, defeat, and publication changes.

#### mimeyer

- Initial project structure, tooling, dependencies, and model design.

- FSM and game-loop implementation.

- Character and ghost architecture, movement, and pathfinding.

- Collision logic, gameplay states, menus, and level progression.

- Timer, collectibles, guide, high-score flow, and gameplay integration.

- Refactoring, linting, debugging, and stability improvements.