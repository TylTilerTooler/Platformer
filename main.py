import pygame
import random
import time
import math
import sys
import threading

pygame.init() # Initialize immediately

from menu import Menu

# window size
WIDTH = 1300
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Global settings
game_settings = {"shadows": True, "daylight_cycle": True, "weather": True, "clouds": True}
pygame.display.set_caption("Platformer")

# fps
clock = pygame.time.Clock()
FPS = 60

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SHADOW_BLACK = (0, 0, 75)
BLUE = (0, 0, 255)
SKY_COLOR = (100, 180, 255)
SPACE_COLOR = (5, 5, 25)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
current_color = WHITE

# fonts
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 60)

def lerp_color(color1, color2, t):
    return (
        int(color1[0] + (color2[0] - color1[0]) * t),
        int(color1[1] + (color2[1] - color1[1]) * t),
        int(color1[2] + (color2[2] - color1[2]) * t)
    )

platforms = []
coins = []
enemies = []
spikes = []
clouds = []
platforms.append(pygame.Rect(0, 540, 3000, 65))

def reset():
    global player, player_vel_x, player_vel_y, player_speed, jump_power, gravity,\
    on_ground, score, hp, invincible_timer, camera_x, min_camera_x, world_end_x, clouds,\
    light_angle, is_raining, rain_timer, rain_drops, till_rain
    # player
    player = pygame.Rect(200, 300, 40, 40)
    player_vel_x = 0
    player_vel_y = 0
    player_speed = 6
    jump_power = -16
    gravity = 1
    on_ground = False

    # scores
    hp = 2
    score = 0
    invincible_timer = 0

    # world & cam
    camera_x = 0
    min_camera_x = 0
    world_end_x = 3000

    clouds = []
    platforms = []


    light_angle = -180
    
    is_raining = False
    rain_timer = 0
    rain_drops = []
    till_rain = random.randint(600, 3600)

    # Initialize random clouds
    for _ in range(12):
        w = random.randint(100, 200)
        h = random.randint(40, 80)
        # Create a surface for each cloud to support transparency
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (255, 255, 255, random.randint(100, 180)), (0, 0, w, h))
        clouds.append({
            "x": random.uniform(0, WIDTH * 2),
            "y": random.randint(20, 250),
            "speed": random.uniform(0.2, 0.7),
            "surf": surf
        })

    platforms.append(pygame.Rect(0, 540, 3000, 65))

# shadow
shadow_x_vel = 0
shadow_y_vel = 0
shadow_speed = 10
shadows = []

is_raining = True
rain_timer = 0
rain_drops = []
light_angle = -180
till_rain = random.randint(600, 3600)

# Reason: We increased the number of rays by calculating every 0.5 degrees instead of 1.
# This ensures that even at the bottom of the screen, the rays are close enough to overlap.
shadows = [{"angle": i * 0.5} for i in range(720)]

# Threading communication variables
shadow_results = [] # Stores (x, y) coordinates for shadows
shadow_lock = threading.Lock()
worker_state = {
    "occluders": [],
    "camera_x": 0,
    "light_angle": -180,
    "running": True,
    "shadows_enabled": True
}
state_lock = threading.Lock()

# Create a transparent surface for shadows
shadow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

def get_velocity(angle, speed):
    angle = math.radians(angle)
    return speed * math.cos(angle), speed * math.sin(angle)

