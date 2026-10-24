# Phase 1 — Initial task list and gameplay requirements
### Sep 27 — Sunday, 20:36:30

Initial TODO list created

Mika Meyer created TODO.md to track outstanding bugs and features following work on the level logic.

Bugs to fix:

- Fix game-breaking behavior when using different movement-speed values.

Features to implement:

- Make ghosts kill the player.

- Include super Pac-gums.

- Allow ghosts to be eaten.

- Add a start menu.

- Add game-over and win screens.

- Implement a leaderboard.

- Implement level changes.

- Enforce a level time limit.

- Add cheat mode.

- Add a pause menu.

Project-management significance: this establishes the first explicit backlog of gameplay requirements, covering core mechanics, user interface, progression, and optional gameplay controls.
### Sep 27 — Sunday, 21:48:44

Level-transition requirements refined

The TODO list was updated after the commit that recorded completion of level logic.

- Removed the generic level change task.

- Added a requirement to wait for a button press when entering a level.

- Added a requirement to ensure Pygame clears the screen before rendering the next level or screen.

Interpretation: the backlog shifted from implementing level progression itself toward polishing the transition experience and preventing visual artifacts.
### Sep 28 — Monday, 02:05:35

Pause-menu requirements and player-state persistence

The pause-menu task was refined, and a new level-initialization issue was identified.

- Replaced the generic pause-menu requirement with show details on pause.

- Removed the level-entry button-press requirement.

- Added a task to reset player attributes when changing levels.

- Retained the screen-clearing requirement.

Bugs still outstanding:

- Game-breaking movement speeds.

- Ghosts not yet reliably killing the player.

- Player attributes potentially carrying over incorrectly between levels.

- Screen clearing during transitions.

Interpretation: the project was beginning to distinguish between the existence of a feature and the finer details of its behavior.
# Phase 2 — Bug tracking and player-death mechanics
### Oct 4 — Sunday, 18:36:40

Additional gameplay and rendering bugs recorded

The backlog expanded following further gameplay development.

- Added a requirement for levels to load fully within the frame.

- Added a requirement to wait for input after the player respawns following death.

- Added a requirement to deduct a life when the player dies.

- Added a requirement to increase the ghost collision radius.

- Retained the time limit, cheat mode, pause details, and other outstanding features.

Key focus: collision reliability, death and respawn behavior, and correct screen rendering.
### Oct 4 — Sunday, 23:35:03

TODO backlog categorized into bugs and features

Mika reorganized the list to make outstanding work easier to prioritize.

- Created a Bugs section, divided into Movement, Logic, and Visual categories.

- Kept the movement-speed problem under Movement.

- Grouped the respawn-input and ghost-collision-radius issues under Logic.

- Grouped incomplete level rendering and screen-size compatibility under Visual.

- Moved the level time limit into the Features section.

- Retained super Pac-gums, edible ghosts, start menu, game-over/win screens, leaderboard, cheat mode, and pause details as feature tasks.

- Retained life deduction on player death.

Project-management significance: the TODO file became a structured backlog rather than a simple flat list.
### Oct 4 — Sunday, 23:39:41

Movement-speed bug removed from the backlog

The movement-speed issue was removed from the TODO list.

- The speed-related bug was no longer listed as outstanding.

- Other logic and visual bugs remained open.

Important qualification: this indicates that the issue was removed from the tracked backlog; the TODO diff alone does not prove the exact fix or its testing status.
### Oct 5 — Monday, 01:20:36

Player death and life deduction implemented

The commit feat: refactor player death logic to fsm; fix: player can actually loose lives corresponds with several backlog changes.

- Removed the requirement to wait for input after player death and respawn.

- Removed the life-deduction task.

- Reduced the game-over/win requirement to a game-over screen.

- Retained the ghost collision-radius issue.

- Retained visual issues involving level framing and screen sizing.

Milestone: player-death handling and life deduction were treated as implemented, and the backlog was narrowed to the remaining screen and collision work.
### Oct 5 — Monday, 03:14:24

Outstanding bugs linked to source-code locations

The TODO file began linking remaining issues directly to relevant code.

- Linked the ghost collision-radius issue to src/pac_man/loop/level.py.

- Linked level framing and screen sizing to the level initialization code.

- Added a death-animation duration issue, linked to the game loop.

- Linked the level time-limit task to the game loop.

- Linked the start menu and game-over screen to the FSM implementation.

Interpretation: the backlog became more actionable by connecting requirements to specific implementation locations.
### Oct 5 — Monday, 19:18:47

Player spawn issue identified

A new logic bug was added:

- Player can spawn in an enclosed space on maps containing the 42 sign.

The existing ghost collision-radius and rendering issues remained.

Key focus: ensuring generated maps provide valid player spawn locations.
# Phase 3 — Main menu, time limit, and high-score development
### Oct 6 — Tuesday, 03:32:50

