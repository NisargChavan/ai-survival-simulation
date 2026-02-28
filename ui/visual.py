import pygame
import os

# ===============================
# WORLD SETTINGS
# ===============================
WORLD_WIDTH = 50
WORLD_HEIGHT = 50

# Maximum window size (to keep it reasonable)
MAX_SCREEN_WIDTH = 1000
MAX_SCREEN_HEIGHT = 800

# ===============================
# AUTO CELL SIZE (Fit to screen)
# ===============================
CELL_SIZE_X = MAX_SCREEN_WIDTH // WORLD_WIDTH
CELL_SIZE_Y = MAX_SCREEN_HEIGHT // WORLD_HEIGHT
CELL_SIZE = min(CELL_SIZE_X, CELL_SIZE_Y)

SCREEN_WIDTH = WORLD_WIDTH * CELL_SIZE
SCREEN_HEIGHT = WORLD_HEIGHT * CELL_SIZE

# ===============================
# INIT
# ===============================
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI Survival World")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 18)

# ===============================
# ASSETS
# ===============================
ASSET_PATH = os.path.join("assets")

grass_img = pygame.image.load(os.path.join(ASSET_PATH, "grass.png"))
grass_img = pygame.transform.scale(grass_img, (CELL_SIZE, CELL_SIZE))

seed_img = pygame.image.load(os.path.join(ASSET_PATH, "seeds.png"))
seed_img = pygame.transform.scale(seed_img, (CELL_SIZE, CELL_SIZE))

crop_img = pygame.image.load(os.path.join(ASSET_PATH, "crop.png"))
crop_img = pygame.transform.scale(crop_img, (CELL_SIZE, CELL_SIZE))

farmland_img = pygame.image.load(os.path.join(ASSET_PATH, "farmland.png"))
farmland_img = pygame.transform.scale(farmland_img, (CELL_SIZE, CELL_SIZE))

# ===============================
# COLORS
# ===============================
RED = (220, 60, 60)
GREEN = (60, 200, 80)
BLUE = (70, 120, 240)
YELLOW = (240, 220, 70)
PURPLE = (180, 80, 220)
ORANGE = (255, 140, 0)
BLACK = (30, 30, 30)

AGENT_COLORS = {
    "A": RED,
    "B": BLUE,
    "C": GREEN
}

# ===============================
# DRAW WORLD
# ===============================
def draw_world(agents, foods, farms, crops, episode, step, energy_packs, dangers):

    # ---- Grass Background ----
    for x in range(WORLD_WIDTH):
        for y in range(WORLD_HEIGHT):
            screen.blit(grass_img, (x * CELL_SIZE, y * CELL_SIZE))
            
    # ---- Agent Plots ----
    for agent in agents:
        cx, cy = agent.plot_center
        half = agent.plot_size // 2
        
        for x in range(cx - half, cx + half + 1):
            for y in range(cy - half, cy + half + 1):
                if 0 <= x < WORLD_WIDTH and 0 <= y < WORLD_HEIGHT:
                    screen.blit(
                        farmland_img,
                        (x * CELL_SIZE, y * CELL_SIZE)
                    )        

    # ---- Food ----
    for fx, fy in foods:
        pygame.draw.rect(
            screen,
            YELLOW,
            (
                fx * CELL_SIZE + CELL_SIZE//4,
                fy * CELL_SIZE + CELL_SIZE//4,
                CELL_SIZE//2,
                CELL_SIZE//2
            )
        )

    # ---- Farms (growing) ----
    for (fx, fy), farm in farms.items():
        screen.blit(seed_img, (fx * CELL_SIZE, fy * CELL_SIZE))

    # ---- Crops (ready) ----
    for (fx, fy), owner in crops.items():
        screen.blit(crop_img, (fx * CELL_SIZE, fy * CELL_SIZE))

    # ---- Energy Packs ----
    for ex, ey in energy_packs:
        pygame.draw.rect(
            screen,
            PURPLE,
            (
                ex * CELL_SIZE + CELL_SIZE//4,
                ey * CELL_SIZE + CELL_SIZE//4,
                CELL_SIZE//2,
                CELL_SIZE//2
            )
        )

    # ---- Danger ----
    for dx, dy in dangers:
        pygame.draw.rect(
            screen,
            ORANGE,
            (
                dx * CELL_SIZE,
                dy * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE
            ),
            2
        )

    # ---- Agents ----
    for agent in agents:
        if agent.energy <= 0:
            continue

        color = AGENT_COLORS.get(agent.name, BLACK)

        pygame.draw.rect(
            screen,
            color,
            (
                agent.x * CELL_SIZE + 2,
                agent.y * CELL_SIZE + 2,
                CELL_SIZE - 4,
                CELL_SIZE - 4
            )
        )

    # ---- UI Text ----
    ep_text = font.render(f"Episode: {episode}", True, (0, 0, 0))
    step_text = font.render(f"Step: {step}", True, (0, 0, 0))

    screen.blit(ep_text, (10, 10))
    screen.blit(step_text, (10, 30))

    pygame.display.flip()
    clock.tick(100)