def shadow_worker():
    global shadow_results
    # Optimization: Increased speed and reduced steps to cover screen distance faster
    worker_shadow_speed = 20
    test_rect = pygame.Rect(0, 0, 1, 1)
    while worker_state["running"]:
        # 1. Get a snapshot of the current game state
        with state_lock:
            local_occluders = worker_state["occluders"]
            local_cam_x = worker_state["camera_x"]
            local_light_angle = worker_state["light_angle"]
            local_enabled = worker_state["shadows_enabled"]

        if not local_enabled:
            time.sleep(0.1)
            continue
        
        new_results = []

        light_radius = 800
        light_x = math.cos(math.radians(local_light_angle)) * light_radius
        light_y = math.sin(math.radians(local_light_angle)) * light_radius

        for shadow in shadows:
            curr_x, curr_y = WIDTH // 2 + light_x + local_cam_x, HEIGHT - 250 + light_y
            vx, vy = get_velocity(shadow["angle"], worker_shadow_speed)
            
            shadow_start = None
            has_hit_platform = False
            
            # 100 steps * 20 speed = 2000px, enough to exit any part of the 1300px screen
            for step in range(100): 
                curr_x += vx
                curr_y += vy
                screen_x = curr_x - local_cam_x

                if screen_x < -500 or screen_x > WIDTH + 500 or curr_y > HEIGHT + 100:
                    break
                
                test_rect.x = curr_x
                test_rect.y = curr_y
                in_platform = test_rect.collidelist(local_occluders) != -1
                
                if in_platform:
                    has_hit_platform = True
                elif has_hit_platform and shadow_start is None:
                    shadow_start = (screen_x, curr_y)
            
            if shadow_start:
                # Store the start of the shadow and the final calculated point of the ray
                new_results.append((shadow_start, (screen_x, curr_y)))
        
        # 3. Push results to main thread
        with shadow_lock:
            shadow_results = new_results
            
        time.sleep(0.01) # Prevent thread from hogging 100% CPU





def generate_section(start_x, end_x):
    global platforms, coins, enemies, spikes

    # platforms
    x = start_x
    platform_count = 0

    while x < end_x:
        w = random.randint(120, 180)
        y = random.randint(300, 480)
        h = 40

        new_platform = pygame.Rect(x, y, w, h)

        # 1. Collision Check: Only add if it doesn't overlap any existing platforms
        if new_platform.collidelist(platforms) == -1:
            platforms.append(new_platform)

            if platform_count != 0:
                # coins
                if random.random() < 0.6:
                    coin_count = random.randint(1, 3)
                    for i in range(coin_count):
                        coin_x = x + 20 + i * 30
                        if coin_x < x + w - 20:
                            coins.append(pygame.Rect(coin_x, y - 30, 18, 18))

                # enemies
                if random.random() < 0.3:
                    enemy_w, enemy_h = 30, 30
                    enemy_x = x + random.randint(0, max(0, w - enemy_w))
                    enemy_y = y - enemy_h
                    enemy = {
                        "rect" : pygame.Rect(enemy_x, enemy_y, enemy_w, enemy_h),
                        "speed" :  random.randint(1, 2),
                        "left_bound" : x,
                        "right_bound" : x + w - enemy_w,
                        "dir" : random.choice([-1, 1])
                    }
                    enemies.append(enemy)

                # spikes
                if random.random() < 0.2: # Simplified probability
                    spike_count = random.randint(1, 5)
                    spike_w = spike_count * 25
                    spike_x = x + random.randint(0, max(0, w - spike_w))
                    spike_y = y - 20
                    spikes.append(pygame.Rect(spike_x, spike_y, spike_w, 20))

        # 2. Sequential Update: Move x to the end of this platform + a random gap
        x += w + random.randint(10, 100)
        platform_count += 1

def draw_spikes(screen, spike_rect, camera_x):
    global spike_color
    spike_x = spike_rect.x - camera_x
    spike_y = spike_rect.y
    spike_w = spike_rect.width
    spike_h = spike_rect.height

    triangle_w = 25
    count = spike_w // triangle_w

    # Draw the main red spikes
    for i in range(count):
        x1 = spike_x + i * triangle_w
        x2 = x1 + triangle_w // 2
        x3 = x1 + triangle_w
        y1 = spike_y + spike_h
        y2 = spike_y
        pygame.draw.polygon(screen, spike_color, [(x1, y1), (x2, y2), (x3, y1)])

