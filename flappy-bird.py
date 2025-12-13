import pygame  # Das Herzstück: Die Bibliothek, die Spieleentwicklung ermöglicht (Grafik, Sound, Events)
import random  # Ermöglicht Zufallsereignisse (z.B. wo Rohre erscheinen, welche Farbe sie haben)
import os      # Hilft beim Finden von Dateien auf deinem Computer (egal ob Windows oder Mac)

# =============================================================================
# 1. KONFIGURATION & EINSTELLUNGEN
# Hier legen wir die Grundregeln des Spiels fest.
# =============================================================================

SCREEN_WIDTH = 600       # Breite des Spiel-Fensters in Pixeln
SCREEN_HEIGHT = 800      # Höhe des Spiel-Fensters
FPS = 60                 # Frames Per Second: Wie oft das Bild pro Sekunde aktualisiert wird (flüssiges Bild)

PIPE_GAP = 150           # Der vertikale Abstand zwischen dem oberen und unteren Rohr (Durchflugschneise)
DAY_PIPE_SPEED = 5       # Wie schnell sich die Rohre am Tag bewegen
NIGHT_PIPE_SPEED = 6     # Nachts wird das Spiel etwas schneller und schwieriger

# --- PowerUp-Konfiguration ---
SPEED_BOOST = 1          # Wenn man das "Speed"-PowerUp einsammelt: +1 Geschwindigkeit
LSD_SPEED_BOOST = 15     # Wenn man "LSD" einsammelt: Extreme Geschwindigkeit (+15)

# --- Physik der Biene ---
GRAVITY = 0.5            # Schwerkraft: Zieht die Biene jeden Frame um 0.5 Pixel stärker nach unten
BIRD_JUMP = -10          # Sprungkraft: Wenn man drückt, fliegt die Biene 10 Pixel nach oben (Negativ = Oben in Pygame)

# --- Hintergrund ---
BG_SCROLL_SPEED = 1      # Der Hintergrund bewegt sich sehr langsam für einen 3D-Effekt (Parallax)

# =============================================================================
# 2. DATEIPFADE (ASSETS)
# Wir sagen dem Programm, wo die Bilder und Töne liegen.
# =============================================================================

ASSET_DIR = 'assets'     # Der Ordnername, in dem alles liegt

# Bilder laden (os.path.join baut den Pfad korrekt zusammen, z.B. assets/background_day.png)
BG_IMG = os.path.join(ASSET_DIR, 'background_day.png')
BG_NIGHT_IMG = os.path.join(ASSET_DIR, 'background_night.png')
GROUND_IMG = os.path.join(ASSET_DIR, 'ground.png')

# Animations-Bilder für die Biene (Flügelschlag)
BIRD_FRAMES = [
    os.path.join(ASSET_DIR, 'bee_frame1.png'),
    os.path.join(ASSET_DIR, 'bee_frame2.png'),
    os.path.join(ASSET_DIR, 'bee_frame3.png')
]

# Verschiedene Rohr-Grafiken
PIPE_FILES = [
    os.path.join(ASSET_DIR, 'pipe.png'),
    os.path.join(ASSET_DIR, 'pipe (2).png'),
    os.path.join(ASSET_DIR, 'pipe (3).png')
]

GAME_OVER_IMG = os.path.join(ASSET_DIR, 'gameover.png')

# PowerUp Icons
SHIELD_FILE = os.path.join(ASSET_DIR, 'shield.png')
SPEED_FILE = os.path.join(ASSET_DIR, 'speed.png')
LSD_FILE = os.path.join(ASSET_DIR, 'lsd.png')

# Sound-Dateien
MUSIC_FILE = os.path.join(ASSET_DIR, 'soundtrack.mp3')
ZUM1_FILE = os.path.join(ASSET_DIR, 'Zum1.wav')  # Summen 1
ZUM2_FILE = os.path.join(ASSET_DIR, 'Zum2.wav')  # Summen 2
ZUM3_FILE = os.path.join(ASSET_DIR, 'Zum3.wav')  # Summen 3
DEATH_SOUND_FILE = os.path.join(ASSET_DIR, 'deathsound.wav') # Ton beim Verlieren

