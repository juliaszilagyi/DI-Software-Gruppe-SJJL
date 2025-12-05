import pygame
import random
import os

# --- 1. Game Constants / Einstellungen ---
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 800
FPS = 60
PIPE_GAP = 150   # Lücke zwischen oberem und unterem Rohr
PIPE_SPEED = 4
GRAVITY = 0.5
BIRD_JUMP = -10

# Asset-Pfade
ASSET_DIR = 'assets'
BG_IMG = os.path.join(ASSET_DIR, 'background_day.png')
BG_NIGHT_IMG = os.path.join(ASSET_DIR, 'background_night.png')  # G NEU
GROUND_IMG = os.path.join(ASSET_DIR, 'ground.png')
BIRD_FRAMES = [
    os.path.join(ASSET_DIR, 'bee_frame1.png'),
    os.path.join(ASSET_DIR, 'bee_frame2.png'),
    os.path.join(ASSET_DIR, 'bee_frame3.png')
]
PIPE_IMG = os.path.join(ASSET_DIR, 'pipe.png')
GAME_OVER_IMG = os.path.join(ASSET_DIR, 'gameover.png')

# --- 2. Pygame Initialisierung ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bee')
clock = pygame.time.Clock()

# Laden der Assets
try:
    # Hintergründe laden (G)
    BG = pygame.transform.scale(
        pygame.image.load(BG_IMG).convert(),
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )
    BG_NIGHT = pygame.transform.scale(
        pygame.image.load(BG_NIGHT_IMG).convert(),
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )
    GROUND = pygame.transform.scale(
        pygame.image.load(GROUND_IMG).convert_alpha(),
        (SCREEN_WIDTH * 2, 100)
    )
    PIPE_IMAGE = pygame.image.load(PIPE_IMG).convert_alpha()
    BIRD_IMAGES = [pygame.image.load(f).convert_alpha() for f in BIRD_FRAMES]
    BIRD_IMAGES = [pygame.transform.scale(img, (40, 30)) for img in BIRD_IMAGES]
except pygame.error as e:
    print(
        f"Fehler beim Laden von Assets. Stelle sicher, dass der Ordner '{ASSET_DIR}' "
        f"existiert und die Dateien vorhanden sind (background_night.png benötigt)."
    )
    pygame.quit()
    exit()

# --- 3. PowerUp Klasse (NEU) ---
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type="shield"):
        super().__init__()
        self.type = power_type
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        if power_type == "speed":
            pygame.draw.circle(self.image, (255, 215, 0), (15, 15), 15)  # Gold
        else:  # shield
            pygame.draw.rect(self.image, (0, 255, 0), (5, 5, 20, 20))  # Grün
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        self.rect.x -= PIPE_SPEED
        if self.rect.right < 0:
            self.kill()

# --- 4. Klassen-Definitionen ---

class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = BIRD_IMAGES
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(80, SCREEN_HEIGHT // 2))
        self.velocity = 0
        self.animation_counter = 0

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += int(self.velocity)
        self.animation_counter += 1
        if self.animation_counter >= 5:
            self.animation_counter = 0
            self.index = (self.index + 1) % len(self.images)
        angle = max(-30, min(90, self.velocity * 3))
        self.image = pygame.transform.rotate(self.images[self.index], angle * -1)
        self.rect = self.image.get_rect(center=self.rect.center)

    def jump(self):
        self.velocity = BIRD_JUMP

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x_pos, height, inverted=False):
        super().__init__()
        self.image = PIPE_IMAGE
        self.rect = self.image.get_rect()
        self.inverted = inverted
        self.passed = False

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x_pos, height]
        else:
            self.rect.topleft = [x_pos, height]

    def update(self):
        self.rect.x -= PIPE_SPEED
        if self.rect.right < 0:
            self.kill()

