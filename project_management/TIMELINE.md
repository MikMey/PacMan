# Phase 1 — Project initiation and technical foundation
### Sep 11 — Friday

Repository initialization and development tooling

The project begins with two initial-commit records and the establishment of a structured codebase.

- Initial repository commit.

- Structured source files and subject/specification file added.

- Makefile established.

- mypy and flake8 introduced for type checking and linting.

- Files reorganized into a more maintainable project structure.

### Sep 12 — Saturday

Rendering and maze-generation dependencies

The project begins developing the graphical foundations required to display the game world.

- MiniLibX and maze-generator dependencies added.

- Sprite sheet and basic rendering implemented.

- Sprite scaling for different assets introduced.

- Multi-tile tile support added.

- Maze-generation branch integrated through pull request #1.

### Sep 14 — Monday

Object-oriented model foundation

The project structure is expanded to support reusable game models and configuration.

- Models directory created for object-oriented types.

- Initial config.json structure introduced.

- Dependencies and utility package organized.

- Source directories refactored to fit the project structure.

- Dedicated model-development branches initialized.

### Sep 15 — Tuesday

Maze model, tile classes, and game-loop architecture

The core architecture is established, combining maze generation, character models, and state-based execution.

- Simple map and maze-generator classes implemented with tests.

- Tile classes instantiated and dependencies connected.

- Configuration logic added by ldreger.

- mimeyer introduced the initial character-object design.

- Basic finite-state-machine (FSM) framework added for the game loop.

- Abstract state class and state-specific inheritance established.

- Game-loop and model branches integrated.

### Sep 16 — Wednesday

Tile awareness and sprite foundations

The game world is prepared for more sophisticated navigation and rendering.

- Neighbor-aware tile generation implemented.

- Basic sprite-sheet logic added.

# Phase 2 — Playable character, level model, and HUD
### Sep 17 — Thursday

Level and player logic

The project progresses from foundational architecture to concrete gameplay entities.

- Level and player logic added.

- General code cleanup performed.

### Sep 18 — Friday

Map boundaries and first HUD work

The game gains a more defined play area and its initial information display.

- Borders added to tile generation.

- Beginning of the HUD implemented.

### Sep 19 — Saturday

Viewport and level sizing

The rendering system is adjusted to fit the game world to the display.

- Level tiling adjusted to screen width and height.

- Initial screen-sizing implementation recorded as imperfect, indicating further refinement was needed.

### Sep 21 — Monday

Centralized game loading and integration

The game-loading architecture is consolidated and development branches are integrated.

- Game class added for centralized loading by ldreger.

- A commit marked “Ready to merge” recorded.

- Main branch integrated into mimeyer's branch.

- Dependency lockfile restored.

- Game logic modified.

### Sep 23 — Wednesday

Game loop, movement constraints, logging, and HUD

The project combines state-based execution with movement rules and player-facing information.

- FSM execution and state transitions developed.

- Game-loop directories and class organization refactored.

- Character classes and reusable parent-class methods reorganized.

- Movement constrained to open corridors and checked against walls.

- Logging package introduced for debugging.

- Basic score HUD added by ldreger.

- Life-counter HUD added by ldreger.

- Maze-generation and game-loop pull requests integrated.

# Phase 3 — Ghost development, navigation, and game mechanics
### Sep 24 — Thursday

Ghost classes and tile-navigation infrastructure

Enemy characters are introduced, alongside the underlying tile and movement infrastructure.

- Ghost type introduced through the character model.

- Ghost initialization, rendering, image handling, and parent interactions developed.

- Placeholder sprites and ghost-related update methods added.

- Tile matrix, tile-position, and unit-vector methods developed.

- Logging and movement-object type hints improved.

- Ghost movement attempted but described as broken; it was subsequently commented out.

- Documentation and several structural fixes committed.

- ldreger added ghost sprites and tile-color cycling controls.

- Makefile fix received from the collaborating branch.

### Sep 25 — Friday

Breadth-first search (BFS) and maze integration

Pathfinding infrastructure is added to support more intelligent ghost behavior.

- BFS implementation added for navigation.

- Reference creation added for tiles.

- Dataclass compatibility fixed in reference creation.

- Maze-generation tiling branch merged into the main development branch.

- Ghost navigation and tile-coordinate infrastructure continued to evolve.

### Sep 26 — Saturday

Movement tuning and level initialization refactoring

Player and ghost movement are refined while level initialization is reorganized.

- Ghost movement made functional and then slowed.

- Player speed reduced.

- Level and screen initialization refactored.

- New-level calls adapted to the game-loop architecture.

- Python version adjusted for Pygame compatibility.

- Map size reduced.

- Speed-scaling issue identified.

### Sep 27 — Sunday

Collision, level progression, and player-state refactoring

Gameplay becomes more complete through collision handling, level transitions, and state management.

- Ghost collision logic added.

- Pause-gameplay functionality introduced.

- Level step-over and completion logic developed.

- Player score converted to a class-level variable.

- Infinite-loop bug in Inky's movement corrected.