# Leere Listen/Variablen, die wir später füllen
PIPE_IMAGES = []
FLAP_SOUNDS = [] 
DEATH_SOUND = None 
POWERUP_IMAGES = {}      # Hier speichern wir die geladenen PowerUp-Bilder
PIPE_SPEED = DAY_PIPE_SPEED

# --- Farbpalette für Rohre ---
# Das sind RGB-Werte (Rot, Grün, Blau). Wir mischen diese später über die Rohre,
# um sie zufällig einzufärben, ohne extra Bilder laden zu müssen.
PIPE_COLORS = [
    (255, 255, 255), # Weiß (Originalfarbe bleibt erhalten)
    (255, 100, 100), # Rotstich
    (100, 255, 100), # Grünstich
    (100, 100, 255), # Blaustich
    (255, 255, 100), # Gelb
    (255, 100, 255), # Lila
    (100, 255, 255), # Cyan (Türkis)
    (255, 165, 0)    # Orange
]

# =============================================================================
# 3. PYGAME STARTEN & ASSETS LADEN
# Hier wird das Fenster geöffnet und die Dateien in den Speicher geladen.
# =============================================================================

pygame.init()          # Startet Pygame
pygame.mixer.init()    # Startet das Sound-System

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # Erstellt das Fenster
pygame.display.set_caption('Flappy Bee') # Titel des Fensters
clock = pygame.time.Clock() # Die "Uhr", die sicherstellt, dass das Spiel nicht zu schnell läuft (FPS)

# --- Hilfsfunktion: Hintergrund skalieren ---
# Damit das Bild nicht verzerrt aussieht, skalieren wir es proportional zur Höhe.
def scale_bg_proportional(image_path, target_height):
    img = pygame.image.load(image_path).convert() # Bild laden
    original_width = img.get_width()
    original_height = img.get_height()
    scale_factor = target_height / original_height # Berechnen, wie stark wir vergrößern müssen
    new_width = int(original_width * scale_factor)
    return pygame.transform.scale(img, (new_width, int(target_height)))

try:
    # Hintergründe laden mit unserer Spezial-Funktion
    BG = scale_bg_proportional(BG_IMG, SCREEN_HEIGHT)
    BG_NIGHT = scale_bg_proportional(BG_NIGHT_IMG, SCREEN_HEIGHT)
    
    # Boden laden und auf Bildschirmbreite strecken
    GROUND = pygame.transform.scale(pygame.image.load(GROUND_IMG).convert_alpha(), (SCREEN_WIDTH * 2, 100))

    # Alle Rohr-Varianten laden
    for pipe_file in PIPE_FILES:
        image = pygame.image.load(pipe_file).convert_alpha()
        PIPE_IMAGES.append(image)

    # Bienen-Animation laden und auf richtige Größe bringen
    BIRD_IMAGES = [pygame.image.load(f).convert_alpha() for f in BIRD_FRAMES]
    BIRD_IMAGES = [pygame.transform.scale(img, (80, 60)) for img in BIRD_IMAGES]

    # --- PowerUp Bilder laden ---
    # Wir prüfen, ob die Datei existiert, laden sie und skalieren sie klein (40x40)
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
    exit() # Spiel beenden, wenn Bilder fehlen

# --- Sounds laden ---
try:
    # Flügelschlag-Sounds sammeln
    zum_files = [ZUM1_FILE, ZUM2_FILE, ZUM3_FILE]
    for z_file in zum_files:
        if os.path.exists(z_file):
            s = pygame.mixer.Sound(z_file)
            s.set_volume(0.2) # Leiser machen (20%)
            FLAP_SOUNDS.append(s)
    
    if os.path.exists(DEATH_SOUND_FILE):
        DEATH_SOUND = pygame.mixer.Sound(DEATH_SOUND_FILE)
        DEATH_SOUND.set_volume(0.5)