Start-menu task removed

The commit feat: mainscreen implementation coincided with removal of the linked start-menu item.

- Start menu removed from the outstanding feature list.

- Game-over screen remained outstanding.

- Super Pac-gums and edible ghosts remained outstanding.

- Rendering and spawn-related issues remained tracked.

Milestone: main-screen implementation was reflected in the TODO backlog.
### Oct 6 — Tuesday, 23:38:12

Game time limit implemented; display tasks added

The commit feat: game time limit enforced coincided with further backlog changes.

- Removed the level time-limit task.

- Added a task to visualize lost lives.

- Added a task to visualize the timer.

- Retained the game-over screen, super Pac-gums, edible ghosts, cheat mode, and pause details.

Milestone: the time-limit behavior was no longer tracked as an outstanding feature, while its user-facing display still needed attention.
### Oct 7 — Wednesday, 02:31:49

High-score entry and display introduced

The commit feat: Highscore site and entering added as states coincided with a change in the backlog.

- Removed the generic leaderboard task.

- Added an optional task to improve the appearance of high-score screens.

- Retained the game-over screen and remaining gameplay features.

- Kept timer and lost-life visualization tasks open.

Interpretation: high-score functionality had advanced enough for the backlog to shift toward presentation improvements.
### Oct 7 — Wednesday, 05:02:42

Screen-framing bugs removed

Following the commit fix: screen cut off at bottom:

- Removed the level-framing issue.

- Removed the screen-size compatibility issue.

- Retained the death-animation duration issue.

- Retained timer and lost-life visualization tasks.

Milestone: two rendering issues were removed from the backlog following a corresponding screen-rendering fix.
### Oct 7 — Wednesday, 07:16:20

Player spawn bug removed

The commit fix: player spawn in 42 sign coincided with the removal of the enclosed-spawn issue.

- Removed the player-spawn bug from the Logic section.

- Retained the ghost collision-radius issue.

- Retained the remaining visual and gameplay tasks.

Milestone: the known spawn issue was no longer tracked as outstanding.
### Oct 7 — Wednesday, 08:59:35

Game-over flow refined

The commit fix: game over on name enter coincided with additional TODO changes.

- Removed the lost-life visualization task.

- Added an optional improvement for the game-over screen.

- Retained timer visualization and high-score screen improvements.

- Removed the game-over screen and cheat mode from the remaining feature list.

- Retained super Pac-gums, edible ghosts, and pause details.

Interpretation: the game-over flow had progressed, leaving presentation improvements as optional work.
### Oct 7 — Wednesday, 09:01:40

Remaining presentation work reprioritized

The TODO list was reorganized again.

- Marked the ghost collision-radius issue as a bonus task.

- Marked death-animation duration as a bonus task.

- Marked high-score screen improvements as optional.

- Marked game-over screen improvements as optional.

- Marked pause details as optional.

- Kept timer visualization as an outstanding visual task.

- Retained super Pac-gums and edible ghosts as feature requirements.

Project-management significance: the backlog distinguished core requirements from lower-priority polish.
### Oct 7 — Wednesday, 09:04:07

Remaining requirements expanded

The commit remaining requirments added more explicit user-interface and navigation tasks.

- Added display of the final score.

- Added visualization of the current level.

- Added an instructions option to the main menu.

- Added the ability to return to the main menu from gameplay.

- Retained timer visualization and optional presentation improvements.

- Retained super Pac-gums and edible ghosts.

### Oct 7 — Wednesday, 09:29:13

Final-score display removed from outstanding work

The commit fix: highscores to null bug; feat: score on game over screen coincided with removal of the final-score display task.

- Removed the final-score visualization task.

- Retained current-level visualization.

- Retained timer visualization.

- Retained optional high-score and game-over screen improvements.

Milestone: showing the score on the game-over screen was now reflected in the code and no longer tracked as outstanding.
# Phase 4 — Ghost behavior, menu navigation, and collectible mechanics
### Oct 7 — Wednesday, 15:00:36

Ghost behavior identified as a major remaining issue

The commit feet: ghost can be turned into fleeing, but buggggyy coincided with a new bug entry.

- Added a ghost-movement bug described as “fix da ghsot”.

- Removed edible ghosts from the feature list, suggesting that work had begun on the mechanic.

- Retained super Pac-gums.

- Retained the instructions option and return-to-main-menu requirement.

Key focus: ghost behavior was still unstable, despite progress on fleeing mechanics.
### Oct 8 — Thursday, 03:44:58

Returning to the main menu implemented; ghost interaction issues documented

Following return to main menu from gameloop:

- Removed the generic ghost-movement bug.

- Removed the super Pac-gum and return-to-menu tasks from the outstanding feature list.

- Added a bug where super Pac-gums should cause ghosts to flee.

