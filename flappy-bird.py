import pygame
import random
import os

# --- 1. Game Constants / Einstellungen ---
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 700
FPS = 60
PIPE_GAP = 150  # Lücke zwischen oberem und unterem Rohr
PIPE_SPEED = 4
GRAVITY = 0.5
BIRD_JUMP = -10

# Asset-Pfade (MÜSSEN ERSETZT WERDEN)
ASSET_DIR = 'assets'
BG_IMG = os.path.join(ASSET_DIR, 'background_day.png')
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
    # Skalieren der Bilder auf die gewünschte Größe
    BG = pygame.transform.scale(pygame.image.load(BG_IMG).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
    GROUND = pygame.transform.scale(pygame.image.load(GROUND_IMG).convert_alpha(), (SCREEN_WIDTH * 2, 100))
    PIPE_IMAGE = pygame.image.load(PIPE_IMG).convert_alpha()
    BIRD_IMAGES = [pygame.image.load(f).convert_alpha() for f in BIRD_FRAMES]
    # Reduzieren Sie die Größe der Biene, wenn die Bilder zu groß sind
    BIRD_IMAGES = [pygame.transform.scale(img, (40, 30)) for img in BIRD_IMAGES]
except pygame.error as e:
    print(f"Fehler beim Laden von Assets. Stelle sicher, dass der Ordner '{ASSET_DIR}' existiert und die Dateien ({os.path.basename(e.filename)}) vorhanden sind.")
    pygame.quit()
    exit()

# --- 3. Klassen-Definitionen ---

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
        # 3.1. Gravitation
        self.velocity += GRAVITY
        self.rect.y += int(self.velocity)
        
        # 3.2. Animation (Flügelschlag)
        self.animation_counter += 1
        if self.animation_counter >= 5:  # Wechselt den Frame alle 5 Loops
            self.animation_counter = 0
            self.index = (self.index + 1) % len(self.images)
        
        # 3.3. Rotation (Nicken)
        # Rotiert das Bild basierend auf der Geschwindigkeit (Fallwinkel)
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
        
        if inverted:
            # Oberes Rohr
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x_pos, height]
        else:
            # Unteres Rohr
            self.rect.topleft = [x_pos, height]

    def update(self):
        self.rect.x -= PIPE_SPEED
        # Entfernt das Rohr, wenn es außerhalb des Bildschirms ist
        if self.rect.right < 0:
            self.kill()

