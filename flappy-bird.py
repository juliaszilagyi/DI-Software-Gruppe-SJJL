import pygame  # Bibliothek für 2D-Games (Fenster, Grafiken, Events, etc.)
import random  # Für Zufallswerte (z.B. Rohrhöhen, PowerUps)
import os      # Für Dateipfade (plattformunabhängig)

# --- 1. Game Constants / Einstellungen ---

# Fenstergröße: bestimmt die Spielfläche
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800

# Bildwiederholrate: wie oft pro Sekunde Logik + Zeichnen ausgeführt werden
FPS = 60

# Vertikaler Abstand zwischen oberem und unterem Hindernis
# (= Durchfluglücke für die Biene)
PIPE_GAP = 200

# Basisgeschwindigkeiten der Hindernisse (Rohre/Blumen) und des Bodens:
# Tagsüber langsamer, nachts etwas schneller
DAY_PIPE_SPEED = 5
NIGHT_PIPE_SPEED = 6

# Zusätzliche Geschwindigkeit, wenn ein Speed-PowerUp aktiv ist
SPEED_BOOST = 1  # +1 auf die Basisgeschwindigkeit

# Aktuelle Geschwindigkeit (wird im Spielverlauf dynamisch angepasst)
PIPE_SPEED = DAY_PIPE_SPEED

# Stärke der Schwerkraft: bestimmt, wie schnell die Biene nach unten fällt
GRAVITY = 0.5

# Sprungstärke der Biene (negativ = nach oben)
BIRD_JUMP = -10

# --- Asset-Pfade ---

# Ordner, in dem alle Grafiken liegen
ASSET_DIR = 'assets'

# Hintergrundbilder (Tag & Nacht)
BG_IMG = os.path.join(ASSET_DIR, 'background_day.png')
BG_NIGHT_IMG = os.path.join(ASSET_DIR, 'background_night.png')

# Bodenbild
GROUND_IMG = os.path.join(ASSET_DIR, 'ground.png')

# Animationsframes der Biene (Flügelbewegung)
BIRD_FRAMES = [
    os.path.join(ASSET_DIR, 'bee_frame1.png'),
    os.path.join(ASSET_DIR, 'bee_frame2.png'),
    os.path.join(ASSET_DIR, 'bee_frame3.png')
]

# Verschiedene Hindernisbilder (z.B. Blumen/Pipes), aus denen zufällig gewählt wird
PIPE_FILES = [
    os.path.join(ASSET_DIR, 'pipe.png'),
    os.path.join(ASSET_DIR, 'pipe (2).png'),
    os.path.join(ASSET_DIR, 'pipe (3).png')
]

# Optionales Game-Over-Bild (im Code aktuell nicht direkt verwendet)
GAME_OVER_IMG = os.path.join(ASSET_DIR, 'gameover.png')

# Liste, in der später alle geladenen Hindernisbilder gespeichert werden
PIPE_IMAGES = []

# --- 2. Pygame Initialisierung ---

# Startet alle benötigten Pygame-Module (Grafik, Sound, etc.)
pygame.init()

# Erstellt das Spielfenster
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Fenstertitel setzen
pygame.display.set_caption('Flappy Bee')

# Clock-Objekt zur Kontrolle der FPS
clock = pygame.time.Clock()

# --- Laden der Assets (Bilder) ---

