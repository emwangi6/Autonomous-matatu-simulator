import pygame
import random

pygame.init()

# Screen setup
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("MATATU SIMULATOR")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
brown = (165, 42, 42)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)


# Matatu setup
lanes = [100, 300, 500, 700]  # starts from left to right (0,1,2,3)
matatu_lane_index = 1  # start in lane 300
matatu_x = lanes[matatu_lane_index]
matatu_y = 400  # fixed vertical position
scroll_y = 0

# Obstacles + zebra setup
obstacles = []
zebra_crossings = []
paused = False  # game pause state
current_zebra = None  # tracks the zebra that paused the game
zebra_ignore_timer = 0  # timer to ignore zebra detection after unpause

SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 1500)  # obstacle spawn after 1.5 seconds

ZEBRA_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(ZEBRA_EVENT, 10000)  # zebra spawn after 10 seconds


# FUNCTIONS
def near_zebra():
    # Check if zebra crossing is close to the matatu
    global current_zebra
    for zx, zy in zebra_crossings:
        if matatu_y - 70 < zy < matatu_y + 100:  # zebra ahead of matatu
            if current_zebra is None:  # only trigger once per zebra
                current_zebra = (zx, zy)
                return True
    return False


def ai_dodge():
    #Matatu AI to dodge obstacles smoothly
    global matatu_lane_index, matatu_x

    danger = None
    for obs_x, obs_y in obstacles:
        if abs(obs_y - matatu_y) < 150:  # obstacle close
            if abs(obs_x - lanes[matatu_lane_index]) < 60:  # same lane
                danger = (obs_x, obs_y)
                break

    if danger:
        # Check which lanes are safe
        safe_lanes = []
        for i, lx in enumerate(lanes):
            blocked = False
            for ox, oy in obstacles:
                if abs(oy - matatu_y) < 150 and abs(ox - lx) < 60:
                    blocked = True
                    break
            if not blocked:
                safe_lanes.append(i)

        # Pick nearest safe lane
        if safe_lanes:
            best_lane = min(safe_lanes, key=lambda i: abs(i - matatu_lane_index))
            matatu_lane_index = best_lane

    # Smooth movement toward chosen lane
    target_x = lanes[matatu_lane_index]
    if matatu_x < target_x:
        matatu_x += 5
    elif matatu_x > target_x:
        matatu_x -= 5


def draw():
    global scroll_y
    screen.fill(brown)

    # Road background
    pygame.draw.rect(screen, black, (50, 0, 700, 600))

    # Lane dividers
    for i in range(0, height, 40):
        pygame.draw.rect(screen, yellow, (395, (i + scroll_y) % height, 10, 20))

    # Side lane markers
    for i in range(0, height, 50):
        pygame.draw.rect(screen, white, (205, (i + scroll_y) % height, 5, 30))
    for i in range(0, height, 50):
        pygame.draw.rect(screen, white, (595, (i + scroll_y) % height, 5, 30))

    # Roadside flowers
    for i in range(0, height, 100):
        y = (i + scroll_y) % height
        pygame.draw.circle(screen, red, (30, y + 30), 10)
        pygame.draw.circle(screen, green, (30, y + 30), 5)
        pygame.draw.circle(screen, red, (770, y + 30), 10)
        pygame.draw.circle(screen, green, (770, y + 30), 5)

    # Draw zebra crossings (under vehicles) 
    for zx, zy in zebra_crossings:
        for i in range(0, 700, 40):
            pygame.draw.rect(screen, white, (50 + i, zy, 20, 50))

    # Draw matatu
    body_width = 50
    body_height = 125
    pygame.draw.rect(screen, blue, (matatu_x, matatu_y, body_width, body_height))
    pygame.draw.rect(screen, yellow, (matatu_x + 5, matatu_y + 20, 40, 30))
    pygame.draw.rect(screen, yellow, (matatu_x + 5, matatu_y + 70, 40, 30))
    pygame.draw.circle(screen, red, (matatu_x + body_width // 2, matatu_y + 10), 8)

    # Draw obstacles
    for obs_x, obs_y in obstacles:
        pygame.draw.rect(screen, green, (obs_x, obs_y, 50, 100))
        pygame.draw.circle(screen, red, (obs_x + 25, obs_y + 10), 8)
        pygame.draw.rect(screen, yellow, (obs_x + 5, obs_y + 20, 40, 30))
        pygame.draw.rect(screen, yellow, (obs_x + 5, obs_y + 60, 40, 30))

    # Pause message
    if paused:
        font = pygame.font.SysFont("Arial", 36, bold=True)
        text = font.render("Zebra Crossing!!! Press SPACE to continue", True, red)
        screen.blit(text, (100, 250))

    pygame.display.update()

# MAIN LOOP
def main():
    global scroll_y, paused, current_zebra, zebra_ignore_timer
    clock = pygame.time.Clock()
    run = True

    while run:
        draw()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            elif event.type == SPAWN_EVENT and not paused:
                lane_x = random.choice(lanes)
                obstacles.append([lane_x, -120])
            elif event.type == ZEBRA_EVENT and not paused:
                zebra_crossings.append([0, -20])  # spawn new zebra crossing
            elif event.type == pygame.KEYDOWN and paused:
                if event.key == pygame.K_SPACE:  # resume game
                    paused = False
                    zebra_ignore_timer = 60  # ignore zebra for 1 second 
                    if current_zebra in zebra_crossings:
                        zebra_crossings.remove(current_zebra)  # remove zebra
                    current_zebra = None  # reset

        if not paused:
            # Update scroll position
            scroll_y += 5
            if scroll_y > height:
                scroll_y = 0

            # Move obstacles
            for obs in obstacles:
                obs[1] += 5
            obstacles[:] = [obs for obs in obstacles if obs[1] < height]

            # Move zebra crossings
            for zebra in zebra_crossings:
                zebra[1] += 5
            zebra_crossings[:] = [z for z in zebra_crossings if z[1] < height]

            # AI movement 
            ai_dodge()

            # Zebra detection (with ignore timer)
            if zebra_ignore_timer > 0:
                zebra_ignore_timer -= 1  # countdown timer
            else:
                if near_zebra():
                    paused = True

        clock.tick(30)

    pygame.quit()
    quit()


if __name__ == "__main__":
    main()