class GameWorld:
    def __init__(self):
        self.bird = Bird()
        self.all_sprites = pygame.sprite.Group()
        self.pipe_group = pygame.sprite.Group()
        self.all_sprites.add(self.bird)
        
        self.ground_y = SCREEN_HEIGHT - 100
        self.ground_scroll = 0
        self.score = 0
        self.game_active = False
        self.time_since_last_pipe = 0
        self.pipe_frequency = 1500 # Neue Rohre alle 1500ms (1.5 Sekunden)
        
        self.font = pygame.font.Font('freesansbold.ttf', 40)
        self.high_score = 0
        self.scored_pipe_x = SCREEN_WIDTH + 100 # X-Position des nächsten Rohrs, für das Punkte vergeben werden

    def draw_background(self):
        screen.blit(BG, (0, 0))

    def draw_ground(self):
        # Scrollender Boden
        screen.blit(GROUND, (self.ground_scroll, self.ground_y))
        screen.blit(GROUND, (self.ground_scroll + SCREEN_WIDTH * 2, self.ground_y))
        self.ground_scroll -= PIPE_SPEED
        if self.ground_scroll <= -SCREEN_WIDTH * 2:
            self.ground_scroll = 0

    def draw_text(self, text, y_pos, color=(255, 255, 255)):
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        screen.blit(text_surface, text_rect)

    def check_collisions(self):
        # Kollision mit Rohren
        if pygame.sprite.spritecollide(self.bird, self.pipe_group, False):
            return True
        
        # Kollision mit Boden oder Decke
        if self.bird.rect.bottom > self.ground_y or self.bird.rect.top < -50:
            return True
            
        return False
        
    def generate_pipe(self):
        # Zufällige Höhe für die Lücke
        min_height = 150
        max_height = self.ground_y - PIPE_GAP - 50
        pipe_height = random.randint(min_height, max_height)
        
        # Oberes Rohr
        top_pipe = Pipe(SCREEN_WIDTH, pipe_height, inverted=True)
        # Unteres Rohr
        bottom_pipe = Pipe(SCREEN_WIDTH, pipe_height + PIPE_GAP, inverted=False)
        
        self.pipe_group.add(top_pipe, bottom_pipe)
        self.all_sprites.add(top_pipe, bottom_pipe)
        
        # X-Position des nächsten Rohrs für die Punktewertung festlegen
        self.scored_pipe_x = SCREEN_WIDTH + PIPE_IMAGE.get_width() 

    def update_score(self):
        # Überprüfen, ob die Biene durch das Rohr geflogen ist
        if self.pipe_group and self.bird.rect.left > self.pipe_group.sprites()[0].rect.right:
            if self.bird.rect.left > self.scored_pipe_x: # Sicherstellen, dass nur einmal pro Rohrsatz gezählt wird
                self.score += 1
                self.scored_pipe_x = SCREEN_WIDTH + 1000 # Setze auf einen weit entfernten Wert
                if self.score > self.high_score:
                    self.high_score = self.score

    def reset_game(self):
        self.bird = Bird()
        self.all_sprites = pygame.sprite.Group()
        self.pipe_group = pygame.sprite.Group()
        self.all_sprites.add(self.bird)
        self.score = 0
        self.time_since_last_pipe = 0
        self.scored_pipe_x = SCREEN_WIDTH + 100

# --- 4. Main Game Loop ---

game = GameWorld()
running = True

while running:
    # Event-Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game.game_active:
                    game.bird.jump()
                else:
                    # Startet das Spiel, wenn die Leertaste im Start/Game-Over-Screen gedrückt wird
                    game.reset_game()
                    game.game_active = True
        
        # Automatisches Rohr-Generieren
        if game.game_active:
            if event.type == pygame.USEREVENT + 1:
                 game.generate_pipe()

    # --- SPIEL LOGIK ---
    if game.game_active:
        # Rohr-Timer (wird nur einmal nach Spielstart gesetzt)
        if game.time_since_last_pipe == 0:
            pygame.time.set_timer(pygame.USEREVENT + 1, game.pipe_frequency)
            game.time_since_last_pipe = 1 # Setzt einen Wert ungleich Null
            
        game.all_sprites.update()
        
        if game.check_collisions():
            game.game_active = False
            pygame.time.set_timer(pygame.USEREVENT + 1, 0) # Stoppt den Rohr-Timer
        
        game.update_score()
    
    # --- RENDERING ---
    game.draw_background()
    
    if game.game_active:
        game.pipe_group.draw(screen)
        game.all_sprites.draw(screen)
        game.draw_text(str(game.score), 50, (0, 0, 0)) # Aktueller Punktestand
    else:
        # Start-/Game-Over-Screen
        if game.score == 0:
            game.draw_text("FLAPPY BEE", SCREEN_HEIGHT // 3, (255, 255, 0))
            game.draw_text("Drücke Leertaste zum Start", SCREEN_HEIGHT // 2, (255, 255, 255))
        else:
            # Game-Over-Screen
            game.draw_text("GAME OVER", SCREEN_HEIGHT // 4, (255, 0, 0))
            game.draw_text(f"SCORE: {game.score}", SCREEN_HEIGHT // 4 + 60, (255, 255, 255))
            game.draw_text(f"HIGHSCORE: {game.high_score}", SCREEN_HEIGHT // 4 + 120, (255, 255, 255))
            game.draw_text("Drücke Leertaste für Neustart", SCREEN_HEIGHT // 4 + 200, (255, 255, 255))


    game.draw_ground() # Boden wird immer zuletzt gezeichnet, um über Rohren/Vogel zu liegen

    # Update des gesamten Bildschirms
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()