- Level initialization, asset caching, and screen initialization refactored.

- Player state and level-entry behavior improved.

- Remaining tasks recorded in commit messages.

### Sep 28 — Monday

Persistent player lifecycle and level-entry behavior

The architecture is refined to maintain player state across multiple levels.

- One player object reused across the game loop.

- Late initialization added for each level.

- Level-entry wait behavior introduced.

- Player attributes adjusted during level changes.

- Character refactoring and direction-change handling improved.

# Phase 4 — Menu system, game states, and high-score functionality
### Oct 4 — Sunday

Player-death handling and gameplay stability

The game-loop behavior and player lifecycle are stabilized in preparation for a more complete user interface.

- Player-state handling refactored.

- Death-state handler introduced.

- Screen clearing on level change fixed.

- Escape-to-exit behavior added.

- Character movement glitch fixed for speeds not divisible by tile size.

- Test data updated and categorized.

- Initialization changes repeatedly reverted and reapplied.

### Oct 5 — Monday

FSM alignment and main-menu development

The user interface begins to take shape around the state-machine architecture.

- Player-death logic refactored into the FSM.

- Player lives made functional.

- Game-object logic adapted to the FSM architecture.

- General refactoring and documentation cleanup performed.

- Initial main-menu layout implemented.

- Minor changes and fixes committed.

### Oct 6 — Tuesday

Main-screen implementation and game-time enforcement

The main screen is implemented, and time-limit behavior is added.

- Main-screen implementation recorded.

- Static Pac-Man character included and character positioning corrected.

- FSM documentation and naming compliance improved.

- Time-limit enforcement introduced.

- Linting corrected to inspect all Python files.

- Merge from ldreger's branch integrated.

### Oct 7 — Wednesday

Collectibles, level cycling, and high-score states

The game gains a more complete gameplay loop, including collectibles, scoring, and end-of-game states.

- Pac-gum and super Pac-gum generation added.

- Level-cycle logic implemented, including quitting after all collectibles are eaten.

- Ghost fleeing behavior developed, though initially buggy.

- High-score display and name-entry states introduced.

- Score display added to the game-over screen.

- High-score null-value bugs fixed.

- Cheat navigation, speed-hack, ghost-freeze, and live-generation debugging features added.

- Additional requirement-related changes and lint fixes committed.

- Multiple pull requests merged.

### Oct 8 — Thursday

Major gameplay integration day

Core gameplay, enemy AI, menus, timing, and player guidance are integrated and refined.

- Functional timer added.

- Main-menu logic and super Pac-gums implemented.

- Player color changed.

- Level-configuration state mismatch identified.

- Ghost fleeing and BFS logic improved.

- Ghosts made to flee toward corners while avoiding the player.

- Ghost respawn cycle and respawn speed-up behavior added.

- Scoring adjusted to respect configuration.

- Guide state, selection, and menu access added.

- Linting, typing, and general code updates performed.

- Package-generation functionality added.

- Consistent maze seeding fixed.

- Returning to the main menu from gameplay implemented.

- Branch merges and integration changes recorded.

### Oct 9 — Friday

Player guide improvement

Player-facing instructions and usability are refined following the major gameplay integration.

- Guide functionality improved.
# Phase 5 — Reliability, packaging, and release preparation
### Oct 10 — Saturday

Bug fixing, score persistence, and code cleanup

Development shifts toward reliability, project compliance, and maintainability.

- Score persistence after returning to the main menu fixed.

- Scoreboard updates corrected when a new score is lower.

- Crashes from excessive dimensions fixed.

- Docstrings and code cleanup added.

- pac-man.py entry point added for project-specification compliance.

- Makefile targets and cache-cleaning behavior updated.

- Multiline configuration comments removed.

- README and project structure continued to be refined.

### Oct 11–12 — Sunday–Monday

No commits listed

No commits are included for these dates in the supplied history.

- No recorded development milestones can be confirmed for this period.

- The available history does not establish whether testing, planning, or other work took place.

### Oct 13 — Tuesday

Configuration hardening

The project becomes more resilient to invalid or unexpected configuration values.

- Configuration values clamped to safe ranges.

- Fallback behavior added for invalid configuration.

### Oct 14 — Wednesday

Code quality and high-score validation

Development tooling, diagnostics, and data validation are improved.

- Lint compliance fixed.

- Debug-mode Makefile target added.

- Logging improved.

- High-score validation added.

### Oct 15 — Thursday

Player documentation

Documentation is updated to help players understand the controls.

- README updated with movement information.
### Oct 16 — Friday

Release preparation and publication

The final recorded development day focuses on user-facing features, build configuration, documentation, and publication.

- Makefile build rule and README updated.

- Maze-seeding behavior corrected so the seed applies only to the first maze.

- Pause menu added.

- Win and lose screens added.

- README updated again.

- High-score data reset or cleared, according to the “Emptied highscore” commit.

- Pac-Man published on itch.io, according to the “Add: Pacman on itch” commit.

Milestone: The latest listed development activity culminates in publication, with final gameplay screens and build improvements recorded on the same date.