except Exception as e:
    print(f"Fehler beim Laden der Soundeffekte: {e}")

# --- Musik starten ---
music_ready = False
try:
    if os.path.exists(MUSIC_FILE):
        pygame.mixer.music.load(MUSIC_FILE)
        pygame.mixer.music.set_volume(0.1) # Hintergrundmusik leise
        music_ready = True
    else:
        print(f"WARNUNG: Datei '{MUSIC_FILE}' nicht gefunden.")
except Exception as e:
    print(f"Fehler beim Laden der Musik: {e}")


# =============================================================================
# 4. SPIEL-OBJEKTE (KLASSEN)
# Hier definieren wir, wie sich Biene, Rohre und PowerUps verhalten.
# =============================================================================

# --- PowerUp Klasse ---
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, power_type="shield"):
        super().__init__()
        self.type = power_type
        
        # Bild zuweisen: Wenn wir ein PNG haben, nutzen wir es. Sonst zeichnen wir einen Kreis (Fallback).
        if power_type in POWERUP_IMAGES:
            self.image = POWERUP_IMAGES[power_type]
        else:
            # Fallback (Notlösung falls Bilder fehlen)
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            if power_type == "speed":
                pygame.draw.circle(self.image, (255, 215, 0), (15, 15), 15)
            elif power_type == "lsd":
                pygame.draw.circle(self.image, (255, 255, 255), (15, 15), 15)
                pygame.draw.circle(self.image, (255, 0, 255), (15, 15), 15, 3)
            else:
                pygame.draw.rect(self.image, (0, 255, 0), (5, 5, 20, 20))

        # Position festlegen
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        # Bewegt das PowerUp nach links (auf den Spieler zu)
        self.rect.x -= PIPE_SPEED
        # Wenn es den linken Bildschirmrand verlässt, wird es gelöscht (Speicher sparen)
        if self.rect.right < 0:
            self.kill()

# --- Biene (Spieler) Klasse ---
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.images = BIRD_IMAGES
        self.index = 0 # Welches Bild der Animation gerade gezeigt wird
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(80, SCREEN_HEIGHT // 2)) # Startposition
        self.velocity = 0 # Aktuelle Geschwindigkeit (fallen oder steigen)
        self.animation_counter = 0 # Zählt Frames für die Animation
        self.mask = pygame.mask.from_surface(self.image) # Für pixelgenaue Kollision

    def update(self):
        # Physik anwenden: Schwerkraft
        self.velocity += GRAVITY
        self.rect.y += int(self.velocity)
        
        # Animation: Bilder durchwechseln
        self.animation_counter += 1
        if self.animation_counter >= 5: # Alle 5 Frames Bild wechseln
            self.animation_counter = 0
            self.index = (self.index + 1) % len(self.images)
        
        # Rotation: Biene dreht sich je nach Flugrichtung
        angle = max(-30, min(90, self.velocity * 3))
        self.image = pygame.transform.rotate(self.images[self.index], angle * -1)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image) # Maske aktualisieren nach Drehung

        # Decke berühren verhindern
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0

    def jump(self):
        # Spieler drückt Taste -> Biene fliegt hoch
        self.velocity = BIRD_JUMP
        if FLAP_SOUNDS:
            random.choice(FLAP_SOUNDS).play() # Zufälliges Summen abspielen

# --- Rohr Klasse ---
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x_pos, height, inverted=False, pipe_image=None):
        super().__init__()
        # Standardbild nehmen, falls keins übergeben wurde
        self.image = pipe_image if pipe_image is not None else PIPE_IMAGES[0]
        self.rect = self.image.get_rect()
        self.inverted = inverted
        self.passed = False # Hat der Spieler dieses Rohr schon passiert? (Für Punkte)
        
        # Wenn inverted=True, ist es das obere Rohr (muss gedreht/gespiegelt werden)
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x_pos, height]
        else:
            self.rect.topleft = [x_pos, height]
            
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        # Rohr nach links bewegen
        self.rect.x -= PIPE_SPEED
        # Löschen wenn aus dem Bild
        if self.rect.right < 0:
            self.kill()

