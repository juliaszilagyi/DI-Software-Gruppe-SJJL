import pygame  # Das Herzstück: Die Bibliothek, die Spieleentwicklung ermöglicht (Grafik, Sound, Events)
import random  # Ermöglicht Zufallsereignisse (z.B. wo Rohre erscheinen, welche Farbe sie haben)
import os      # Hilft beim Finden von Dateien auf deinem Computer (egal ob Windows oder Mac)

# =============================================================================
# 1. KONFIGURATION & EINSTELLUNGEN
# =============================================================================

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

PIPE_GAP = 150
DAY_PIPE_SPEED = 5
NIGHT_PIPE_SPEED = 6

SPEED_BOOST = 1
LSD_SPEED_BOOST = 15

GRAVITY = 0.5
BIRD_JUMP = -10

BG_SCROLL_SPEED = 1

# --- Pipes erscheinen erst nach 3 Sekunden ---
PIPE_DELAY_AT_START_MS = 3000

# =============================================================================
# 2. DATEIPFADE (ASSETS)
# =============================================================================

ASSET_DIR = 'assets'

BG_IMG = os.path.join(ASSET_DIR, 'background_day.png')
BG_NIGHT_IMG = os.path.join(ASSET_DIR, 'background_night.png')
GROUND_IMG = os.path.join(ASSET_DIR, 'ground.png')

BIRD_FRAMES = [
    os.path.join(ASSET_DIR, 'bee_frame1.png'),
    os.path.join(ASSET_DIR, 'bee_frame2.png'),
    os.path.join(ASSET_DIR, 'bee_frame3.png')
]

PIPE_FILES = [
    os.path.join(ASSET_DIR, 'pipe.png'),
    os.path.join(ASSET_DIR, 'pipe (2).png'),
    os.path.join(ASSET_DIR, 'pipe (3).png')
]

GAME_OVER_IMG = os.path.join(ASSET_DIR, 'gameover.png')

SHIELD_FILE = os.path.join(ASSET_DIR, 'shield.png')
SPEED_FILE = os.path.join(ASSET_DIR, 'speed.png')
LSD_FILE = os.path.join(ASSET_DIR, 'lsd.png')

MUSIC_FILE = os.path.join(ASSET_DIR, 'soundtrack.mp3')
ZUM1_FILE = os.path.join(ASSET_DIR, 'Zum1.wav')
ZUM2_FILE = os.path.join(ASSET_DIR, 'Zum2.wav')
ZUM3_FILE = os.path.join(ASSET_DIR, 'Zum3.wav')
DEATH_SOUND_FILE = os.path.join(ASSET_DIR, 'deathsound.wav')

PIPE_IMAGES = []
FLAP_SOUNDS = []
DEATH_SOUND = None
POWERUP_IMAGES = {}
PIPE_SPEED = DAY_PIPE_SPEED

PIPE_COLORS = [
    (255, 255, 255),
    (255, 100, 100),
    (100, 255, 100),
    (100, 100, 255),
    (255, 255, 100),
    (255, 100, 255),
    (100, 255, 255),
    (255, 165, 0)
]

# =============================================================================
# 3. PYGAME STARTEN & ASSETS LADEN
# =============================================================================

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bee')
clock = pygame.time.Clock()

def scale_bg_proportional(image_path, target_height):
    img = pygame.image.load(image_path).convert()
    original_width = img.get_width()
    original_height = img.get_height()
    scale_factor = target_height / original_height
    new_width = int(original_width * scale_factor)
    return pygame.transform.scale(img, (new_width, int(target_height)))

try:
    BG = scale_bg_proportional(BG_IMG, SCREEN_HEIGHT)
    BG_NIGHT = scale_bg_proportional(BG_NIGHT_IMG, SCREEN_HEIGHT)

    GROUND = pygame.transform.scale(
        pygame.image.load(GROUND_IMG).convert_alpha(),
        (SCREEN_WIDTH * 2, 100)
    )

    for pipe_file in PIPE_FILES:
        image = pygame.image.load(pipe_file).convert_alpha()
        PIPE_IMAGES.append(image)

    BIRD_IMAGES = [pygame.image.load(f).convert_alpha() for f in BIRD_FRAMES]
    BIRD_IMAGES = [pygame.transform.scale(img, (80, 60)) for img in BIRD_IMAGES]

    if os.path.exists(SHIELD_FILE):
        img = pygame.image.load(SHIELD_FILE).convert_alpha()
        POWERUP_IMAGES['shield'] = pygame.transform.scale(img, (40, 40))

    if os.path.exists(SPEED_FILE):
        img = pygame.image.load(SPEED_FILE).convert_alpha()
        POWERUP_IMAGES['speed'] = pygame.transform.scale(img, (40, 40))

    if os.path.exists(LSD_FILE):
        img = pygame.image.load(LSD_FILE).convert_alpha()
        POWERUP_IMAGES['lsd'] = pygame.transform.scale(img, (40, 40))

