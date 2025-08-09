import pygame
import time
import math
import random
from utils import scale_image, blit_rotate_center, blit_text_center, create_gradient_surface
pygame.font.init()

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.55)
GREY_CAR = scale_image(pygame.image.load("imgs/grey-car.png"), 0.55)
PURPLE_CAR = scale_image(pygame.image.load("imgs/purple-car.png"), 0.55)
WHITE_CAR = scale_image(pygame.image.load("imgs/white-car.png"), 0.55)

# Car selection data
CARS = {
    "Red": RED_CAR,
    "Green": GREEN_CAR,
    "Grey": GREY_CAR,
    "Purple": PURPLE_CAR,
    "White": WHITE_CAR
}

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

MAIN_FONT = pygame.font.SysFont("comicsans", 25)
TITLE_FONT = pygame.font.SysFont("arial", 40, bold=True)
INFO_FONT = pygame.font.SysFont("arial", 20)

FPS = 60
PATH = [(164, 121), (68, 136), (68, 479), (294, 707), (392, 670), (419, 535),
        (539, 480), (606, 679), (654, 729), (731, 643), (739, 404), (458, 365),
        (417, 273), (688, 253), (732, 136), (665, 76), (350, 76), (287, 163),
        (276, 380), (192, 396), (166, 251)]

class GameInfo():
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img=self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel
        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0

class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (180, 200)

    def __init__(self, max_vel, rotation_vel, car_img=None):
        if car_img:
            self.IMG = car_img
        super().__init__(max_vel, rotation_vel)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration/2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()

class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (150, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)
        #self.draw_points(win)

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi/2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle > 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1


    def move(self):
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_path_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.2


class Particle:
    def __init__(self, x, y, color, vel_x, vel_y, life_time):
        self.x = x
        self.y = y
        self.color = color
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.life_time = life_time
        self.max_life = life_time
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.life_time -= 1
        self.vel_x *= 0.98  # Friction
        self.vel_y *= 0.98

    def draw(self, win):
        if self.life_time > 0:
            alpha = int(255 * (self.life_time / self.max_life))
            color_with_alpha = (*self.color, alpha)
            # Create a surface for alpha blending
            particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surf, color_with_alpha, (self.size, self.size), self.size)
            win.blit(particle_surf, (self.x - self.size, self.y - self.size))

    def is_alive(self):
        return self.life_time > 0


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_exhaust_particles(self, car_x, car_y, car_angle, car_vel):
        if car_vel > 0.5:  # Only add particles when moving
            # Calculate exhaust position behind the car
            radians = math.radians(car_angle + 180)  # Behind the car
            exhaust_x = car_x + math.sin(radians) * 20
            exhaust_y = car_y + math.cos(radians) * 20

            for _ in range(2):
                vel_x = random.uniform(-1, 1) + math.sin(radians) * car_vel * 0.3
                vel_y = random.uniform(-1, 1) + math.cos(radians) * car_vel * 0.3
                color = (100, 100, 100) if random.random() > 0.5 else (80, 80, 80)
                self.particles.append(Particle(exhaust_x, exhaust_y, color, vel_x, vel_y, 30))

    def add_collision_particles(self, x, y):
        for _ in range(10):
            vel_x = random.uniform(-3, 3)
            vel_y = random.uniform(-3, 3)
            color = (255, 255, 0) if random.random() > 0.5 else (255, 200, 0)
            self.particles.append(Particle(x, y, color, vel_x, vel_y, 20))

    def add_speed_particles(self, car_x, car_y, car_angle, car_vel):
        if car_vel > 3:  # Only add speed lines when going fast
            for _ in range(3):
                # Create particles around the car
                offset_x = random.uniform(-15, 15)
                offset_y = random.uniform(-15, 15)
                vel_x = random.uniform(-2, 2)
                vel_y = random.uniform(-2, 2)
                color = (255, 255, 255)
                self.particles.append(Particle(car_x + offset_x, car_y + offset_y, color, vel_x, vel_y, 15))

    def update(self):
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)

    def draw(self, win):
        for particle in self.particles:
            particle.draw(win)