- Added a bug where ghosts sometimes cannot be eaten while respawning.

- Retained the bonus ghost collision-radius issue.

- Retained timer and current-level visualization.

Milestone: main-menu navigation was no longer tracked as outstanding, while the remaining ghost interaction issues were recorded more precisely.
### Oct 8 — Thursday, 04:29:48

Scoring and linting improvements

The commit fix: eaten objects score points accroding to config; fix: lint coincided with a reprioritization.

- Retained the super Pac-gum fleeing issue.

- Downgraded the respawning-ghost edibility issue to a bonus task.

- Retained the bonus collision-radius issue.

- Kept timer and current-level visualization outstanding.

Interpretation: scoring behavior was addressed in code, while remaining ghost edge cases were increasingly treated as optional polish.
### Oct 8 — Thursday, 04:53:05

Super Pac-gum placement and optional polish refined

The TODO list was reorganized.

- Added a requirement to spawn super Pac-gums in corners.

- Removed the respawning-ghost edibility issue from the core bug list and moved it into Optional.

- Moved death-animation duration, high-score screen polish, game-over screen polish, and pause details into Optional.

- Retained timer and current-level visualization.

- Retained the instructions option in the main menu.

Key focus: collectible placement and the remaining core presentation requirements.
### Oct 8 — Thursday, 05:33:01

Guide functionality tracked

The commit feat: guide state and selection coincided with a new visual task.

- Added a task to improve the information displayed in the guide.

- Retained timer visualization and current-level visualization.

- Kept high-score configuration and visual improvements in Optional.

### Oct 8 — Thursday, 05:47:16

Guide accessible from the menu

The commit feat: guide access from menu coincided with further refinement.

- Removed the guide-information display task.

- Added an optional task to improve the guide.

- Retained timer and current-level visualization.

Milestone: guide access had been implemented; further guide improvements were treated as optional.
### Oct 8 — Thursday, 12:07:59

Super Pac-gum fleeing behavior removed from the backlog

The commit Add: Super Pacgums and main menu logic coincided with removal of the requirement for super Pac-gums to make ghosts flee.

- Removed the super Pac-gum fleeing issue from the outstanding list.

- Retained the requirement to spawn super Pac-gums in corners.

- Retained current-level visualization.

- Kept optional polish and edge cases.

Interpretation: the core super Pac-gum behavior was considered sufficiently implemented to remove its corresponding task.
### Oct 8 — Thursday, 14:12:18

Timer visualization task removed

The commit Add: Functional Timer coincided with removal of the timer-visualization task.

- Removed timer visualization from the outstanding visual requirements.

- Retained current-level visualization.

- Retained super Pac-gum corner placement and optional polish.

Milestone: the timer was implemented, and its corresponding display task was no longer tracked.
# Phase 5 — Final cleanup and release preparation
### Oct 9 — Friday, 10:33:41

Guide improvement task removed

The commit feat: guide improvement coincided with removal of the optional guide-improvement task.

- Removed the guide-improvement task from Optional.

- Retained the optional high-score configuration task.

- Retained the optional death-animation, high-score presentation, game-over presentation, pause details, respawning-ghost interaction, and collision-radius tasks.

- Current-level visualization remained outstanding.

### Oct 16 — Friday, 15:50:37

TODO file removed during release preparation

The commit Add: Makefile build rule and README update deleted TODO.md.

Immediately before deletion, the remaining backlog contained:

Remaining functional or visual tasks:

- Spawn super Pac-gums in corners.

- Visualize the current level.

Optional improvements:

- Load the high-score file path from configuration.

- Correct the death-animation duration.

- Improve the appearance of high-score screens.

- Improve the game-over screen.

- Show additional details on the pause screen.

- Address occasional ghost-edibility issues while a ghost is respawning.

- Increase the ghost collision radius.

Project-management significance: the TODO file was removed on the same date as build-rule and documentation changes and the recorded itch.io publication. Its deletion does not prove that every remaining task was completed; some may have been deferred, considered unnecessary, or left untracked.
Summary of backlog evolution

| Period | Main focus | Observed progress |
| - | - | - |
| Sep 27–28 | Initial gameplay requirements | Initial bugs and features recorded; level-transition and player-state requirements refined |
| Oct 4–5 | Stability and death mechanics | Movement issue removed; life deduction and death handling implemented; bugs categorized |
| Oct 6–7 | Menus, timer, high scores | Main menu and time-limit tasks removed; high-score flow and game-over scoring developed |
| Oct 7–8 | Ghosts, collectibles, and navigation | Ghost issues narrowed; menu return, guide access, super Pac-gums, and timer functionality addressed |
| Oct 9 | Guide and polish | Guide-improvement task removed |
| Oct 16 | Release preparation | TODO file deleted; optional polish and a small number of feature tasks remained in its final version |