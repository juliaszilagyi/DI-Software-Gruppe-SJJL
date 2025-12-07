# ---------- DI-Software-Gruppe-SJJL // pair1SL ----------
# ---------- Straub Sarah, SZILÁGYI Júlia ----------

#still to be done: now the meteors (red bubbles are pictures and cant change the size
#also the scoring is now messy, will check with different shapes tomorrow
#

# ---------- main_bubblepopper.py ----------


from tkinter import *
import pygame
from random import randint, random
from math import sqrt

# ---------- Window / Canvas ----------

# Window size
HEIGHT = 500
WIDTH = 800

# Create window
window = Tk()
window.title("Bubble Popper")

# Canvas for drawing
canvas = Canvas(window, width=WIDTH, height=HEIGHT, bg='black')
canvas.pack()

# Starry background
star_ids = []

def create_starry_background(num_stars=150):
    global star_ids
    for _ in range(num_stars):
        x = randint(0, WIDTH)
        y = randint(0, HEIGHT)
        r = randint(1, 2)  # tiny radius for small stars
        star = canvas.create_oval(x-r, y-r, x+r, y+r, fill='white', outline='')
        star_ids.append(star)

# Generate stars once at the beginning
create_starry_background()


# ---------- Game States ----------

MENU = 'MENU'
GAME_RUNNING = 'GAME_RUNNING'
GAME_PAUSED = 'GAME_PAUSED'
GAME_OVER = 'GAME_OVER'

state = MENU

# ---------- Music -----------
pygame.mixer.init()
sound_on = True  # sound starts on

# Load your sounds
sound_green = pygame.mixer.Sound("green_sound.mp3")  # positive bubble
sound_red = pygame.mixer.Sound("red_sound.wav")      # negative bubble
pygame.mixer.music.load("background.ogg")            # background music
pygame.mixer.music.set_volume(0.3)                   # adjust volume (0.0 to 1.0)
sound_game_over = pygame.mixer.Sound("game_over.mp3")# game over sounf


# Start/Stop background music
def start_music():
    pygame.mixer.music.play(-1)  # -1 = loop forever

def stop_music():
    pygame.mixer.music.stop()
    
def toggle_sound():
    global sound_on
    if sound_on:
        pygame.mixer.music.pause()
        sound_on = False
        canvas.itemconfig(sound_btn_text, text="Sound: OFF")
    else:
        pygame.mixer.music.unpause()
        sound_on = True
        canvas.itemconfig(sound_btn_text, text="Sound: ON")

#Images
from PIL import Image, ImageTk

# Load original image
rocket_orig = Image.open("rocket.png")
rocket_resized = rocket_orig.resize((50, 30))  # width, height in pixels
rocket_img = ImageTk.PhotoImage(rocket_resized)

fuel_orig = Image.open("fuel.png")
fuel_resized = fuel_orig.resize((20, 30))
fuel_img = ImageTk.PhotoImage(fuel_resized)

meteor_orig = Image.open("meteorite.png")
meteor_resized = meteor_orig.resize((50, 50))
meteor_img = ImageTk.PhotoImage(meteor_resized)

# ---------- Player's Ship ----------

SHIP_RADIUS = 15
SHIP_SPEED = 20
CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2

# Ship image
ship_body = canvas.create_image(CENTER_X, CENTER_Y, image=rocket_img)

# Collision circle for detecting hits
ship_hitbox = canvas.create_oval(
    CENTER_X - SHIP_RADIUS, CENTER_Y - SHIP_RADIUS,
    CENTER_X + SHIP_RADIUS, CENTER_Y + SHIP_RADIUS,
    outline='black'
)
canvas.itemconfig(ship_hitbox, state=HIDDEN)  # hide hitbox

# Thruster/flame behind the ship
thruster = canvas.create_polygon(
    CENTER_X - 30, CENTER_Y - 5,
    CENTER_X - 30, CENTER_Y + 5,
    CENTER_X - 40, CENTER_Y,
    fill='orange'
)

# ---------- Thruster animation ----------
thruster_flame_state = 1  # 1 = bigger, -1 = smaller

def animate_thruster():
    global thruster_flame_state
    if state == GAME_RUNNING:
        coords = canvas.coords(thruster)
        if thruster_flame_state == 1:
            coords[5] += 3
            thruster_flame_state = -1
        else:
            coords[5] -= 3
            thruster_flame_state = 1
        canvas.coords(thruster, coords)
    window.after(100, animate_thruster)

animate_thruster()