try:
    # Hintergrund (Tag) auf Fenstergröße skalieren
    BG = pygame.transform.scale(
        pygame.image.load(BG_IMG).convert(),
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    # Hintergrund (Nacht) auf Fenstergröße skalieren
    BG_NIGHT = pygame.transform.scale(
        pygame.image.load(BG_NIGHT_IMG).convert(),
        (SCREEN_WIDTH, SCREEN_HEIGHT)
    )

    # Bodenbild laden und in der Breite verdoppeln, damit es scrollen kann
    GROUND = pygame.transform.scale(
        pygame.image.load(GROUND_IMG).convert_alpha(),
        (SCREEN_WIDTH * 2, 100)
    )

    # Hindernisbilder (Pipes/Blumen) laden und in die Liste PIPE_IMAGES packen
    for pipe_file in PIPE_FILES:
        image = pygame.image.load(pipe_file).convert_alpha()
        PIPE_IMAGES.append(image)

    # Bienen-Frames laden, mit Transparenz, und auf ein einheitliches Format skalieren
    BIRD_IMAGES = [pygame.image.load(f).convert_alpha() for f in BIRD_FRAMES]
    BIRD_IMAGES = [pygame.transform.scale(img, (80, 60)) for img in BIRD_IMAGES]

except pygame.error as e:
    # Falls ein Laden fehlschlägt (z.B. Pfad falsch, Datei fehlt)
    print(
        f"Fehler beim Laden von Assets. Stelle sicher, dass der Ordner '{ASSET_DIR}' "
        f"existiert und die Dateien vorhanden sind (pipe.png, pipe (2).png, pipe (3).png benötigt)."
    )
    pygame.quit()
    exit()

# --- 3. PowerUp Klasse ---

class PowerUp(pygame.sprite.Sprite):
    """
    Repräsentiert ein PowerUp im Spiel.

    Mögliche Typen:
      - "shield": schützt einmalig vor einer Kollision mit einem Hindernis
      - "speed": erhöht kurzzeitig die Geschwindigkeit des Spiels

    PowerUps bewegen sich wie die Hindernisse von rechts nach links.
    """
    def __init__(self, x, y, power_type="shield"):
        super().__init__()
        self.type = power_type

        # Transparente Oberfläche als Basis für die simple Darstellung
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)

        # Visuelle Unterscheidung:
        # Speed = gelber Kreis, Shield = grünes Rechteck
        if power_type == "speed":
            pygame.draw.circle(self.image, (255, 215, 0), (15, 15), 15)
        else:
            pygame.draw.rect(self.image, (0, 255, 0), (5, 5, 20, 20))

        # Rechteck zur Positionierung (Mittelpunkt bei (x, y))
        self.rect = self.image.get_rect(center=(x, y))
    
    def update(self):
        """
        Bewegung der PowerUps:
        Sie scrollen mit der gleichen Geschwindigkeit wie die Hindernisse von rechts nach links.
        """
        self.rect.x -= PIPE_SPEED

        # Wenn komplett aus dem Bildschirm raus, PowerUp löschen
        if self.rect.right < 0:
            self.kill()

# --- 4. Klassen-Definitionen ---