def draw(win, images, player_car, computer_car, game_info, particle_system, animated_bg):
    for img, pos in images:
        win.blit(img, pos)

    # Draw animated background elements
    animated_bg.draw(win)

    # Draw particles behind cars
    particle_system.draw(win)

    # Enhanced UI with gradient background panels
    ui_panel = create_gradient_surface(280, 120, (20, 20, 40), (40, 40, 80))
    ui_panel.set_alpha(200)
    win.blit(ui_panel, (5, HEIGHT - 125))

    # Add border to UI panel
    pygame.draw.rect(win, (100, 150, 255), (5, HEIGHT - 125, 280, 120), 2)

    # Level display with better styling and glow effect
    level_text = INFO_FONT.render(f"LEVEL {game_info.level}", 1, (100, 200, 255))
    win.blit(level_text, (20, HEIGHT - level_text.get_height() - 105))

    # Time display with icon-like prefix
    time_text = INFO_FONT.render(f"⏱ TIME: {game_info.get_level_time()}s", 1, (255, 255, 255))
    win.blit(time_text, (20, HEIGHT - time_text.get_height() - 80))

    # Speed display with color coding and better formatting
    speed = round(player_car.vel, 1)
    speed_color = (255, 255, 255)
    if speed > 3:
        speed_color = (255, 255, 100)  # Yellow for fast
    if speed > 4:
        speed_color = (255, 150, 150)  # Red for very fast

    vel_text = INFO_FONT.render(f"🏎 SPEED: {speed}", 1, speed_color)
    win.blit(vel_text, (20, HEIGHT - vel_text.get_height() - 55))

    # Enhanced speed bar with gradient
    bar_width = 200
    bar_height = 12
    bar_x = 20
    bar_y = HEIGHT - 30

    # Background bar with gradient
    bg_gradient = create_gradient_surface(bar_width, bar_height, (30, 30, 30), (60, 60, 60))
    win.blit(bg_gradient, (bar_x, bar_y))

    # Speed bar fill with dynamic color
    speed_ratio = min(player_car.vel / player_car.max_vel, 1.0)
    fill_width = int(bar_width * speed_ratio)

    if fill_width > 0:
        if speed_ratio < 0.5:
            bar_color1, bar_color2 = (0, 150, 0), (0, 255, 0)
        elif speed_ratio < 0.8:
            bar_color1, bar_color2 = (150, 150, 0), (255, 255, 0)
        else:
            bar_color1, bar_color2 = (150, 0, 0), (255, 0, 0)

        speed_gradient = create_gradient_surface(fill_width, bar_height, bar_color1, bar_color2, vertical=False)
        win.blit(speed_gradient, (bar_x, bar_y))

    # Border for speed bar with glow effect
    pygame.draw.rect(win, (150, 200, 255), (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2), 2)
    pygame.draw.rect(win, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)

    # Minimap
    draw_minimap(win, player_car, computer_car)

    # Performance indicators
    draw_performance_indicators(win, player_car, computer_car, game_info)

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()


def draw_minimap(win, player_car, computer_car):
    """Draw a minimap in the top-right corner"""
    minimap_size = 120
    minimap_x = WIDTH - minimap_size - 20
    minimap_y = 20

    # Minimap background
    minimap_bg = create_gradient_surface(minimap_size, minimap_size, (20, 20, 40), (40, 40, 80))
    minimap_bg.set_alpha(200)
    win.blit(minimap_bg, (minimap_x, minimap_y))

    # Minimap border
    pygame.draw.rect(win, (100, 150, 255), (minimap_x, minimap_y, minimap_size, minimap_size), 2)

    # Scale factor for minimap
    scale_x = minimap_size / WIDTH
    scale_y = minimap_size / HEIGHT

    # Draw track outline on minimap (simplified)
    track_points = [(164, 121), (68, 136), (68, 479), (294, 707), (392, 670), (419, 535),
                   (539, 480), (606, 679), (654, 729), (731, 643), (739, 404), (458, 365),
                   (417, 273), (688, 253), (732, 136), (665, 76), (350, 76), (287, 163)]

    minimap_track_points = []
    for point in track_points:
        mini_x = minimap_x + int(point[0] * scale_x)
        mini_y = minimap_y + int(point[1] * scale_y)
        minimap_track_points.append((mini_x, mini_y))

    if len(minimap_track_points) > 2:
        pygame.draw.lines(win, (100, 100, 100), True, minimap_track_points, 2)

    # Draw finish line on minimap
    finish_mini_x = minimap_x + int(FINISH_POSITION[0] * scale_x)
    finish_mini_y = minimap_y + int(FINISH_POSITION[1] * scale_y)
    pygame.draw.circle(win, (255, 255, 0), (finish_mini_x, finish_mini_y), 3)

    # Draw cars on minimap
    player_mini_x = minimap_x + int(player_car.x * scale_x)
    player_mini_y = minimap_y + int(player_car.y * scale_y)
    pygame.draw.circle(win, (255, 100, 100), (player_mini_x, player_mini_y), 3)

    computer_mini_x = minimap_x + int(computer_car.x * scale_x)
    computer_mini_y = minimap_y + int(computer_car.y * scale_y)
    pygame.draw.circle(win, (100, 255, 100), (computer_mini_x, computer_mini_y), 3)

    # Minimap title
    minimap_title = pygame.font.SysFont("arial", 12).render("MAP", 1, (255, 255, 255))
    win.blit(minimap_title, (minimap_x + 5, minimap_y + 5))


