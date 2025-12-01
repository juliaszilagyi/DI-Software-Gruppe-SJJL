
# Bubble Popper
## DI-Software-Gruppe-SJJL // pair1SL


## Überblick

„Bubble Popper“ ist ein kleines Arcade-Spiel in Python mit `tkinter`.  
Der Spieler steuert ein Raumschiff und muss **gute Bubbles einsammeln** und **schlechten Bubbles ausweichen**. Gute Bubbles bringen **Zeit-Gutschriften**, schlechte Bubbles ziehen **Zeit ab**. Läuft das Zeitkonto auf 0, ist das Spiel vorbei.

Dieses Projekt wird in einer **gemeinsamen Git-Repository** entwickelt.


## Geplante Features


### 1. Startseite (Hauptmenü)

Beim Start des Programms wird **nicht sofort das Spiel gestartet**, sondern zuerst eine Startseite angezeigt.

**Elemente der Startseite:**

- Titel des Spiels
- Zwei Buttons / Menüpunkte:
  - **"Start Game"** – startet das eigentliche Spiel
  - **"Exit Game"** – beendet das Programm

**Technische Idee:**

- Verwendung desselben `Tk()`-Fensters und Canvas.
- Ein eigener „State“ für das Hauptmenü (z. B. `state = "MENU"`).
- Bei Klick auf **"Start Game"**:
  - Spielvariablen (Zeitkonto, Bubbles, Score, etc.) werden initialisiert.
  - State wechselt zu `GAME_RUNNING`.
- Bei Klick auf **"Exit Game"**:
  - `window.destroy()` oder `quit()` aufrufen.


### 2. Spielfluss & Steuerung

**Steuerung des Schiffes:**

- Pfeiltasten:
  - `↑` – nach oben
  - `↓` – nach unten
  - Space - Pause/Fortsetzen

**Spielzustände (States):**

- `MENU` – Startseite
- `GAME_RUNNING` – Spiel läuft
- `GAME_PAUSED` – Spiel ist pausiert
- `GAME_OVER` – Endbildschirm

Der Hauptspiel-Loop läuft nur in `GAME_RUNNING`.


### 3. Pause-Funktion

Das Spiel soll **pausiert** werden können.

**Geplantes Verhalten:**

- Leertaste zum Pausieren/Fortsetzen:
  - Wenn `GAME_RUNNING` dann Wechsel zu `GAME_PAUSED`
  - Wenn `GAME_PAUSED` dann Wechsel zurück zu `GAME_RUNNING`
- Im **Pause-Zustand**:
  - Bubbles bewegen sich nicht weiter.
  - Es werden keine neuen Bubbles gespawnt.
  - Die Zeit auf dem Konto läuft nicht weiter.
- Text "PAUSED"` wird in der Mitte des Screens angezeigt.


### 4. Gute & schlechte Bubbles

Es gibt zwei Arten von Bubbles:

1. **Gute Bubbles**
   - Farbe z. B. **grün** oder eine andere klare Farbe.
   - Berührt das Schiff eine gute Bubble:
     - Das Zeitkonto erhöht sich um einen Wert (abhängig von Größe und/oder Geschwindigkeit).
2. **Schlechte Bubbles**
   - Farbe z. B. **rot** oder eine andere klare Farbe.
   - Berührt das Schiff eine schlechte Bubble:
     - Das Zeitkonto verringert sich um einen Wert (abhängig von Größe/Geschwindigkeit).

**Technische Umsetzung:**

- Beim Erstellen einer Bubble (`create_bubble()`):
  - Zufällig entscheiden, ob Bubble gut oder schlecht ist (z. B. 70 % gut, 30 % schlecht).
  - Unterschiedliche Farben für gute/schlechte Bubbles setzen.
  - Liste `bubble_ids`, `bubble_rad`, `bubble_speeds` und `bubble_types`
- In der Kollisionsfunktion:
  - Bei Kollision prüfen, ob `bubble_types[i] == "good"` oder `"bad"`.
  - Entsprechend Zeit hinzufügen oder abziehen.


### 5. Zeit-Konto (Time Account)

Zusätzlich zu einem klassischen Score steht hier vor allem die **Zeit im Fokus**.

**Startbedingungen:**

- Der Spieler startet mit einem **Zeitkonto von 30 Sekunden**.
- Es gibt eine Anzeige auf dem Canvas,
  - `TIME`-Label
  - aktuelle Restzeit in Sekunden

**Verhalten bei Kollision:**

- Für **gute Bubbles**:
  - Zeit **+X Sekunden**  
    Beispiel: `+ (Radius + Speed) / 10` Sekunden
- Für **schlechte Bubbles**:
  - Zeit **−Y Sekunden**  
    Beispiel: `- (Radius + Speed) / 10` Sekunden

**Spielende:**

- Wenn das Zeitkonto ≤ 0 ist:
  - State wechselt auf `GAME_OVER`.
  - Es wird ein Game-Over-Screen angezeigt
- Ein klassischer Score wird zusätzlich angezeigt


### 6. HUD / Anzeige im Spiel

Im laufenden Spiel werden folgende Informationen angezeigt:

- **TIME** – aktuelles Zeitkonto in Sekunden (auf gerundet `int`).
- **SCORE** – Punkte
- Die Anzeige wird in jeder Loop-Iteration über `canvas.itemconfig(...)` aktualisiert.


### 7. Hintergrundmusik

Während des Spiels soll **ein Lied im Hintergrund laufen**.

**Geplantes Verhalten:**

- Musik startet, wenn:
  - Das Spiel vom Hauptmenü aus mit **"Start Game"** begonnen wird.
- Musik stoppt / pausiert, wenn:
  - Das Spiel beendet wird (`Exit Game`)  
  - beim Pausieren des Spiels


### 8. Game Over Screen

Am Ende des Spiels (Zeitkonto ist 0 oder kleiner):

- Text in der Mitte:
  - `"GAME OVER"`
- Anzeige von:
  - Buttons:
    - `"Back to Menu"` – zurück zur Startseite
    - `"Exit Game"` – Spiel beenden