def reset_player_position():
    global player_vel_x, player_vel_y
    speed = 15
    angle = random.choice([225, 315]) # 225 is Up-Left, 315 is Up-Right
    rad = math.radians(angle)
    player_vel_x = speed * math.cos(rad)
    player_vel_y = speed * math.sin(rad)

def damage_player(amount = 1):
    global hp, invincible_timer
    if invincible_timer <= 0:
        hp -= amount
        invincible_timer = 1000
        reset_player_position()
    else:
        return
    
def shadow_move_x(steps, shadow):
    for i in steps:
        shadow["rect"].x += 1


generate_section(200, 3000)

# Initialize and run the main menu
main_menu = Menu(screen, game_settings)
main_menu.run()

# Start the shadow thread ONLY after the menu is closed (game started)
t = threading.Thread(target=shadow_worker, daemon=True)
t.start()

reset()

running = True

while running:
    clock.tick(FPS)

    # Cycle from -180 (Sunrise) through 0 (Sunset) to 180 (Night)
    if game_settings["daylight_cycle"]:
        if light_angle < 0:
            light_angle += 0.1
        elif light_angle < 180:
            light_angle += 0.5
    else:
        light_angle = -135

    if light_angle > 180:
        light_angle = -180

    # Optimization: Pre-calculate visible objects once per frame
    # Using a slightly wider margin than the screen width to prevent popping
    visible_platforms = [p for p in platforms if p.right > camera_x - 50 and p.left < camera_x + WIDTH + 50]
    visible_enemies = [e for e in enemies if e["rect"].right > camera_x - 50 and e["rect"].left < camera_x + WIDTH + 50]
    visible_coins = [c for c in coins if c.right > camera_x - 50 and c.left < camera_x + WIDTH + 50]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_UP or event.key == pygame.K_w) and on_ground:
                player_vel_y = jump_power
            
    
    keys = pygame.key.get_pressed()


    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player_vel_x += -player_speed / 15 if is_raining else -player_speed / 5
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player_vel_x += player_speed / 15 if is_raining else player_speed / 5


    # 1. Handle Horizontal Movement and Collisions
    player.x += int(player_vel_x)
    if player.x < 0:
        player.x = 0

    for platform in visible_platforms: # Optimization: Only check visible platforms
        if player.colliderect(platform):
            if player_vel_x > 0: # Moving right, hit left side of platform
                player.right = platform.left
            elif player_vel_x < 0: # Moving left, hit right side of platform
                player.left = platform.right

    # 2. Handle Vertical Movement and Collisions
    player_vel_y += gravity
    player.y += player_vel_y
    on_ground = False

    for platform in visible_platforms: # Optimization: Only check visible platforms
        if player.colliderect(platform):
            if player_vel_y > 0: # Falling, hit top of platform
                player.bottom = platform.top
                player_vel_y = 0
                on_ground = True
            elif player_vel_y < 0: # Jumping, hit bottom of platform
                player.top = platform.bottom
                player_vel_y = 0

    # Weather and Rain logic
    if game_settings["weather"]:
        if not is_raining:
            if till_rain:
                till_rain -= 1
            else:
                is_raining = True
                rain_timer = random.randint(1200, 3600)
        else:
            if rain_timer <= 0:
                rain_timer = random.randint(1200, 3600)
            rain_timer -= 1
            if rain_timer <= 0:
                is_raining = False
                till_rain = random.randint(600, 3600)
    else:
        is_raining = False
        rain_drops = []

    if is_raining:
        # Spawn rain particles
        for _ in range(random.randint(5, 20)):
            rain_drops.append([random.randint(0, WIDTH), -20, random.randint(10, 20)])

    # 3. Apply Friction/Damping (Slipperier when raining)
    current_damping = 0.95 if is_raining else 0.85
    if abs(player_vel_x) > 0.1:
        player_vel_x *= current_damping
    else:
        player_vel_x = 0

    for coin in visible_coins: # Optimization: Only check visible coins
        if player.colliderect(coin):
            coins.remove(coin)
            score += 1

    for spike in [s for s in spikes if s.right > camera_x and s.left < camera_x + WIDTH]:
        if player.colliderect(spike):
            damage_player()
            break

    for enemy in enemies:
        enemy["rect"].x += enemy["dir"] * enemy["speed"]
        if enemy["rect"].x <= enemy["left_bound"]:
            enemy["rect"].x = enemy["left_bound"]
            enemy["dir"] = 1
        elif enemy["rect"].x >= enemy["right_bound"]:
            enemy["rect"].x = enemy["right_bound"]
            enemy["dir"] = -1

        if player.colliderect(enemy["rect"]):
            if player_vel_y > 0 and player.bottom - player_vel_y <= enemy["rect"].top:
                enemies.remove(enemy)
                score += 3
                player_vel_y = -10
            else:
                damage_player()
                break

        if invincible_timer > 0:
            invincible_timer -= 1

    camera_x = player.centerx - WIDTH // 2
    if camera_x < min_camera_x:
        camera_x = min_camera_x

    # Restrict player from moving left past the camera edge (into deleted areas)
    if player.left < camera_x:
        player.left = camera_x

    # Optimization: Collect all objects that should cast shadows (Occluders)
    # Using list concatenation is faster than repeated appends and copies.
    occluders = visible_platforms + [player] + [e["rect"] for e in visible_enemies] + \
                [s for s in spikes if s.right > camera_x and s.left < camera_x + WIDTH] + \
                visible_coins

    with state_lock:
        worker_state["occluders"] = occluders
        worker_state["camera_x"] = camera_x
        worker_state["light_angle"] = light_angle
        worker_state["shadows_enabled"] = game_settings["shadows"] and light_angle < 20

    if player.x > world_end_x - 1500:
        generate_section(world_end_x, world_end_x + 2000)
        world_end_x += 2000

        # Cleanup objects far behind the player to save memory and improve performance
        cleanup_threshold = camera_x - 1000
        if cleanup_threshold > min_camera_x:
            min_camera_x = cleanup_threshold

        platforms = [p for p in platforms if p.right > min_camera_x]
        coins = [c for c in coins if c.right > min_camera_x]
        spikes = [s for s in spikes if s.right > min_camera_x]
        enemies = [e for e in enemies if e["rect"].right > min_camera_x]

        # Update the floor to move its start point forward and maintain length
        if platforms:
            platforms[0].x = min_camera_x
            platforms[0].width = world_end_x - min_camera_x


    if invincible_timer > 0:
        current_color = RED
    else:
        current_color = WHITE
        
    # Calculate background color based on sun intensity
    # Intensity is 1.0 at -90 degrees (Noon) and 0.0 at -180/0 degrees (Sunrise/Sunset)
    intensity = max(0, -math.sin(math.radians(light_angle)))
    bg_color = lerp_color(SPACE_COLOR, SKY_COLOR, intensity)
    screen.fill(bg_color)
    
    # Calculate platform brightness based on sun intensity. 
    # We use int() because Pygame colors must be integers, and we simplified the max() logic.
    brightness = max(0.1, min(1, intensity * 1.5))
    platform_color = (int(WHITE[0] * brightness), int(WHITE[1] * brightness), int(WHITE[2] * brightness))
    player_color = (int(current_color[0] * brightness), int(current_color[1] * brightness), int(current_color[2] * brightness))
    spike_color = (int(RED[0] * brightness), int(RED[1] * brightness), int(RED[2] * brightness))
    coin_color = (int(YELLOW[0] * brightness), int(YELLOW[1] * brightness), int(YELLOW[2] * brightness))
    enemy_color = (int(RED[0] * brightness), int(RED[1] * brightness), int(RED[2] * brightness))


    # Draw and update clouds (Parallax effect)
    if game_settings["clouds"]:
        for cloud in clouds:
            cloud["x"] += cloud["speed"]
            # Modulo wrap ensures clouds cycle infinitely across the sky
            rel_x = (cloud["x"] - camera_x * 0.3) % (WIDTH + 400) - 200
            screen.blit(cloud["surf"], (rel_x, cloud["y"]))

    player_draw = pygame.Rect(player.x - camera_x, player.y, player.width, player.height)
    pygame.draw.rect(screen, player_color, player_draw)

    if game_settings["shadows"] and light_angle < 0:
        shadow_surface.fill((0, 0, 0, 0)) # Clear with dtransparency
        with shadow_lock:
            for line_pts in shadow_results:
                if line_pts:
                    # Using a color with alpha (4th value: 160) for semi-transparency.
                    # Width is increased to 25 to ensure overlap with 1-degree ray spacing.
                    pygame.draw.line(shadow_surface, (0, 0, 40, 160), line_pts[0], line_pts[1], width=17)
        
        # Blit the shadow overlay onto the main screen
        screen.blit(shadow_surface, (0, 0))

    for platform in visible_platforms: # Optimization: Use pre-filtered list
        platform_draw = pygame.Rect(platform.x - camera_x, platform.y, platform.width, platform.height)
        pygame.draw.rect(screen, platform_color, platform_draw)





    for spike in spikes:
        draw_spikes(screen, spike, camera_x)
    for coin in coins:
        coin_draw = pygame.Rect(coin.x - camera_x, coin.y, coin.width, coin.height)
        pygame.draw.rect(screen, coin_color, coin_draw)
    for enemy in enemies:
        enemy_draw = pygame.Rect(enemy["rect"].x - camera_x, enemy["rect"].y, enemy["rect"].width, enemy["rect"].height)
        pygame.draw.rect(screen, enemy_color, enemy_draw)

    # Draw and update rain particles
    new_drops = []
    rain_hitboxes = [
        pygame.Rect(platform.x - camera_x, platform.y, platform.width, platform.height)
        for platform in visible_platforms
    ]
    for drop in rain_drops:
        drop[1] += 20
        raindrop_rect = pygame.Rect(drop[0], drop[1], 2, 10)
        if raindrop_rect.collidelist(rain_hitboxes) != -1:
            continue

        if drop[1] < HEIGHT:
            new_drops.append(drop)
            pygame.draw.line(screen, (int(130 * brightness), int(130 * brightness), int(255 * brightness)), (drop[0], drop[1]), (drop[0], drop[1] + drop[2]), 3)
    rain_drops = new_drops





    # Draw UI Text
    score_surf = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_surf, (20, 20))
    hp_surf = font.render(f"HP: {hp}", True, WHITE)
    screen.blit(hp_surf, (20, 50))
    distance_surf = font.render(f"{camera_x // 50}m", True, WHITE)
    screen.blit(distance_surf, (WIDTH // 2  - distance_surf.get_width() // 2, HEIGHT // 2 - 200))
    FPS_surf = font.render(f"FPS: {int(clock.get_fps())}", True, WHITE)
    screen.blit(FPS_surf, (20, 80))


    if hp <= 0:
        
        screen.fill(BLACK)

        game_over_surf = big_font.render("Game Over", True, WHITE)
        screen.blit(game_over_surf, (WIDTH // 2 - game_over_surf.get_width() // 2, HEIGHT // 2 - game_over_surf.get_height() // 2))
        pygame.display.update()
        time.sleep(2)
        reset()
        platforms = []
        clouds = []
        coins = []
        enemies = []
        spikes = []
        platforms.append(pygame.Rect(0, 540, 3000, 65))
        generate_section(200, 3000)
        main_menu.run()

    pygame.display.update()


pygame.quit()
with state_lock:
    worker_state["running"] = False
sys.exit()
        
        
