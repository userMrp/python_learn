import pygame
import random
import os

# 初始化Pygame
pygame.init()

# 设置屏幕大小
screen_width = 720
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Match 3 Game")

# 定义颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# 设置工作目录为脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 图片路径
image_folder = "pic/nezha/"
images = [pygame.image.load(os.path.join(image_folder, f"{i}.png")).convert_alpha() for i in range(1, 6)]

# 网格设置
grid_size = 9
tile_size = screen_width // grid_size


# 创建一个随机初始化的网格
def create_grid():
    return [[random.randint(0, 4) for _ in range(grid_size)] for _ in range(grid_size)]


# 检查是否有匹配项
def check_matches(grid):
    matches = set()
    # Check horizontal matches
    for y in range(grid_size):
        for x in range(grid_size - 2):
            if grid[y][x] == grid[y][x + 1] == grid[y][x + 2] != -1:
                matches.add((y, x))
                matches.add((y, x + 1))
                matches.add((y, x + 2))

    # Check vertical matches
    for x in range(grid_size):
        for y in range(grid_size - 2):
            if grid[y][x] == grid[y + 1][x] == grid[y + 2][x] != -1:
                matches.add((y, x))
                matches.add((y + 1, x))
                matches.add((y + 2, x))

    return matches


# 移除匹配项并让上方的方块落下
def remove_matches(grid, matches, fall_duration):
    new_tiles = {}
    for y, x in matches:
        grid[y][x] = -1
    for x in range(grid_size):
        offset = 0
        for y in range(grid_size - 1, -1, -1):
            if grid[y][x] == -1:
                offset += 1
            else:
                grid[y + offset][x] = grid[y][x]
                if offset > 0:
                    start_pos = (-offset * tile_size, (y + offset) * tile_size)
                    end_pos = (x * tile_size, (y + offset) * tile_size)
                    new_tiles[(y + offset, x)] = ("fall", pygame.time.get_ticks(), fall_duration, start_pos, end_pos)
        for y in range(offset):
            new_value = random.randint(0, 4)
            grid[y][x] = new_value
            start_pos = (-tile_size, y * tile_size)
            end_pos = (x * tile_size, y * tile_size)
            new_tiles[(y, x)] = ("fall", pygame.time.get_ticks(), fall_duration, start_pos, end_pos)
    return new_tiles


# 绘制网格
def draw_grid(grid, animations):
    for y in range(grid_size):
        for x in range(grid_size):
            image_index = grid[y][x]
            if image_index != -1:
                pos_x = x * tile_size
                pos_y = y * tile_size

                # Apply animation if any
                if (y, x) in animations:
                    anim_type, start_time, duration, start_pos, end_pos = animations[(y, x)]
                    elapsed = (pygame.time.get_ticks() - start_time) / 1000.0

                    if elapsed < duration:
                        if anim_type == "swap":
                            t = elapsed / duration
                            pos_x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
                            pos_y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
                        elif anim_type == "fall":
                            t = elapsed / duration
                            pos_y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
                    else:
                        del animations[(y, x)]

                screen.blit(images[image_index], (pos_x, pos_y))


# 主循环
def main():
    clock = pygame.time.Clock()
    grid = create_grid()
    selected_tile = None
    running = True
    animations = {}
    swap_start_time = 0
    swap_duration = 1.0  # 1 second for swap animation
    fall_duration = 1.0  # 1 second for fall animation

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                col = x // tile_size
                row = y // tile_size
                if selected_tile is not None and (abs(selected_tile[0] - row) + abs(selected_tile[1] - col)) == 1:
                    # Record the swap animation
                    start_pos = (selected_tile[1] * tile_size, selected_tile[0] * tile_size)
                    end_pos = (col * tile_size, row * tile_size)
                    animations[(selected_tile[0], selected_tile[1])] = (
                    "swap", pygame.time.get_ticks(), swap_duration, start_pos, end_pos)
                    animations[(row, col)] = ("swap", pygame.time.get_ticks(), swap_duration, end_pos, start_pos)

                    # Swap tiles in a temporary state
                    temp = grid[selected_tile[0]][selected_tile[1]]
                    grid[selected_tile[0]][selected_tile[1]] = grid[row][col]
                    grid[row][col] = temp

                    # Check for matches
                    matches = check_matches(grid)
                    if len(matches) > 0:
                        new_anims = remove_matches(grid, matches, fall_duration)
                        animations.update(new_anims)

                    else:
                        # Swap back if no match
                        temp = grid[selected_tile[0]][selected_tile[1]]
                        grid[selected_tile[0]][selected_tile[1]] = grid[row][col]
                        grid[row][col] = temp

                    selected_tile = None
                else:
                    selected_tile = (row, col)

        # Draw the grid
        draw_grid(grid, animations)

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
    main()


