# Spaceship Sprint
## DI-Software-Gruppe-SJJL // pair1SJ

## Überblick

„**Spaceship Sprint**“ ist ein kleines Arcade-Spiel in Python mit `tkinter`.  
Der Spieler steuert ein **Raumschiff** und muss **Sterne einsammeln** und **Meteoriten ausweichen**.

- **Sterne (good bubbles)** erhöhen den **Score**.  
- **Treibstoff (fuel bubbles)** verlängert die **verbleibende Zeit**.  
- **Meteoriten (bad bubbles)** verringern die **Zeit**.  

- Je **kleiner** ein Stern oder Treibstoff, desto **mehr Punkte oder Zeit** er gibt.  
- Je **größer** ein Meteorit, desto **stärker** wird die Zeit reduziert.  

Das Spiel enthält außerdem **Twinkling Stars** im Hintergrund, **Best Score**, und kleine **Story-Momente**, bei denen der Spieler nach Erreichen bestimmter Punkte **neue Planeten besucht**.

Dieses Projekt wird in einer **gemeinsamen Git-Repository** entwickelt.

---

## Features

### 1. Startseite (Hauptmenü)

Beim Start des Programms wird zuerst eine **Startseite** angezeigt, nicht das Spiel selbst.

**Elemente der Startseite:**

- Titel des Spiels: "**Spaceship Sprint**"  
- Zwei Buttons:
  - **Start Game** – startet das eigentliche Spiel
  - **Exit Game** – beendet das Programm  
- **Beste Punktzahl** wird unten angezeigt

**Technische Umsetzung:**

- Ein `Tk()`-Fenster und Canvas werden wiederverwendet.  
- Eigener **State** für das Menü: `state = "MENU"`  
- **Hover-Effekte** für Buttons

---

### 2. Spielfluss & Steuerung

**Steuerung des Schiffes:**

- Pfeiltasten:
  - `↑` – nach oben
  - `↓` – nach unten
- `Space` oder `P` – **Pause / Fortsetzen**

**Spielzustände (States):**

- `MENU` – Startseite  
- `GAME_RUNNING` – Spiel läuft  
- `GAME_PAUSED` – Spiel pausiert  
- `GAME_OVER` – Endbildschirm  

**Tick-Loop:** Läuft nur, wenn `state == GAME_RUNNING`

---

### 3. Pause-Funktion

Das Spiel kann **pausiert** werden:

- `Space` oder `P`: **Pauses / resumes** das Spiel  
- Während der Pause:
  - **Bubbles bewegen sich nicht**  
  - **Keine neuen Bubbles** werden erstellt  
  - **Zeit läuft nicht weiter**  
- Text "**PAUSED**" wird in der Mitte angezeigt

---

### 4. Sterne, Treibstoff & Meteoriten

- **Sterne (good):** erhöhen den **Score**  
  - **Kleinere Sterne** bringen **mehr Punkte**
- **Treibstoff (fuel):** verlängert die **verbleibende Zeit**  
  - **Kleinere Treibstoff-Bubbles** geben **mehr Zeit**
- **Meteoriten (bad):** verringern die **Zeit**  
  - **Größere Meteoriten** ziehen **mehr Zeit** ab

**Technische Umsetzung:**

- `create_bubble()` entscheidet zufällig die Art der Bubble  
- Bubble-Listen: `bubble_ids`, `bubble_radii`, `bubble_speeds`, `bubble_types`  
- Kollisionsfunktion prüft Typ und wendet **Punkte / Zeitänderungen** an

---

### 5. Zeitkonto & Score

- **Startwert:** 30 Sekunden  
- Anzeige über einen **Time-Bar** und **Score-Text**  
- Zeitänderungen bei Kollisionen abhängig von **Bubble-Typ**, **Größe** und **Geschwindigkeit**  
- **Spielende:** wenn Zeit ≤ 0 → **Game Over**

---

### 6. HUD / Anzeige im Spiel

- **SCORE** – aktuelle Punkte  
- **TIME BAR** – verbleibende Zeit, mit Farbwechsel:
  - Grün > 50%  
  - Gelb 20–50%  
  - Rot < 20%  
- **Sound-Icon** – klickbar zum **An-/Ausschalten** von Musik und Soundeffekten

---

### 7. Hintergrundmusik & Sounds

- **Hintergrundmusik** startet beim Spielstart  
- Soundeffekte bei:
  - **Sternen / Treibstoff** (positiv)  
  - **Meteoriten** (negativ)  
  - **Erreichen eines neuen Planeten** (Applaus)  
  - **Game Over**  
- Sound kann über **Icon** ein- und ausgeschaltet werden

---

### 8. Planeten & Story

- **Story-Momente** nach Punkten: 200, 500, 800, 1500  
- Spieler fliegt zu einem **neuen Planeten**  
- Animation mit **Planet fly-in** und Overlay  
- Buttons für:
  - **Weiter zum nächsten Planeten**  
  - **Zurück zum Menü**

---

### 9. Game Over Screen

- Text: "**GAME OVER**"  
- Anzeige von:
  - **Score**  
  - **Best Score**  
- Buttons:
  - **Back to Menu** – zurück zur Startseite  
  - **Exit Game** – Spiel beenden

---



# -----OLD------- #
# Bubble Popper
## DI-Software-Gruppe-SJJL // pair1SJ


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