except pygame.error as e:
    print(f"Fehler beim Laden von Assets: {e}")
    pygame.quit()
    exit()

try:
    zum_files = [ZUM1_FILE, ZUM2_FILE, ZUM3_FILE]
    for z_file in zum_files:
        if os.path.exists(z_file):
            s = pygame.mixer.Sound(z_file)
            s.set_volume(0.2)
            FLAP_SOUNDS.append(s)

    if os.path.exists(DEATH_SOUND_FILE):
        DEATH_SOUND = pygame.mixer.Sound(DEATH_SOUND_FILE)
        DEATH_SOUND.set_volume(0.5)

except Exception as e:
    print(f"Fehler beim Laden der Soundeffekte: {e}")

music_ready = False
try:
    if os.path.exists(MUSIC_FILE):
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(0.1)
        music_ready = True
    else:
        print(f"WARNUNG: Datei '{MUSIC_FILE}' nicht gefunden.")
except Exception as e:
    print(f"Fehler beim Laden der Musik: {e}")

# =============================================================================
# 4. SPIEL-OBJEKTE (KLASSEN)
# =============================================================================

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type="shield"):
        super().__init__()
        self.type = power_type

        if power_type in POWERUP_IMAGES:
            self.image = POWERUP_IMAGES[power_type]
        else:
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            if power_type == "speed":
                pygame.draw.circle(self.image, (255, 215, 0), (15, 15), 15)
            elif power_type == "lsd":
                pygame.draw.circle(self.image, (255, 255, 255), (15, 15), 15)
                pygame.draw.circle(self.image, (255, 0, 255), (15, 15), 15, 3)
            else:
                pygame.draw.rect(self.image, (0, 255, 0), (5, 5, 20, 20))

        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x -= PIPE_SPEED
        if self.rect.right < 0:
            self.kill()


class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = BIRD_IMAGES
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(80, SCREEN_HEIGHT // 2))
        self.velocity = 0
        self.animation_counter = 0
        self.mask = pygame.mask.from_surface(self.image)

        # --- NEU (verbessert): Konstante Hitbox (unabhängig von Rotation) ---
        # Du kannst hier feinjustieren: kleiner = verzeihender
        self.hitbox_size = (36, 24)
        self.hitbox = pygame.Rect(0, 0, *self.hitbox_size)
        self.hitbox.center = self.rect.center

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
        self.mask = pygame.mask.from_surface(self.image)

        # --- NEU (verbessert): Hitbox konstant halten ---
        self.hitbox.size = self.hitbox_size
        self.hitbox.center = self.rect.center

        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0
            self.hitbox.center = self.rect.center

    def jump(self, sound_on=True):
        self.velocity = BIRD_JUMP
        if sound_on and FLAP_SOUNDS:
            random.choice(FLAP_SOUNDS).play()


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x_pos, height, inverted=False, pipe_image=None):
        super().__init__()
        self.image = pipe_image if pipe_image is not None else PIPE_IMAGES[0]
        self.rect = self.image.get_rect()
        self.inverted = inverted
        self.passed = False

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x_pos, height]
        else:
            self.rect.topleft = [x_pos, height]

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x -= PIPE_SPEED
        if self.rect.right < 0:
            self.kill()