class Bird(pygame.sprite.Sprite):
    """
    Repräsentiert die Biene, die der Spieler steuert.

    Eigenschaften:
      - vertikale Geschwindigkeit (Schwerkraft + Sprung)
      - Animationsframes (Flügelschlag)
      - Rotation je nach Flugrichtung
      - pixelgenaue Maske für Kollisionserkennung
    """
    def __init__(self):
        super().__init__()
        self.images = BIRD_IMAGES           # Animationsframes
        self.index = 0                      # Aktueller Frame-Index
        self.image = self.images[self.index]
        # Startposition: etwas links, vertikal mittig
        self.rect = self.image.get_rect(center=(80, SCREEN_HEIGHT // 2))
        self.velocity = 0                   # Vertikale Geschwindigkeit
        self.animation_counter = 0          # Zählt Frames für Animation

        # Maske für pixelgenaue Kollisionserkennung
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        """
        Aktualisiert Position, Animation, Rotation und Maske der Biene pro Frame.
        """
        # Schwerkraft anwenden -> Biene fällt nach unten
        self.velocity += GRAVITY
        self.rect.y += int(self.velocity)
        
        # Flügel-Animation: alle 5 Frames den nächsten Frame anzeigen
        self.animation_counter += 1
        if self.animation_counter >= 5:
            self.animation_counter = 0
            self.index = (self.index + 1) % len(self.images)
        
        # Rotationswinkel abhängig von der vertikalen Geschwindigkeit
        # (steigend = nach oben gekippt, fallend = nach unten)
        angle = max(-30, min(90, self.velocity * 3))

        # Aktuellen Bienenframe rotieren
        self.image = pygame.transform.rotate(self.images[self.index], angle * -1)

        # Nach dem Rotieren muss das Rect neu gesetzt werden,
        # damit die Biene ihre Position (Mittelpunkt) beibehält
        self.rect = self.image.get_rect(center=self.rect.center)

        # Maske nach der Rotation neu berechnen (für pixelgenaue Kollision)
        self.mask = pygame.mask.from_surface(self.image)

        # Biene darf nicht über den oberen Bildschirmrand hinaus fliegen
        if self.rect.top < 0:
            self.rect.top = 0
            # Geschwindigkeit oben abbremsen, damit sie nicht "zittert"
            self.velocity = 0

    def jump(self):
        """
        Wird aufgerufen, wenn der Spieler die Leertaste drückt:
        Biene bekommt einen Sprungimpuls nach oben.
        """
        self.velocity = BIRD_JUMP

class Pipe(pygame.sprite.Sprite):
    """
    Repräsentiert ein einzelnes Hindernis (Rohr/Blume).

    Es gibt zwei Varianten:
      - inverted=True: oberes Hindernis (auf den Kopf gestellt)
      - inverted=False: unteres Hindernis

    Je ein oberes und ein unteres bilden zusammen die Lücke, durch die die Biene fliegt.
    """
    def __init__(self, x_pos, height, inverted=False, pipe_image=None):
        super().__init__()

        # Bild des Hindernisses: entweder das übergebene oder das erste aus PIPE_IMAGES
        self.image = pipe_image if pipe_image is not None else PIPE_IMAGES[0]
        self.rect = self.image.get_rect()
        self.inverted = inverted   # Merkt sich, ob das Hindernis oben ist
        self.passed = False        # Für das Scoring: wurde dieses Hindernis schon passiert?

        if inverted:
            # Oberes Hindernis: Bild vertikal spiegeln und mit seiner Unterkante an 'height' ausrichten
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x_pos, height]
        else:
            # Unteres Hindernis: mit seiner Oberkante an 'height' ausrichten
            self.rect.topleft = [x_pos, height]

        # Maske für pixelgenaue Kollision basierend auf dem finalen Bild
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        """
        Bewegt das Hindernis von rechts nach links.
        """
        self.rect.x -= PIPE_SPEED

        # Wenn das Hindernis komplett aus dem Bildschirm verschwunden ist, löschen
        if self.rect.right < 0:
            self.kill()

class GameWorld:
    """
    Die GameWorld verwaltet den gesamten Spielzustand:

      - Biene, Hindernisse, PowerUps, Boden, Hintergrund
      - Score & Highscore
      - Aktives PowerUp (shield/speed)
      - Tag/Nacht-Zyklus
      - Kollisionserkennung & GameOver-Logik
    """
    def __init__(self):
        # Biene erzeugen
        self.bird = Bird()

        # Sprite-Gruppen für einfaches Updaten/Zeichnen
        self.all_sprites = pygame.sprite.Group()
        self.pipe_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()

        # Biene zu den "all_sprites" hinzufügen
        self.all_sprites.add(self.bird)

        # Vertikale Position des Bodens (Oberkante)
        self.ground_y = SCREEN_HEIGHT - 100

        # Offset für den scrollenden Boden
        self.ground_scroll = 0

        # Aktueller Punktestand
        self.score = 0

        # Ist das Spiel gerade aktiv (läuft) oder im Start-/GameOver-Zustand?
        self.game_active = False

        # Hilfsvariable, um den Start des Rohr-Timers zu steuern
        self.time_since_last_pipe = 0

        # Wie oft neue Hindernisse erzeugt werden (in Millisekunden)
        self.pipe_frequency = 1500

        # Aktives PowerUp (None, oder Dict mit {type, duration})
        self.powerup_active = None
        
        # Zeitvariable für Tag/Nacht-Zyklus (in Frames)
        self.game_time = 0

        # Anzahl Frames, nach denen Tag/Nacht wechseln (z.B. ca. 30 Sekunden bei 60 FPS)
        self.day_night_cycle = 1800

        # Gibt an, ob es aktuell Nacht ist
        self.is_night = False

        # Schriftart für alle Texte im Spiel
        self.font = pygame.font.Font('BoldPixels.ttf', 40)

        # Speichert den bisher höchsten erreichten Score
        self.high_score = 0
        
        # Breite eines Hindernisses (aus einem Bild entnommen)
        self.pipe_width = PIPE_IMAGES[0].get_width()

        # Referenzposition für Scoring (hier: rechts außerhalb)
        self.scored_pipe_x = SCREEN_WIDTH + self.pipe_width

        # Wurde das Spiel mindestens einmal gestartet?
        self.game_started = False

        # Anfangsgeschwindigkeit (Tag, kein PowerUp) setzen
        self.update_pipe_speed()

    def update_pipe_speed(self):
        """
        Berechnet die aktuelle Geschwindigkeit PIPE_SPEED abhängig von:
          - Tag oder Nacht
          - aktivem Speed-PowerUp
        Kombinationen:
          - Tag ohne Speed  -> 5
          - Tag mit Speed   -> 6
          - Nacht ohne Speed-> 6
          - Nacht mit Speed -> 7
        """
        global PIPE_SPEED

        # Basisgeschwindigkeit abhängig von Tag/Nacht
        base_speed = DAY_PIPE_SPEED if not self.is_night else NIGHT_PIPE_SPEED

        # Wenn Speed-PowerUp aktiv ist: Basisgeschwindigkeit + SPEED_BOOST
        if self.powerup_active and self.powerup_active["type"] == "speed":
            PIPE_SPEED = base_speed + SPEED_BOOST
        else:
            PIPE_SPEED = base_speed

    def draw_background(self):
        """
        Zeichnet den Hintergrund je nach Tag/Nacht-Zustand.
        Bei Nacht kommt eine leicht transparente dunkle Ebene darüber.
        """
        bg = BG_NIGHT if self.is_night else BG
        screen.blit(bg, (0, 0))

        if self.is_night:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(100)  # Transparenz
            overlay.fill((20, 20, 40))
            screen.blit(overlay, (0, 0))

    def draw_ground(self):
        """
        Zeichnet und scrollt den Boden.
        Durch zwei aneinander gehängte Bodenbilder entsteht ein Loop-Effekt.
        """
        # Zwei Bodenstücke hintereinander zeichnen
        screen.blit(GROUND, (self.ground_scroll, self.ground_y))
        screen.blit(GROUND, (self.ground_scroll + SCREEN_WIDTH * 2, self.ground_y))

        # Boden nach links bewegen
        self.ground_scroll -= PIPE_SPEED

        # Wenn genug nach links gescrollt wurde, wieder zurücksetzen (Loop)
        if self.ground_scroll <= -SCREEN_WIDTH * 2:
            self.ground_scroll = 0

    def draw_text(self, text, y_pos, color=(255, 255, 255)):
        """
        Zeichnet einen Text zentriert auf der X-Achse an einer bestimmten Y-Position.
        Wird für Score, Titel, Anweisungen etc. verwendet.
        """
        text_surface = self.font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_pos))
        screen.blit(text_surface, text_rect)

    def draw_game_over_screen(self):
        """
        Zeichnet das Game-Over-Overlay mit:
          - Game Over Titel
          - aktuellem Score
          - Highscore
          - Hinweis, wie neu gestartet wird
        """
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

    def draw_powerup_timer(self):
        """
        Zeichnet rechts neben dem Score den aktuellen PowerUp-Timer,
        z.B.: "SPEED 3.4s"
        """
        if not self.powerup_active:
            return

        # Farbe abhängig vom PowerUp-Typ
        color = (0, 255, 0) if self.powerup_active["type"] == "shield" else (255, 215, 0)

        # Restdauer in Sekunden (Dauer wird intern in Frames gespeichert)
        seconds_left = self.powerup_active["duration"] / FPS
        if seconds_left < 0:
            seconds_left = 0

        # Text, z.B. "SHIELD 4.5s" oder "SPEED 2.3s"
        text = f"{self.powerup_active['type'].upper()} {seconds_left:0.1f}s"
        text_surface = self.font.render(text, True, color)

        # Position des Scores ermitteln (z.B. bei y=100)
        score_text = str(self.score)
        score_surface = self.font.render(score_text, True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))

        # Timer rechts neben dem Score platzieren
        text_rect = text_surface.get_rect(midleft=(score_rect.right + 20, score_rect.centery))
        screen.blit(text_surface, text_rect)

    def check_collisions(self):
        """
        Kollisionserkennung:

        - Boden:
            Wenn die Unterkante der Biene den Boden berührt oder darunter ist -> sofort Game Over.
            (Schild schützt NICHT vor Boden)
        - Hindernisse (Pipes/Blumen):
            Pixelgenau über Masken:
              - Wenn Schild aktiv: Kollision wird "verbraucht":
                    -> Schild wird deaktiviert
                    -> getroffene Hindernisse werden gelöscht
                    -> KEIN Game Over
              - Wenn kein Schild: Game Over
        """
        # Boden-Kollision: Biene berührt/überschreitet den Boden
        if self.bird.rect.bottom >= self.ground_y:
            return True

        # Pixelgenaue Kollision mit Hindernissen:
        pipe_hits = pygame.sprite.spritecollide(
            self.bird,
            self.pipe_group,
            False,
            pygame.sprite.collide_mask
        )

        if pipe_hits:
            # Wenn ein Schild aktiv ist, fängt es genau eine Kollision ab
            if self.powerup_active and self.powerup_active["type"] == "shield":
                # Schild wird verbraucht
                self.powerup_active = None
                # Geschwindigkeit falls nötig anpassen (falls vorher Speed aktiv war)
                self.update_pipe_speed()

                # Getroffene Hindernisse löschen, damit die Biene nicht direkt
                # im nächsten Frame wieder darin steckt
                for p in pipe_hits:
                    p.kill()

                # Kein Game Over in diesem Frame, Spiel geht weiter
                return False
            else:
                # Kein Schild aktiv: Kollision führt zu Game Over
                return True

        # Keine Kollision mit Boden oder Hindernissen
        return False

    def check_powerups(self):
        """
        Prüft, ob die Biene ein PowerUp berührt.
        - Kollision mit einem PowerUp:
              -> dieses PowerUp wird aktiviert (shield oder speed)
              -> evtl. vorheriges PowerUp wird überschrieben
        - Jede Frame wird die Restdauer heruntergezählt.
        - Wenn das PowerUp abläuft, wird es deaktiviert und die Geschwindigkeit angepasst.
        """
        # Kollision mit PowerUps (rechteckbasiert, reicht hier, da sie klein sind)
        hit = pygame.sprite.spritecollide(self.bird, self.powerup_group, True)
        if hit:
            # Neues PowerUp wird aktiviert
            self.powerup_active = {"type": hit[0].type, "duration": 300}  # ~5 Sekunden bei 60 FPS
            self.update_pipe_speed()
            
        # Wenn ein PowerUp aktiv ist -> Dauer runterzählen
        if self.powerup_active:
            self.powerup_active["duration"] -= 1
            if self.powerup_active["duration"] <= 0:
                # PowerUp abgelaufen
                self.powerup_active = None
                self.update_pipe_speed()

    def update_day_night(self):
        """
        Steuert den Wechsel zwischen Tag und Nacht.
        Alle 'day_night_cycle' Frames wird umgeschaltet (Tag -> Nacht oder umgekehrt),
        und die Geschwindigkeit entsprechend neu berechnet.
        """
        self.game_time += 1

        # Prüfen, ob ein vollständiger Tag/Nacht-Zyklus vorbei ist
        if self.game_time % self.day_night_cycle == 0:
            self.is_night = not self.is_night
            self.update_pipe_speed()

    def generate_pipe(self):
        """
        Erzeugt ein neues Paar aus oberem und unterem Hindernis an der rechten Bildschirmkante.

        Zusätzlich:
        - Mit 8% Wahrscheinlichkeit wird ein PowerUp erzeugt.
        - Das PowerUp soll NICHT mehr in der Lücke zwischen Top/Bottom-Pipe erscheinen,
          sondern HORIZONTAL zwischen zwei Pipe-Paaren:
              -> also etwas RECHTS hinter diesem Rohrpaar (das nächste Paar kommt später nach)
          und seine vertikale Position ist zufällig zwischen oberem Drittel und unterem Drittel
          des Bildschirms.
        """
        # Zufälliges Hindernisbild auswählen
        random_pipe_image = random.choice(PIPE_IMAGES)
        self.pipe_width = random_pipe_image.get_width()
        
        # Höhe des oberen Hindernisses zufällig im erlaubten Bereich
        min_height = 150
        max_height = self.ground_y - PIPE_GAP - 50
        pipe_height = random.randint(min_height, max_height)

        # Oberes (invertiertes) Hindernis
        top_pipe = Pipe(SCREEN_WIDTH, pipe_height, inverted=True, pipe_image=random_pipe_image)
        # Unteres Hindernis (beginnt PIPE_GAP unter dem oberen)
        bottom_pipe = Pipe(SCREEN_WIDTH, pipe_height + PIPE_GAP, inverted=False, pipe_image=random_pipe_image)

        # Beide in die entsprechenden Gruppen einfügen
        self.pipe_group.add(top_pipe, bottom_pipe)
        self.all_sprites.add(top_pipe, bottom_pipe)

        # PowerUp mit 8% Wahrscheinlichkeit erzeugen
        if random.random() < 0.08:
            # Vertikale Position des PowerUps:
            # zufällig zwischen oberem Drittel und unterem Drittel des Bildschirms
            min_y = SCREEN_HEIGHT // 3
            max_y = 2 * SCREEN_HEIGHT // 3
            pu_y = random.randint(min_y, max_y)

            # Typ: zufällig Shield oder Speed
            pu_type = random.choice(["shield", "speed"])

            # Horizontale Position:
            # Wir setzen das PowerUp RECHTS hinter diesem Rohrpaar,
            # damit es "zwischen" diesem und dem nächsten Pipe-Paar liegt.
            # SCREEN_WIDTH = X-Position des aktuellen Rohrpaares
            # + pipe_width/2 + kleiner Abstand → optisch im Zwischenraum
            pu_x = SCREEN_WIDTH + self.pipe_width + 100

            # PowerUp erzeugen und in die Gruppen einfügen
            pu = PowerUp(pu_x, pu_y, pu_type)
            self.powerup_group.add(pu)
            self.all_sprites.add(pu)

        # Referenzposition (optional) für Scoring basierend auf der Rohrbreite
        self.scored_pipe_x = SCREEN_WIDTH + self.pipe_width

    def update_score(self):
        """
        Erhöht den Score, wenn die Biene ein unteres Hindernis vollständig passiert hat.
        """
        for pipe in self.pipe_group:
            # Nur untere Hindernisse zählen (inverted=False) und nur einmal pro Hindernis
            if not pipe.inverted and not pipe.passed:
                # Wenn die linke Kante der Biene rechts von der rechten Kante des Hindernisses ist,
                # wurde das Hindernis erfolgreich passiert
                if self.bird.rect.left > pipe.rect.right:
                    pipe.passed = True
                    self.score += 1

                    # Highscore updaten, falls neuer Rekord erreicht wurde
                    if self.score > self.high_score:
                        self.high_score = self.score

    def reset_game(self):
        """
        Setzt den gesamten Spielzustand zurück.
        Wird aufgerufen, wenn der Spieler nach Game Over neu startet.
        """
        # Biene neu erstellen
        self.bird = Bird()

        # Alle Sprite-Gruppen neu initialisieren
        self.all_sprites = pygame.sprite.Group()
        self.pipe_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()

        # Nur die Biene zunächst hinzufügen
        self.all_sprites.add(self.bird)

        # Score und Timer zurücksetzen
        self.score = 0
        self.time_since_last_pipe = 0

        # Rohrbreite neu setzen (falls unterschiedliche Rohrbilder verwendet werden)
        self.pipe_width = PIPE_IMAGES[0].get_width()
        self.scored_pipe_x = SCREEN_WIDTH + self.pipe_width

        # PowerUp und Tag/Nacht-Zustand zurücksetzen
        self.powerup_active = None
        self.game_time = 0
        self.is_night = False

        # Geschwindigkeit wieder auf Basiszustand setzen (Tag, ohne PowerUp)
        self.update_pipe_speed()