class GameWorld:
    def __init__(self):
        self.bird = Bird()
        self.all_sprites = pygame.sprite.Group()
        self.pipe_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()  # A NEU
        self.all_sprites.add(self.bird)

        self.ground_y = SCREEN_HEIGHT - 100
        self.ground_scroll = 0
        self.score = 0
        self.game_active = False
        self.time_since_last_pipe = 0
        self.pipe_frequency = 1500

        # PowerUp-System (A)
        self.powerup_active = None  # {"type": "shield", "duration": 300}
        
        # Day/Night-System (H)
        self.game_time = 0
        self.day_night_cycle = 1800  # 30s
        self.is_night = False

        self.font = pygame.font.Font('freesansbold.ttf', 40)
        self.high_score = 0
        self.scored_pipe_x = SCREEN_WIDTH + 100
        self.game_started = False

    def draw_background(self):
        # I NEU: Dynamischer Hintergrund
        bg = BG_NIGHT if self.is_night else BG
        screen.blit(bg, (0, 0))
        if self.is_night:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(100)
            overlay.fill((20, 20, 40))
            screen.blit(overlay, (0, 0))

    def draw_ground(self):
        screen.blit(GROUND, (self.ground_scroll, self.ground_y))
        screen.blit(GROUND, (self.ground_scroll + SCREEN_WIDTH * 2, self.ground_y))
        self.ground_scroll -= PIPE_SPEED
        if self.ground_scroll <= -SCREEN_WIDTH * 2:
            self.ground_scroll = 0

    def draw_text(self, text, y_pos, color=(255, 255, 255)):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        screen.blit(text_surface, text_rect)

    def draw_game_over_screen(self):
        overlay_width, overlay_height = 500, 300
        overlay = pygame.Surface((overlay_width, overlay_height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        overlay_rect = overlay.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(overlay, overlay_rect)
        self.draw_text("GAME OVER", overlay_rect.top + 60, (255, 0, 0))
        self.draw_text(f"SCORE: {self.score}", overlay_rect.top + 130, (255, 255, 255))
        self.draw_text(f"HIGHSCORE: {self.high_score}", overlay_rect.top + 190, (255, 255, 255))
        self.draw_text("Drücke Leertaste für Neustart", overlay_rect.top + 250, (255, 255, 0))

    def check_collisions(self):
        # D NEU: Schild schützt
        if self.powerup_active and self.powerup_active["type"] == "shield":
            return False
        
        if pygame.sprite.spritecollide(self.bird, self.pipe_group, False):
            return True
        if self.bird.rect.bottom > self.ground_y or self.bird.rect.top < -50:
            return True
        return False

    def check_powerups(self):  # B NEU
        hit = pygame.sprite.spritecollide(self.bird, self.powerup_group, True)
        if hit:
            self.powerup_active = {"type": hit[0].type, "duration": 300}
        
        if self.powerup_active:
            self.powerup_active["duration"] -= 1
            if self.powerup_active["duration"] <= 0:
                self.powerup_active = None

    def update_day_night(self):  # J NEU
        self.game_time += 1
        if self.game_time % self.day_night_cycle == 0:
            self.is_night = not self.is_night
            # Nacht = schwieriger (schnellere Pipes)
            global PIPE_SPEED
            PIPE_SPEED = 5 if self.is_night else 4

    def generate_pipe(self):
        min_height = 150
        max_height = self.ground_y - PIPE_GAP - 50
        pipe_height = random.randint(min_height, max_height)

        top_pipe = Pipe(SCREEN_WIDTH, pipe_height, inverted=True)
        bottom_pipe = Pipe(SCREEN_WIDTH, pipe_height + PIPE_GAP, inverted=False)

        self.pipe_group.add(top_pipe, bottom_pipe)
        self.all_sprites.add(top_pipe, bottom_pipe)

        # C NEU: PowerUp zwischen Rohren (8% Chance)
        if random.random() < 0.08:
            pu_y = pipe_height + PIPE_GAP//2 + random.randint(-50, 50)
            pu_type = random.choice(["shield", "speed"])
            pu = PowerUp(SCREEN_WIDTH + 50, pu_y, pu_type)
            self.powerup_group.add(pu)
            self.all_sprites.add(pu)

        self.scored_pipe_x = SCREEN_WIDTH + PIPE_IMAGE.get_width()

    def update_score(self):
        for pipe in self.pipe_group:
            if not pipe.inverted and not pipe.passed:
                if self.bird.rect.left > pipe.rect.right:
                    pipe.passed = True
                    self.score += 1
                    if self.score > self.high_score:
                        self.high_score = self.score

    def reset_game(self):
        self.bird = Bird()
        self.all_sprites = pygame.sprite.Group()
        self.pipe_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()  # Reset PowerUps
        self.all_sprites.add(self.bird)
        self.score = 0
        self.time_since_last_pipe = 0
        self.scored_pipe_x = SCREEN_WIDTH + 100
        self.powerup_active = None  # Reset PowerUp
        self.game_time = 0  # Reset Day/Night
        self.is_night = False

# --- 5. Main Game Loop ---
game = GameWorld()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game.game_active:
                    game.bird.jump()
                else:
                    game.reset_game()
                    game.game_active = True
                    game.game_started = True
        if game.game_active and event.type == pygame.USEREVENT + 1:
            game.generate_pipe()

    if game.game_active:
        if game.time_since_last_pipe == 0:
            pygame.time.set_timer(pygame.USEREVENT + 1, game.pipe_frequency)
            game.time_since_last_pipe = 1

        game.all_sprites.update()
        
        if game.check_collisions():
            game.game_active = False
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
        
        game.update_score()
        game.check_powerups()  # F
        game.update_day_night()  # J

    # RENDERING
    game.draw_background()

    if game.game_active:
        game.pipe_group.draw(screen)
        game.powerup_group.draw(screen)  # E NEU
        game.all_sprites.draw(screen)
        game.draw_text(str(game.score), 50, (255, 255, 255))  # Weiß für Kontrast
        
        # PowerUp-Indikator
        if game.powerup_active:
            color = (0, 255, 0) if game.powerup_active["type"] == "shield" else (255, 215, 0)
            game.draw_text(game.powerup_active["type"].upper(), 100, color)

    else:
        if not game.game_started:
            game.draw_text("FLAPPY BEE", SCREEN_HEIGHT // 3, (255, 255, 0))
            game.draw_text("Drücke Leertaste zum Start", SCREEN_HEIGHT // 2, (255, 255, 255))
        else:
            game.draw_game_over_screen()

    game.draw_ground()
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