class GameWorld:
    def __init__(self):
        self.bird = Bird()
        self.all_sprites = pygame.sprite.Group()
        self.pipe_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()
        self.all_sprites.add(self.bird)

        self.ground_y = SCREEN_HEIGHT - 100
        self.ground_scroll = 0

        self.bg_width = BG.get_width()
        self.bg_scroll = 0

        self.score = 0
        self.game_active = False
        self.time_since_last_pipe = 0
        self.pipe_frequency = 1500

        self.powerup_active = None
        self.lsd_color_timer = 0

        self.game_time = 0
        self.day_night_cycle = 1800
        self.is_night = False

        # Fonts (mit Fallback)
        try:
            self.font = pygame.font.Font('BoldPixels.ttf', 40)
            self.small_font = pygame.font.Font('BoldPixels.ttf', 26)
        except:
            self.font = pygame.font.SysFont(None, 40)
            self.small_font = pygame.font.SysFont(None, 28)

        self.high_score = 0
        self.pipe_width = PIPE_IMAGES[0].get_width()
        self.game_started = False

        # Pause + Sound Toggle
        self.paused = False
        self.sound_on = True

        # Startzeit fürs Pipe-Delay
        self.run_start_ticks = 0

        # Buttons (Exit + Sound)
        self.exit_button = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 120, 240, 60)
        self.sound_button = pygame.Rect(20, 20, 120, 44)

        self.update_pipe_speed()

    def update_pipe_speed(self):
        global PIPE_SPEED
        difficulty_bonus = (self.score // 15)
        base_speed = (DAY_PIPE_SPEED if not self.is_night else NIGHT_PIPE_SPEED) + difficulty_bonus

        if self.powerup_active:
            if self.powerup_active["type"] == "speed":
                PIPE_SPEED = base_speed + SPEED_BOOST
            elif self.powerup_active["type"] == "lsd":
                PIPE_SPEED = base_speed + LSD_SPEED_BOOST
            else:
                PIPE_SPEED = base_speed
        else:
            PIPE_SPEED = base_speed

    def draw_background(self):
        current_bg = BG_NIGHT if self.is_night else BG

        screen.blit(current_bg, (self.bg_scroll, 0))
        screen.blit(current_bg, (self.bg_scroll + self.bg_width, 0))
        if self.bg_width < SCREEN_WIDTH:
            screen.blit(current_bg, (self.bg_scroll + self.bg_width * 2, 0))

        self.bg_scroll -= BG_SCROLL_SPEED
        if self.bg_scroll <= -self.bg_width:
            self.bg_scroll = 0

        if self.is_night:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(100)
            overlay.fill((20, 20, 40))
            screen.blit(overlay, (0, 0))

    def draw_lsd_effect(self):
        if self.powerup_active and self.powerup_active["type"] == "lsd":
            self.lsd_color_timer += 1
            if self.lsd_color_timer > 5:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                overlay.fill((r, g, b))
                overlay.set_alpha(100)
                screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
                self.lsd_color_timer = 0

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
        overlay_width, overlay_height = 700, 300
        overlay = pygame.Surface((overlay_width, overlay_height))
        overlay.set_alpha(220)
        overlay.fill((0, 0, 0))
        overlay_rect = overlay.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(overlay, overlay_rect)

        self.draw_text("GAME OVER", overlay_rect.top + 60, (255, 0, 0))
        self.draw_text(f"SCORE: {self.score}", overlay_rect.top + 130, (255, 255, 255))
        self.draw_text(f"HIGHSCORE: {self.high_score}", overlay_rect.top + 190, (255, 255, 255))
        self.draw_text("Leertaste = Neustart", overlay_rect.top + 250, (255, 255, 0))

        # Exit-Button im Game-Over-Screen
        pygame.draw.rect(screen, (180, 50, 50), self.exit_button, border_radius=10)
        t = self.small_font.render("EXIT", True, (255, 255, 255))
        screen.blit(t, t.get_rect(center=self.exit_button.center))

    def draw_powerup_timer(self):
        if not self.powerup_active:
            return

        if self.powerup_active["type"] == "lsd":
            color = (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
        elif self.powerup_active["type"] == "shield":
            color = (0, 255, 0)
        else:
            color = (255, 215, 0)

        seconds_left = max(0, self.powerup_active["duration"] / FPS)
        text = f"{self.powerup_active['type'].upper()} {seconds_left:0.1f}s"
        text_surface = self.small_font.render(text, True, color)

        score_text = str(self.score)
        score_surface = self.font.render(score_text, True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))

        text_rect = text_surface.get_rect(midleft=(score_rect.right + 20, score_rect.centery))
        screen.blit(text_surface, text_rect)

    def draw_sound_button(self):
        pygame.draw.rect(screen, (30, 30, 30), self.sound_button, border_radius=10)
        label = "SOUND: ON" if self.sound_on else "SOUND: OFF"
        t = self.small_font.render(label, True, (255, 255, 255))
        screen.blit(t, t.get_rect(center=self.sound_button.center))

    def draw_pause_overlay(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(120)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        self.draw_text("PAUSE", SCREEN_HEIGHT // 2 - 20, (255, 255, 255))
        t = self.small_font.render("P = weiter | ESC = Exit", True, (255, 255, 0))
        screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30)))

    def check_collisions(self):
        hit_ground = self.bird.rect.bottom >= self.ground_y

        # --- VERBESSERT: Bird-Hitbox vs. verkleinerte Pipe-Hitbox ---
        pipe_hits = []
        for p in self.pipe_group:
            # Pipe-Hitbox etwas kleiner (entfernt "unsichtbare Ränder"/Transparenzbereiche)
            pipe_hitbox = p.rect.inflate(-p.rect.width * 0.18, -p.rect.height * 0.02)
            if self.bird.hitbox.colliderect(pipe_hitbox):
                pipe_hits.append(p)

        if self.powerup_active and self.powerup_active["type"] == "lsd":
            return False

        if hit_ground:
            if self.sound_on and DEATH_SOUND:
                DEATH_SOUND.play()
            return True

        if pipe_hits:
            if self.powerup_active and self.powerup_active["type"] == "shield":
                self.powerup_active = None
                self.update_pipe_speed()
                for p in pipe_hits:
                    p.kill()
                return False
            else:
                if self.sound_on and DEATH_SOUND:
                    DEATH_SOUND.play()
                return True

        return False

    def check_powerups(self):
        hit = pygame.sprite.spritecollide(self.bird, self.powerup_group, True)
        if hit:
            ptype = hit[0].type
            duration = 300
            self.powerup_active = {"type": ptype, "duration": duration}
            self.update_pipe_speed()

        if self.powerup_active:
            self.powerup_active["duration"] -= 1
            if self.powerup_active["duration"] <= 0:
                self.powerup_active = None
                self.update_pipe_speed()

    def update_day_night(self):
        self.game_time += 1
        if self.game_time % self.day_night_cycle == 0:
            self.is_night = not self.is_night
            self.update_pipe_speed()

    def generate_pipe(self):
        raw_top_image = random.choice(PIPE_IMAGES).copy()
        raw_bottom_image = random.choice(PIPE_IMAGES).copy()

        top_color = random.choice(PIPE_COLORS)
        top_image = raw_top_image
        top_image.fill(top_color, special_flags=pygame.BLEND_MULT)

        bottom_color = random.choice(PIPE_COLORS)
        bottom_image = raw_bottom_image
        bottom_image.fill(bottom_color, special_flags=pygame.BLEND_MULT)

        self.pipe_width = top_image.get_width()

        min_height = 150
        max_height = self.ground_y - PIPE_GAP - 50
        pipe_height = random.randint(min_height, max_height)

        top_pipe = Pipe(SCREEN_WIDTH, pipe_height, inverted=True, pipe_image=top_image)
        bottom_pipe = Pipe(SCREEN_WIDTH, pipe_height + PIPE_GAP, inverted=False, pipe_image=bottom_image)

        self.pipe_group.add(top_pipe, bottom_pipe)
        self.all_sprites.add(top_pipe, bottom_pipe)

        lsd_active = (self.powerup_active and self.powerup_active["type"] == "lsd")

        if not lsd_active and random.random() < 0.08:
            min_y = SCREEN_HEIGHT // 3
            max_y = 2 * SCREEN_HEIGHT // 3
            pu_y = random.randint(min_y, max_y)
            pu_x = SCREEN_WIDTH + self.pipe_width + 100

            roll = random.random()
            if roll < 0.05:
                pu_type = "lsd"
            elif roll < 0.5:
                pu_type = "shield"
            else:
                pu_type = "speed"

            pu = PowerUp(pu_x, pu_y, pu_type)
            self.powerup_group.add(pu)
            self.all_sprites.add(pu)

    def update_score(self):
        for pipe in self.pipe_group:
            if not pipe.inverted and not pipe.passed:
                if self.bird.rect.left > pipe.rect.right:
                    pipe.passed = True
                    self.score += 1
                    if self.score > self.high_score:
                        self.high_score = self.score
                    self.update_pipe_speed()

    def reset_game(self):
        self.bird = Bird()
        self.all_sprites = pygame.sprite.Group()
        self.pipe_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()
        self.all_sprites.add(self.bird)

        self.score = 0
        self.time_since_last_pipe = 0
        self.powerup_active = None
        self.game_time = 0
        self.is_night = False
        self.paused = False

        # Startzeit für Pipe-Delay setzen
        self.run_start_ticks = pygame.time.get_ticks()

        self.update_pipe_speed()