# --- 5. Main Game Loop ---
# Die zentrale Schleife, in der das Spiel läuft, Events verarbeitet und gezeichnet werden.

game = GameWorld()
running = True

# Pygame-Timer:
# Löst alle 'pipe_frequency' Millisekunden ein Event USEREVENT+1 aus (zum Erzeugen neuer Hindernisse)
pygame.time.set_timer(pygame.USEREVENT + 1, game.pipe_frequency)

while running:
    # --- Event-Verarbeitung ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Fenster schließen -> Spiel beenden
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game.game_active:
                    # Wenn das Spiel läuft: Biene springt
                    game.bird.jump()
                else:
                    # Wenn das Spiel noch nicht läuft oder Game Over ist:
                    # Spiel zurücksetzen und neu starten
                    game.reset_game()
                    game.game_active = True
                    game.game_started = True
        
        # Rohr-Erzeugung (über Timer-Event)
        if game.game_active and event.type == pygame.USEREVENT + 1:
            game.generate_pipe()

    # --- Spiel-Logik, wenn das Spiel aktiv ist ---
    if game.game_active:
        # Timer für Pipes beim ersten Start setzen
        if game.time_since_last_pipe == 0:
            pygame.time.set_timer(pygame.USEREVENT + 1, game.pipe_frequency)
            game.time_since_last_pipe = 1

        # Alle Sprites updaten (Biene, Hindernisse, PowerUps)
        game.all_sprites.update()
        
        # Kollisionen prüfen (Boden + Hindernisse)
        if game.check_collisions():
            # Game Over: Spiel stoppen und keine neuen Hindernisse mehr erzeugen
            game.game_active = False
            pygame.time.set_timer(pygame.USEREVENT + 1, 0)
            
        # Score anpassen, falls neue Hindernisse passiert wurden
        game.update_score()

        # PowerUps verwalten (Einsammeln + Ablauf der Dauer)
        game.check_powerups()

        # Tag/Nacht-Zyklus aktualisieren
        game.update_day_night()

    # --- Rendering / Zeichnen ---

    # Hintergrund (Tag/Nacht)
    game.draw_background()

    if game.game_active:
        # Hindernisse, PowerUps und Biene zeichnen
        game.pipe_group.draw(screen)
        game.powerup_group.draw(screen)
        game.all_sprites.draw(screen)

        # Score anzeigen (hier habe ich ihn gleich auf 100 gesetzt, wie ihr es mochtet)
        game.draw_text(str(game.score), 100, (255, 255, 255))
        
        # PowerUp-Timer anzeigen, falls ein PowerUp aktiv ist
        if game.powerup_active:
            game.draw_powerup_timer()

    else:
        # Spiel ist nicht aktiv: Startscreen oder Game-Over-Screen anzeigen
        if not game.game_started:
            # Startbildschirm vor dem ersten Spiel
            game.draw_text("FLAPPY BEE", SCREEN_HEIGHT // 3, (255, 255, 0))
            game.draw_text("Drücke Leertaste zum Start", SCREEN_HEIGHT // 2, (255, 255, 255))
        else:
            # Game-Over-Bildschirm nach einem Crash
            game.draw_game_over_screen()

    # Boden zum Schluss zeichnen, damit er vor den Hindernissen liegt
    game.draw_ground()

    # Alles, was gezeichnet wurde, auf dem Bildschirm aktualisieren
    pygame.display.update()

    # FPS-Limit einhalten
    clock.tick(FPS)

# Pygame sauber beenden, wenn die Schleife verlassen wurde
pygame.quit()