# Hide ship at the beginning
for part in [ship_body, ship_hitbox, thruster]:
    canvas.itemconfig(part, state=HIDDEN)

# ---------- Ship Movement ----------
def move_ship(event):
    if state != GAME_RUNNING:
        return
    dy = -SHIP_SPEED if event.keysym == 'Up' else SHIP_SPEED if event.keysym == 'Down' else 0
    if dy != 0:
        canvas.move(ship_body, 0, dy)
        canvas.move(ship_hitbox, 0, dy)
        canvas.move(thruster, 0, dy)

canvas.bind_all('<Key>', move_ship)

# ---------- Bubbles (as images) ----------
bubble_ids = []
bubble_radii = []
bubble_speeds = []
bubble_types = []  # 'good' or 'bad'

MIN_BUBBLE_R = 15
MAX_BUBBLE_R = 30
SPAWN_OFFSET = 100
BUBBLE_CHANCE = 5  # 1 in 5 each tick
good_chance = 0.3
GOOD_DECREASE_RATE = 0.005

from PIL import Image, ImageTk

def create_bubble():
    global good_chance
    x = WIDTH + SPAWN_OFFSET
    y = randint(0, HEIGHT)

    ty = 'good' if random() < good_chance else 'bad'

    # Decide radius
    r = randint(MIN_BUBBLE_R, MAX_BUBBLE_R)

    if ty == 'good':
        img_orig = fuel_orig  # keep the original PIL.Image
    else:
        img_orig = meteor_orig

    # Resize dynamically
    img_resized = img_orig.resize((r*2, r*2))
    img = ImageTk.PhotoImage(img_resized)

    # Keep reference so Tkinter doesn't garbage collect it
    bubble_images.append(img)

    bubble_id = canvas.create_image(x, y, image=img)
    bubble_ids.append(bubble_id)
    bubble_radii.append(r)
    bubble_speeds.append(randint(3, 3 + r//2))
    bubble_types.append(ty)

    good_chance = max(0.05, good_chance - GOOD_DECREASE_RATE)


def create_bubble():
    global good_chance
    x = WIDTH + SPAWN_OFFSET
    y = randint(0, HEIGHT)

    # Determine type
    ty = 'good' if random() < good_chance else 'bad'
    if ty == 'good':
        img = fuel_img
        r = fuel_img.width() // 2
    else:
        img = meteor_img
        r = meteor_img.width() // 2

    bubble_id = canvas.create_image(x, y, image=img)
    bubble_ids.append(bubble_id)
    bubble_radii.append(r)
    speed = randint(3, 3 + r // 2)
    bubble_speeds.append(speed)
    bubble_types.append(ty)

    good_chance = max(0.05, good_chance - GOOD_DECREASE_RATE)

# Move bubbles left
def move_bubbles():
    for i in range(len(bubble_ids)):
        canvas.move(bubble_ids[i], -bubble_speeds[i], 0)

# Get center coordinates
def get_center(obj_id):
    pos = canvas.coords(obj_id)
    if not pos:
        return -9999, -9999
    x, y = pos[0], pos[1]
    return x, y

# Delete bubble
def delete_bubble(i):
    try:
        canvas.delete(bubble_ids[i])
    except:
        pass
    del bubble_radii[i]
    del bubble_speeds[i]
    del bubble_types[i]
    del bubble_ids[i]

# Remove off-screen bubbles
def cleanup_bubbles():
    for i in range(len(bubble_ids)-1, -1, -1):
        x, y = get_center(bubble_ids[i])
        if x < -SPAWN_OFFSET:
            delete_bubble(i)

# Distance between objects
def distance(id1, id2):
    x1, y1 = get_center(id1)
    x2, y2 = get_center(id2)
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)


# ---------- HUD ----------

canvas.create_text(50, 30, text='TIME', fill='white')
canvas.create_text(150, 30, text='SCORE', fill='white')

time_text = canvas.create_text(50, 50, fill='white')
score_text = canvas.create_text(150, 50, fill='white')

# Sound button rectangle
sound_btn_rect = canvas.create_rectangle(WIDTH - 130, 20, WIDTH - 20, 50, fill='gray20', outline='white')
sound_btn_text = canvas.create_text(WIDTH - 75, 35, text="Sound: ON", fill='white', font=('Helvetica', 12))

# Bind clicks
canvas.tag_bind(sound_btn_rect, '<Button-1>', lambda e: toggle_sound())
canvas.tag_bind(sound_btn_text, '<Button-1>', lambda e: toggle_sound())


# Hide the HUD at the start
canvas.itemconfig(time_text, state=HIDDEN)
canvas.itemconfig(score_text, state=HIDDEN)

def update_score_display(score):
    canvas.itemconfig(score_text, text=str(score))

def update_time_display(time_left):
    canvas.itemconfig(time_text, text=str(int(time_left)))


# ---------- Time/Score management ----------

start_time_account = 30.0  # seconds initial
time_account = start_time_account
score = 0


# ---------- Collision handling (affects time_account and score) ----------

def check_collisions_and_apply():
    global time_account, score
    # iterate backwards to safely delete bubbles while looping
    for i in range(len(bubble_ids) - 1, -1, -1):
        # calculate distance between ship and bubble
        if distance(ship_hitbox, bubble_ids[i]) < (SHIP_RADIUS + bubble_radii[i]):
            r = bubble_radii[i]
            s = bubble_speeds[i]
            # time change based on radius + speed
            seconds_change = (r + s) / 10.0

            if bubble_types[i] == 'good':
                time_account += seconds_change
                score += int(r + s)  # add points proportional to size + speed
                if sound_on:
                    sound_green.play()  # play positive sound
            else:
                time_account -= seconds_change
                # Deduct points for bad bubble, proportional to size + speed, keep score non-negative
                score = max(0, score - int((r + s) / 2))
                if sound_on:
                    sound_red.play()    # play negative sound

            # delete bubble after collision
            delete_bubble(i)

    # ensure time doesn't go negative (optional, keeps display clean)
    if time_account < 0:
        time_account = 0
            

# ---------- Menu / Buttons / Overlays ----------
menu_items = []
pause_overlay = None
pause_bg = None
game_over_items = []

def clear_menu():
    global menu_items
    for item in menu_items:
        canvas.delete(item)
    menu_items = []

def show_menu():
    global menu_items, state
    state = MENU
    clear_menu()

    # Gray background rectangle for menu
    rect_width = 500
    rect_height = 350
    menu_bg = canvas.create_rectangle(
        CENTER_X - rect_width // 2,
        CENTER_Y - rect_height // 2,
        CENTER_X + rect_width // 2,
        CENTER_Y + rect_height // 2,
        fill='gray30',
        outline=''
    )

    # Title
    title = canvas.create_text(CENTER_X, 120, text='Bubble Popper', fill='white', font=('Helvetica', 40, 'bold'))

    # Start button
    btn_x = CENTER_X
    start_btn = canvas.create_rectangle(btn_x - 100, 200, btn_x + 100, 250, fill='gray20', outline='white')
    start_txt = canvas.create_text(btn_x, 225, text='Start Game', fill='white', font=('Helvetica', 16))

    # Exit button
    exit_btn = canvas.create_rectangle(btn_x - 100, 270, btn_x + 100, 320, fill='gray20', outline='white')
    exit_txt = canvas.create_text(btn_x, 295, text='Exit Game', fill='white', font=('Helvetica', 16))

    # Include all items in menu_items so they can be cleared
    menu_items = [menu_bg, title, start_btn, start_txt, exit_btn, exit_txt]

    # Bind clicks
    canvas.tag_bind(start_btn, '<Button-1>', lambda e: start_game())
    canvas.tag_bind(start_txt, '<Button-1>', lambda e: start_game())
    canvas.tag_bind(exit_btn, '<Button-1>', lambda e: exit_game())
    canvas.tag_bind(exit_txt, '<Button-1>', lambda e: exit_game())


def show_pause_overlay():
    global pause_overlay, pause_bg
    if pause_overlay is not None:
        return

    # Gray background rectangle
    rect_width = 500
    rect_height = 350
    pause_bg = canvas.create_rectangle(
        CENTER_X - rect_width // 2,
        CENTER_Y - rect_height // 2,
        CENTER_X + rect_width // 2,
        CENTER_Y + rect_height // 2,
        fill='gray30',
        stipple='gray12',
        outline=''
    )

    # PAUSED text
    pause_overlay = canvas.create_text(CENTER_X, CENTER_Y, text='PAUSED', fill='yellow', font=('Helvetica', 40, 'bold'))


def hide_pause_overlay():
    global pause_overlay, pause_bg
    if pause_overlay:
        canvas.delete(pause_overlay)
        pause_overlay = None
    if pause_bg:
        canvas.delete(pause_bg)
        pause_bg = None

def show_game_over():
    global game_over_items, state
    state = GAME_OVER
    
    # Clear previous game over items
    clear_game_over()
    
    # play game over sound
    stop_music()
    if sound_on:
        sound_game_over.play()
        game_over_sound_playing = True
    else:
        game_over_sound_playing = False
    
    # Add gray transparent background rectangle
    rect_width = 500
    rect_height = 350
    rect = canvas.create_rectangle(
        CENTER_X - rect_width // 2,
        CENTER_Y - rect_height // 2,
        CENTER_X + rect_width // 2,
        CENTER_Y + rect_height // 2,
        fill='gray30',
        stipple='gray12',
        outline=''
    )
    
    # Game Over Text
    txt = canvas.create_text(CENTER_X, CENTER_Y - 40, text='GAME OVER', fill='white', font=('Helvetica', 40, 'bold'))
    score_txt = canvas.create_text(CENTER_X, CENTER_Y + 10, text=f'SCORE: {score}', fill='white', font=('Helvetica', 20))
    
    # Buttons
    back_btn = canvas.create_rectangle(CENTER_X - 90, CENTER_Y + 50, CENTER_X + 90, CENTER_Y + 90, fill='gray20', outline='white')
    back_txt = canvas.create_text(CENTER_X, CENTER_Y + 70, text='Back to Menu', fill='white')
    exit_btn = canvas.create_rectangle(CENTER_X - 90, CENTER_Y + 100, CENTER_X + 90, CENTER_Y + 140, fill='gray20', outline='white')
    exit_txt = canvas.create_text(CENTER_X, CENTER_Y + 120, text='Exit Game', fill='white')

    # Add all items to list
    game_over_items = [rect, txt, score_txt, back_btn, back_txt, exit_btn, exit_txt]
    
    # Bind clicks
    canvas.tag_bind(back_btn, '<Button-1>', lambda e: back_to_menu())
    canvas.tag_bind(back_txt, '<Button-1>', lambda e: back_to_menu())
    canvas.tag_bind(exit_btn, '<Button-1>', lambda e: exit_game())
    canvas.tag_bind(exit_txt, '<Button-1>', lambda e: exit_game())

def clear_game_over():
    global game_over_items
    for it in game_over_items:
        canvas.delete(it)
    game_over_items = []

def back_to_menu():
    # stop game over sound if playing
    sound_game_over.stop()
    
    # reset game variables and show menu
    global time_account, score
    time_account = start_time_account
    score = 0
    clear_game_over()
    show_menu()

def exit_game():
    window.destroy()

# ---------- Start / Pause / Run logic ----------
def start_game():
    global state, time_account, score
    # reset game state, clear menu
    clear_menu()
    time_account = start_time_account
    score = 0
    update_score_display(score)
    update_time_display(time_account)
    
    # ---------- SHOW SHIP & HUD ----------
    for part in [ship_body, ship_hitbox, thruster]:
        canvas.itemconfig(part, state=NORMAL)
    canvas.itemconfig(time_text, state=NORMAL)
    canvas.itemconfig(score_text, state=NORMAL)
    # -----------------------------------
    
    # clear existing bubbles
    for i in range(len(bubble_ids) - 1, -1, -1):
        delete_bubble(i)
    state = GAME_RUNNING
    start_music() # start background music
    tick()

def toggle_pause(event=None):
    global state
    if state == GAME_RUNNING:
        state = GAME_PAUSED
        show_pause_overlay()
    elif state == GAME_PAUSED:
        hide_pause_overlay()
        state = GAME_RUNNING
        tick()  # resume ticking

canvas.bind_all('<space>', toggle_pause)
canvas.bind_all('p', toggle_pause)

TICK_MS = 50  # 50 ms per tick (~20 FPS)

difficulty_level = 0  # increases over time
good_chance = 0.3  # start with 30% good

def tick():
    global state, time_account, score, good_chance

    if state != GAME_RUNNING:
        return

    # Increase difficulty over time: reduce good bubble chance
    difficulty_level = int((start_time_account - time_account) // 10)  # every 10s
    good_chance = max(0.05, 0.3 - 0.05 * difficulty_level)  # min 5% good

    # spawn bubbles randomly
    if randint(1, BUBBLE_CHANCE) == 1:
        create_bubble()
    
    move_bubbles()
    cleanup_bubbles()
    check_collisions_and_apply()

    # decrease time account by tick
    time_account -= (TICK_MS / 1000.0)
    update_score_display(score)
    update_time_display(time_account)

    if time_account <= 0:
        # game over
        show_game_over()
        return

    # schedule next tick
    window.after(TICK_MS, tick)

# ---------- Initialization ----------
show_menu()

# start tkinter mainloop
window.mainloop()