# --- GameWorld Klasse (Verwaltet die gesamte Spiellogik) ---
class GameWorld:
    def __init__(self):
        # Erstellt Biene und Gruppen für alle Objekte
        self.bird = Bird()
        self.all_sprites = pygame.sprite.Group()   # Alle Objekte für einfaches Zeichnen
        self.pipe_group = pygame.sprite.Group()    # Nur Rohre (für Kollision)
        self.powerup_group = pygame.sprite.Group() # Nur PowerUps
        self.all_sprites.add(self.bird)
        
        # Boden Variablen
        self.ground_y = SCREEN_HEIGHT - 100
        self.ground_scroll = 0
        
        # Hintergrund Variablen (für das Endlos-Scrollen)
        self.bg_width = BG.get_width()
        self.bg_scroll = 0
        
        # Spielstatus Variablen
        self.score = 0
        self.game_active = False # Spiel läuft erst nach Tastendruck
        self.time_since_last_pipe = 0
        self.pipe_frequency = 1500 # Alle 1500ms (1.5 Sekunden) ein neues Rohr
        
        # PowerUp Management
        self.powerup_active = None # Speichert welches PowerUp gerade aktiv ist
        self.lsd_color_timer = 0   # Timer für das LSD-Farbflackern
        
        # Tag/Nacht Zyklus
        self.game_time = 0
        self.day_night_cycle = 1800 # Alle 30 Sekunden (bei 60 FPS) wechselt Tag/Nacht
        self.is_night = False
        
        # UI & Score
        self.font = pygame.font.Font('BoldPixels.ttf', 40) # Schriftart laden
        self.high_score = 0
        self.pipe_width = PIPE_IMAGES[0].get_width()
        self.game_started = False
        self.update_pipe_speed() # Initiale Geschwindigkeit setzen

    def update_pipe_speed(self):
        """Berechnet die Geschwindigkeit basierend auf Score, Tag/Nacht und PowerUps"""
        global PIPE_SPEED
        
        # --- SCHWIERIGKEITSGRAD ---
        # Alle 15 Punkte wird die Basis-Geschwindigkeit um 1 erhöht
        difficulty_bonus = (self.score // 15)
        
        # Basis Speed berechnen (Nachts schneller + Bonus durch Score)
        base_speed = (DAY_PIPE_SPEED if not self.is_night else NIGHT_PIPE_SPEED) + difficulty_bonus
        
        # PowerUp Einflüsse prüfen
        if self.powerup_active:
            if self.powerup_active["type"] == "speed":
                PIPE_SPEED = base_speed + SPEED_BOOST
            elif self.powerup_active["type"] == "lsd":
                PIPE_SPEED = base_speed + LSD_SPEED_BOOST # MEGA SCHNELL
            else:
                PIPE_SPEED = base_speed
        else:
            PIPE_SPEED = base_speed

    def draw_background(self):
        """Zeichnet den Hintergrund und sorgt für das Endlos-Scrolling (Parallax)"""
        current_bg = BG_NIGHT if self.is_night else BG
        
        # Bild zweimal zeichnen, damit es nahtlos scrollt
        screen.blit(current_bg, (self.bg_scroll, 0))
        screen.blit(current_bg, (self.bg_scroll + self.bg_width, 0))
        if self.bg_width < SCREEN_WIDTH:
             screen.blit(current_bg, (self.bg_scroll + self.bg_width * 2, 0))

        # Hintergrund nach links schieben
        self.bg_scroll -= BG_SCROLL_SPEED
        # Zurücksetzen wenn ein Bild durchgelaufen ist
        if self.bg_scroll <= -self.bg_width:
            self.bg_scroll = 0

        # Nachts ein dunkles Overlay drüberlegen
        if self.is_night:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(100) # Halbtransparent
            overlay.fill((20, 20, 40)) # Dunkelblau
            screen.blit(overlay, (0, 0))

    def draw_lsd_effect(self):
        """Erzeugt wilde Regenbogenfarben wenn LSD aktiv ist"""
        if self.powerup_active and self.powerup_active["type"] == "lsd":
            self.lsd_color_timer += 1
            if self.lsd_color_timer > 5: # Alle 5 Frames Farbe wechseln
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                # Zufällige Farbe generieren
                r = random.randint(0, 255)
                g = random.randint(0, 255)
                b = random.randint(0, 255)
                overlay.fill((r, g, b))
                overlay.set_alpha(100) # Transparent
                # BLEND_ADD macht die Farben leuchtend/grell
                screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_ADD)
                self.lsd_color_timer = 0

    def draw_ground(self):
        """Zeichnet den Boden und bewegt ihn mit der Spielgeschwindigkeit"""
        screen.blit(GROUND, (self.ground_scroll, self.ground_y))
        screen.blit(GROUND, (self.ground_scroll + SCREEN_WIDTH * 2, self.ground_y))
        self.ground_scroll -= PIPE_SPEED
        if self.ground_scroll <= -SCREEN_WIDTH * 2:
            self.ground_scroll = 0

    def draw_text(self, text, y_pos, color=(255, 255, 255)):
        """Hilfsfunktion um Text zentriert auf den Bildschirm zu schreiben"""
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        screen.blit(text_surface, text_rect)

    def draw_game_over_screen(self):
        """Zeichnet das Game Over Fenster"""
        overlay_width, overlay_height = 700, 300
        overlay = pygame.Surface((overlay_width, overlay_height))
        overlay.set_alpha(1000) # Leicht durchsichtig
        overlay.fill((0, 0, 0)) # Schwarz
        overlay_rect = overlay.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(overlay, overlay_rect)
        
        # Statistiken anzeigen
        self.draw_text("GAME OVER", overlay_rect.top + 60, (255, 0, 0))
        self.draw_text(f"SCORE: {self.score}", overlay_rect.top + 130, (255, 255, 255))
        self.draw_text(f"HIGHSCORE: {self.high_score}", overlay_rect.top + 190, (255, 255, 255))
        self.draw_text("Drücke Leertaste für Neustart", overlay_rect.top + 250, (255, 255, 0))

    def draw_powerup_timer(self):
        """Zeigt oben an, wie lange ein PowerUp noch hält"""
        if not self.powerup_active: return
        
        # Farbe je nach PowerUp wählen
        if self.powerup_active["type"] == "lsd":
            color = (random.randint(100,255), random.randint(100,255), random.randint(100,255))
        elif self.powerup_active["type"] == "shield":
            color = (0, 255, 0)
        else:
            color = (255, 215, 0)
            
        # Zeit berechnen
        seconds_left = max(0, self.powerup_active["duration"] / FPS)
        text = f"{self.powerup_active['type'].upper()} {seconds_left:0.1f}s"
        text_surface = self.font.render(text, True, color)
        
        # Positionieren neben dem Score
        score_text = str(self.score)
        score_surface = self.font.render(score_text, True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        text_rect = text_surface.get_rect(midleft=(score_rect.right + 20, score_rect.centery))
        screen.blit(text_surface, text_rect)

    def check_collisions(self):
        """Prüft, ob die Biene gegen etwas geflogen ist"""
        # 1. Boden berührt?
        hit_ground = self.bird.rect.bottom >= self.ground_y
        
        # 2. Rohr berührt? (Pixelgenaue Kollision)
        pipe_hits = pygame.sprite.spritecollide(self.bird, self.pipe_group, False, pygame.sprite.collide_mask)
        
        # SONDERREGEL: Wenn LSD aktiv ist, ist man UNSTERBLICH
        if self.powerup_active and self.powerup_active["type"] == "lsd":
            return False

        if hit_ground:
            if DEATH_SOUND:
                DEATH_SOUND.play()
            return True # Spiel vorbei
            
        if pipe_hits:
            # Wenn Schild aktiv ist -> PowerUp weg, Rohre kaputt, Spiel läuft weiter
            if self.powerup_active and self.powerup_active["type"] == "shield":
                self.powerup_active = None
                self.update_pipe_speed()
                for p in pipe_hits: p.kill() # Rohre zerstören
                return False
            else:
                if DEATH_SOUND:
                    DEATH_SOUND.play()
                return True # Spiel vorbei
        return False

    def check_powerups(self):
        """Prüft, ob die Biene ein PowerUp eingesammelt hat"""
        hit = pygame.sprite.spritecollide(self.bird, self.powerup_group, True) # True = PowerUp verschwindet vom Screen
        if hit:
            ptype = hit[0].type
            duration = 300 # Dauer in Frames (300 Frames / 60 FPS = 5 Sekunden)
            self.powerup_active = {"type": ptype, "duration": duration}
            self.update_pipe_speed() # Geschwindigkeit anpassen
            
        # Timer runterzählen
        if self.powerup_active:
            self.powerup_active["duration"] -= 1
            if self.powerup_active["duration"] <= 0:
                self.powerup_active = None # PowerUp abgelaufen
                self.update_pipe_speed()

    def update_day_night(self):
        """Zählt die Zeit hoch und wechselt Tag/Nacht"""
        self.game_time += 1
        if self.game_time % self.day_night_cycle == 0:
            self.is_night = not self.is_night
            self.update_pipe_speed() # Nachts wird es schneller

    def generate_pipe(self):
        """Erstellt neue Rohre und färbt sie zufällig ein"""
        # Kopien der Originalbilder erstellen (damit wir das Original nicht dauerhaft verändern)
        raw_top_image = random.choice(PIPE_IMAGES).copy()
        raw_bottom_image = random.choice(PIPE_IMAGES).copy()
        
        # --- ZUFÄLLIGE FARBE ANWENDEN ---
        top_color = random.choice(PIPE_COLORS)
        # BLEND_MULT behält Schatten bei und färbt nur drüber
        top_image = raw_top_image
        top_image.fill(top_color, special_flags=pygame.BLEND_MULT)
        
        bottom_color = random.choice(PIPE_COLORS)
        bottom_image = raw_bottom_image
        bottom_image.fill(bottom_color, special_flags=pygame.BLEND_MULT)

        self.pipe_width = top_image.get_width()
        
        # Zufällige Höhe berechnen
        min_height = 150
        max_height = self.ground_y - PIPE_GAP - 50
        pipe_height = random.randint(min_height, max_height)
        
        # Rohre erstellen und zur Gruppe hinzufügen
        top_pipe = Pipe(SCREEN_WIDTH, pipe_height, inverted=True, pipe_image=top_image)
        bottom_pipe = Pipe(SCREEN_WIDTH, pipe_height + PIPE_GAP, inverted=False, pipe_image=bottom_image)
        
        self.pipe_group.add(top_pipe, bottom_pipe)
        self.all_sprites.add(top_pipe, bottom_pipe)
        
        # Prüfen ob LSD aktiv ist (keine PowerUps während LSD)
        lsd_active = (self.powerup_active and self.powerup_active["type"] == "lsd")
        
        # Chance auf ein PowerUp (8% Chance, wenn kein LSD)
        if not lsd_active and random.random() < 0.08:
            min_y = SCREEN_HEIGHT // 3
            max_y = 2 * SCREEN_HEIGHT // 3
            pu_y = random.randint(min_y, max_y)
            pu_x = SCREEN_WIDTH + self.pipe_width + 100
            
            # Welches PowerUp?
            roll = random.random()
            if roll < 0.05: # 5% Chance auf LSD (Sehr selten)
                pu_type = "lsd"
            elif roll < 0.5: # 45% Chance auf Schild
                pu_type = "shield"
            else: # 50% Chance auf Speed
                pu_type = "speed"

            pu = PowerUp(pu_x, pu_y, pu_type)
            self.powerup_group.add(pu)
            self.all_sprites.add(pu)

    def update_score(self):
        """Prüft ob der Spieler ein Rohr passiert hat -> Punkt geben"""
        for pipe in self.pipe_group:
            if not pipe.inverted and not pipe.passed:
                if self.bird.rect.left > pipe.rect.right:
                    pipe.passed = True
                    self.score += 1
                    if self.score > self.high_score: self.high_score = self.score
                    
                    # Bei jedem Punkt Speed prüfen und ggf. erhöhen
                    self.update_pipe_speed()

    def reset_game(self):
        """Setzt alles auf Anfang zurück"""
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
        self.update_pipe_speed()

# =============================================================================
# 5. MAIN GAME LOOP
# Hier läuft das eigentliche Spiel in einer Endlosschleife ab.
# =============================================================================

game = GameWorld() # Spielwelt erstellen
running = True

# Timer starten: Alle X Millisekunden wird ein Event gefeuert, um ein Rohr zu bauen
pygame.time.set_timer(pygame.USEREVENT + 1, game.pipe_frequency)

while running:
    # --- A. EVENT HANDLING (Tastendrücke & Schließen) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False # Fenster schließen
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE: # Leertaste gedrückt
                if game.game_active:
                    game.bird.jump() # Springen
                else:
                    # Spiel Neustart
                    if music_ready:
                        try:
                            pygame.mixer.music.rewind()
                            pygame.mixer.music.play(-1) # Musik loopend abspielen
                        except:
                            pass
                    
                    game.reset_game()
                    game.game_active = True
                    game.game_started = True
        
        # --- B. NEUES ROHR GENERIEREN ---
        # Wenn der Timer abgelaufen ist
        if game.game_active and event.type == pygame.USEREVENT + 1:
            game.generate_pipe()

    # --- C. SPIEL-LOGIK UPDATE ---
    if game.game_active:
        # Sicherheitshalber Timer resetten falls nötig
        if game.time_since_last_pipe == 0:
            pygame.time.set_timer(pygame.USEREVENT + 1, game.pipe_frequency)
            game.time_since_last_pipe = 1
            
        # Alle Positionen aktualisieren (Bewegung)
        game.all_sprites.update()
        
        # Kollisionen prüfen (Tod)
        if game.check_collisions():
            game.game_active = False # Spielstopp
            pygame.time.set_timer(pygame.USEREVENT + 1, 0) # Keine neuen Rohre mehr
            if music_ready:
                pygame.mixer.music.stop()

        # Score, PowerUps und Tag/Nacht updaten
        game.update_score()
        game.check_powerups()
        game.update_day_night()

    # --- D. ZEICHNEN (RENDERING) ---
    # Reihenfolge ist wichtig! Was zuletzt gemalt wird, liegt oben.
    
    game.draw_background() # 1. Hintergrund

    if game.game_active:
        game.pipe_group.draw(screen)     # 2. Rohre
        game.powerup_group.draw(screen)  # 3. PowerUps
        game.all_sprites.draw(screen)    # 4. Biene
        game.draw_text(str(game.score), 100, (255, 255, 255)) # 5. Score
        
        if game.powerup_active:
            game.draw_powerup_timer() # Timer anzeigen
            game.draw_lsd_effect()    # LSD-Effekt (falls aktiv)
    else:
        # Startbildschirm oder Game Over Screen
        if not game.game_started:
            game.draw_text("FLAPPY BEE", SCREEN_HEIGHT // 3, (255, 255, 0))
            game.draw_text("Drücke Leertaste zum Start", SCREEN_HEIGHT // 2, (255, 255, 255))
        else:
            game.draw_game_over_screen()

    game.draw_ground() # Boden ganz oben drauf zeichnen
    
    pygame.display.update() # Das fertig gemalte Bild auf dem Monitor anzeigen
    clock.tick(FPS) # Warten, damit wir nicht schneller als 60 FPS sind

# Pygame beenden, wenn Loop vorbei
pygame.quit()