def draw_performance_indicators(win, player_car, computer_car, game_info):
    """Draw additional performance indicators"""
    # Position comparison
    player_distance = calculate_distance_to_finish(player_car)
    computer_distance = calculate_distance_to_finish(computer_car)

    position_text = "LEADING" if player_distance < computer_distance else "BEHIND"
    position_color = (100, 255, 100) if player_distance < computer_distance else (255, 100, 100)

    pos_text = INFO_FONT.render(f"POSITION: {position_text}", 1, position_color)
    win.blit(pos_text, (WIDTH - 250, HEIGHT - 40))

    # Level progress indicator
    progress = min(game_info.level / game_info.LEVELS, 1.0)
    progress_text = INFO_FONT.render(f"PROGRESS: {int(progress * 100)}%", 1, (255, 255, 255))
    win.blit(progress_text, (WIDTH - 250, HEIGHT - 20))


def calculate_distance_to_finish(car):
    """Calculate approximate distance to finish line"""
    return math.sqrt((car.x - FINISH_POSITION[0])**2 + (car.y - FINISH_POSITION[1])**2)


class AnimatedBackground:
    def __init__(self):
        self.time = 0
        self.clouds = []
        self.create_clouds()

    def create_clouds(self):
        """Create animated cloud effects"""
        for _ in range(5):
            cloud = {
                'x': random.randint(-100, WIDTH + 100),
                'y': random.randint(50, 200),
                'speed': random.uniform(0.2, 0.8),
                'size': random.randint(20, 40),
                'alpha': random.randint(30, 80)
            }
            self.clouds.append(cloud)

    def update(self):
        self.time += 1

        # Update clouds
        for cloud in self.clouds:
            cloud['x'] += cloud['speed']
            if cloud['x'] > WIDTH + 100:
                cloud['x'] = -100
                cloud['y'] = random.randint(50, 200)

    def draw(self, win):
        # Draw animated clouds
        for cloud in self.clouds:
            cloud_surface = pygame.Surface((cloud['size'] * 2, cloud['size']), pygame.SRCALPHA)
            pygame.draw.ellipse(cloud_surface, (255, 255, 255, cloud['alpha']),
                              (0, 0, cloud['size'] * 2, cloud['size']))
            win.blit(cloud_surface, (cloud['x'], cloud['y']))

        # Draw animated finish line effect
        self.draw_finish_line_effect(win)

    def draw_finish_line_effect(self, win):
        """Draw animated finish line with checkered pattern"""
        finish_x, finish_y = FINISH_POSITION

        # Animated checkered pattern
        checker_size = 8
        for i in range(8):
            for j in range(4):
                x = finish_x + i * checker_size
                y = finish_y + j * checker_size

                # Animate the checkers
                if (i + j + self.time // 10) % 2 == 0:
                    color = (255, 255, 255)
                else:
                    color = (0, 0, 0)

                pygame.draw.rect(win, color, (x, y, checker_size, checker_size))

        # Glowing border around finish line
        glow_intensity = int(128 + 127 * math.sin(self.time * 0.1))
        glow_color = (255, 255, 0, glow_intensity)

        glow_surface = pygame.Surface((80, 40), pygame.SRCALPHA)
        pygame.draw.rect(glow_surface, glow_color, (0, 0, 80, 40), 3)
        win.blit(glow_surface, (finish_x - 5, finish_y - 5))


class SoundManager:
    """Placeholder sound manager for future sound effects"""
    def __init__(self):
        self.enabled = False  # Set to True when sound files are added

    def play_engine_sound(self, volume):
        if self.enabled:
            # Placeholder for engine sound based on speed
            pass

    def play_collision_sound(self):
        if self.enabled:
            # Placeholder for collision sound
            pass

    def play_finish_sound(self):
        if self.enabled:
            # Placeholder for level complete sound
            pass

    def play_menu_sound(self):
        if self.enabled:
            # Placeholder for menu navigation sound
            pass

def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()
    if not moved:
        player_car.reduce_speed()

def handle_collision(player_car, computer_car, game_info, particle_system):
    collision_occurred = False

    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()
        particle_system.add_collision_particles(player_car.x, player_car.y)
        collision_occurred = True

    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide != None:
        # Enhanced lose screen
        lose_screen(WIN, game_info)
        game_info.reset()
        player_car.reset()
        computer_car.reset()

    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
            particle_system.add_collision_particles(player_car.x, player_car.y)
        else:
            # Enhanced level complete screen
            level_complete_screen(WIN, game_info)
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)

    return collision_occurred