# =============================================================================
# 5. MAIN GAME LOOP
# =============================================================================

game = GameWorld()
running = True

pygame.time.set_timer(pygame.USEREVENT + 1, game.pipe_frequency)

while running:
    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # Fenster schließen (normal)

        if event.type == pygame.KEYDOWN:
            # ESC beendet das Spiel
            if event.key == pygame.K_ESCAPE:
                running = False

            # Pause (P)
            if event.key == pygame.K_p and game.game_active:
                game.paused = not game.paused

            if event.key == pygame.K_SPACE:
                if game.game_active:
                    if not game.paused:
                        game.bird.jump(sound_on=game.sound_on)
                else:
                    # Neustart / Start
                    if music_ready and game.sound_on:
                        try:
                            pygame.mixer.music.rewind()
                            pygame.mixer.music.play(-1)
                        except:
                            pass

                    game.reset_game()
                    game.game_active = True
                    game.game_started = True

        # Maus-Buttons (Sound Toggle + Exit)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Sound Button immer klickbar
            if game.sound_button.collidepoint((mx, my)):
                game.sound_on = not game.sound_on
                if music_ready:
                    if game.sound_on and game.game_active:
                        try:
                            pygame.mixer.music.play(-1)
                        except:
                            pass
                    else:
                        pygame.mixer.music.stop()

            # Exit nur im Start-/GameOver Screen
            if not game.game_active:
                if game.exit_button.collidepoint((mx, my)):
                    running = False

        # Pipes erst nach 3 Sekunden generieren + nicht während Pause
        if game.game_active and (event.type == pygame.USEREVENT + 1):
            if not game.paused:
                now = pygame.time.get_ticks()
                if (now - game.run_start_ticks) >= PIPE_DELAY_AT_START_MS:
                    game.generate_pipe()

    # --- SPIEL-LOGIK UPDATE ---
    if game.game_active and not game.paused:
        if game.time_since_last_pipe == 0:
            pygame.time.set_timer(pygame.USEREVENT + 1, game.pipe_frequency)
            game.time_since_last_pipe = 1

        game.all_sprites.update()

        if game.check_collisions():
            game.game_active = False
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            if music_ready:
                pygame.mixer.music.stop()

        game.update_score()
        game.check_powerups()
        game.update_day_night()

    # --- ZEICHNEN ---
    game.draw_background()

    if game.game_active:
        game.pipe_group.draw(screen)
        game.powerup_group.draw(screen)
        game.all_sprites.draw(screen)
        game.draw_text(str(game.score), 100, (255, 255, 255))

        if game.powerup_active:
            game.draw_powerup_timer()
            game.draw_lsd_effect()

        # Pause Overlay
        if game.paused:
            game.draw_pause_overlay()

    else:
        if not game.game_started:
            game.draw_text("FLAPPY BEE", SCREEN_HEIGHT // 3, (255, 255, 0))
            game.draw_text("Leertaste = Start", SCREEN_HEIGHT // 2, (255, 255, 255))

            # Exit-Button im Startscreen
            pygame.draw.rect(screen, (180, 50, 50), game.exit_button, border_radius=10)
            t = game.small_font.render("EXIT", True, (255, 255, 255))
            screen.blit(t, t.get_rect(center=game.exit_button.center))
        else:
            game.draw_game_over_screen()

    # Sound Button oben links (immer sichtbar)
    game.draw_sound_button()

    game.draw_ground()

    pygame.display.update()
    clock.tick(FPS)

pygame.quit()

