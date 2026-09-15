
from . import MazeGenerator, Map, Player, Ghost, Tile

def get_maze(size: tuple[int], seed) -> list[list[int]]:
    gen = MazeGenerator(
        size=size,
        seed=seed
    )
    return (gen.maze)

def main():
    maze = get_maze((15,15), 42)
    map_array: list[list[Tile]] = Map().create_map(maze)
    player = Player

if __name__ == "__main__":
    main()