def lose_screen(win, game_info):
    # Create overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((255, 0, 0, 100))  # Red tint
    win.blit(overlay, (0, 0))

    # Main text
    lose_text = TITLE_FONT.render("YOU LOST!", 1, (255, 255, 255))
    text_rect = lose_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))

    # Text shadow
    shadow_text = TITLE_FONT.render("YOU LOST!", 1, (0, 0, 0))
    shadow_rect = shadow_text.get_rect(center=(WIDTH//2 + 3, HEIGHT//2 - 47))

    win.blit(shadow_text, shadow_rect)
    win.blit(lose_text, text_rect)

    # Subtitle
    subtitle = INFO_FONT.render("The computer car reached the finish line first!", 1, (255, 255, 255))
    subtitle_rect = subtitle.get_rect(center=(WIDTH//2, HEIGHT//2 + 10))
    win.blit(subtitle, subtitle_rect)

    # Restart message
    restart_text = INFO_FONT.render("Restarting in 3 seconds...", 1, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
    win.blit(restart_text, restart_rect)

    pygame.display.update()
    pygame.time.wait(3000)


def level_complete_screen(win, game_info):
    # Create overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 255, 0, 100))  # Green tint
    win.blit(overlay, (0, 0))

    # Main text
    complete_text = TITLE_FONT.render("LEVEL COMPLETE!", 1, (255, 255, 255))
    text_rect = complete_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))

    # Text shadow
    shadow_text = TITLE_FONT.render("LEVEL COMPLETE!", 1, (0, 0, 0))
    shadow_rect = shadow_text.get_rect(center=(WIDTH//2 + 3, HEIGHT//2 - 47))

    win.blit(shadow_text, shadow_rect)
    win.blit(complete_text, text_rect)

    # Time display
    time_text = INFO_FONT.render(f"Completed in {game_info.get_level_time()} seconds!", 1, (255, 255, 255))
    time_rect = time_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 10))
    win.blit(time_text, time_rect)

    # Next level message
    if game_info.level < game_info.LEVELS:
        next_text = INFO_FONT.render(f"Preparing Level {game_info.level + 1}...", 1, (255, 255, 255))
    else:
        next_text = INFO_FONT.render("Preparing final challenge...", 1, (255, 255, 255))
    next_rect = next_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
    win.blit(next_text, next_rect)

    pygame.display.update()
    pygame.time.wait(2000)


def car_selection_screen(win):
    """Car selection screen that returns the selected car image"""
    selected_car = 0
    car_names = list(CARS.keys())
    car_images = list(CARS.values())

    selecting = True
    clock = pygame.time.Clock()

    while selecting:
        clock.tick(FPS)

        # Background
        win.fill((20, 20, 40))

        # Title
        title_text = TITLE_FONT.render("SELECT YOUR CAR", 1, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH//2, 100))

        # Title shadow
        shadow_text = TITLE_FONT.render("SELECT YOUR CAR", 1, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(WIDTH//2 + 3, 103))

        win.blit(shadow_text, shadow_rect)
        win.blit(title_text, title_rect)

        # Car display area
        car_display_y = HEIGHT // 2 - 50

        # Display cars
        for i, (name, car_img) in enumerate(zip(car_names, car_images)):
            x_pos = WIDTH // 2 + (i - selected_car) * 150
            y_pos = car_display_y

            # Only draw cars that are visible
            if -100 < x_pos < WIDTH + 100:
                # Scale effect for selected car
                if i == selected_car:
                    scaled_car = pygame.transform.scale(car_img,
                        (int(car_img.get_width() * 1.2), int(car_img.get_height() * 1.2)))
                    # Selection highlight
                    highlight_rect = pygame.Rect(x_pos - 60, y_pos - 60, 120, 120)
                    pygame.draw.rect(win, (100, 200, 255), highlight_rect, 3)
                    pygame.draw.rect(win, (50, 100, 200), highlight_rect, 1)
                else:
                    scaled_car = car_img

                # Draw car
                car_rect = scaled_car.get_rect(center=(x_pos, y_pos))
                win.blit(scaled_car, car_rect)

                # Car name
                name_color = (255, 255, 255) if i == selected_car else (150, 150, 150)
                name_text = INFO_FONT.render(name, 1, name_color)
                name_rect = name_text.get_rect(center=(x_pos, y_pos + 80))
                win.blit(name_text, name_rect)

        # Instructions
        instruction_text = INFO_FONT.render("Use A/D to select, SPACE to confirm", 1, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(WIDTH//2, HEIGHT - 100))
        win.blit(instruction_text, instruction_rect)

        # Navigation arrows
        if selected_car > 0:
            left_arrow = INFO_FONT.render("◀", 1, (255, 255, 255))
            win.blit(left_arrow, (50, car_display_y))

        if selected_car < len(car_names) - 1:
            right_arrow = INFO_FONT.render("▶", 1, (255, 255, 255))
            right_rect = right_arrow.get_rect()
            right_rect.right = WIDTH - 50
            right_rect.centery = car_display_y
            win.blit(right_arrow, right_rect)

        pygame.display.update()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a and selected_car > 0:
                    selected_car -= 1
                elif event.key == pygame.K_d and selected_car < len(car_names) - 1:
                    selected_car += 1
                elif event.key == pygame.K_SPACE:
                    return car_images[selected_car]

    return car_images[selected_car]


# Car selection
selected_car_img = car_selection_screen(WIN)
if selected_car_img is None:
    pygame.quit()
    exit()

run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
player_car = PlayerCar(4.5, 4.5, selected_car_img)
computer_car = ComputerCar(3, 3, PATH)
game_info = GameInfo()
particle_system = ParticleSystem()
animated_bg = AnimatedBackground()
sound_manager = SoundManager()

while run:
    clock.tick(FPS)

    # Update systems
    particle_system.update()
    animated_bg.update()

    # Add exhaust particles for moving cars
    particle_system.add_exhaust_particles(player_car.x, player_car.y, player_car.angle, player_car.vel)
    particle_system.add_exhaust_particles(computer_car.x, computer_car.y, computer_car.angle, computer_car.vel)

    # Add speed particles for fast player car
    particle_system.add_speed_particles(player_car.x, player_car.y, player_car.angle, player_car.vel)

    # Sound effects (placeholder calls)
    sound_manager.play_engine_sound(player_car.vel / player_car.max_vel)

    draw(WIN, images, player_car, computer_car, game_info, particle_system, animated_bg)

    while not game_info.started:
        # Enhanced start screen
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        WIN.blit(overlay, (0, 0))

        title_text = TITLE_FONT.render(f"LEVEL {game_info.level}", 1, (255, 255, 255))
        title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        WIN.blit(title_text, title_rect)

        start_text = INFO_FONT.render("Press any key to START!", 1, (255, 255, 255))
        start_rect = start_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
        WIN.blit(start_text, start_rect)

        # Controls info
        controls_text = INFO_FONT.render("Controls: WASD to move", 1, (200, 200, 200))
        controls_rect = controls_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 60))
        WIN.blit(controls_text, controls_rect)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            if event.type == pygame.KEYDOWN:
                game_info.start_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

        #if event.type == pygame.MOUSEBUTTONDOWN:
            #pos = pygame.mouse.get_pos()
            #computer_car.path.append(pos)


    move_player(player_car)
    computer_car.move()

    collision_occurred = handle_collision(player_car, computer_car, game_info, particle_system)

    if game_info.game_finished():
        # Enhanced win screen
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 215, 0, 150))  # Gold tint
        WIN.blit(overlay, (0, 0))

        win_text = TITLE_FONT.render("CONGRATULATIONS!", 1, (255, 255, 255))
        win_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))

        shadow_text = TITLE_FONT.render("CONGRATULATIONS!", 1, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(WIDTH//2 + 3, HEIGHT//2 - 47))

        WIN.blit(shadow_text, shadow_rect)
        WIN.blit(win_text, win_rect)

        complete_text = INFO_FONT.render("You completed all levels!", 1, (255, 255, 255))
        complete_rect = complete_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 10))
        WIN.blit(complete_text, complete_rect)

        restart_text = INFO_FONT.render("Restarting in 5 seconds...", 1, (255, 255, 255))
        restart_rect = restart_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40))
        WIN.blit(restart_text, restart_rect)

        pygame.display.update()
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()
        computer_car.reset()

pygame.quit()
