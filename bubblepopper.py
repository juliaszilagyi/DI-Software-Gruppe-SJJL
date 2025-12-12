# ---------- DI-Software-Gruppe-SJJL // pair1SL ----------
# ---------- Straub Sarah, Julia Szilagyi ----------

#fixed scoring, size of meteorides and fuel tanks, added twinkling stars to background
#changed sound on off to icon, renamed bubble popper to Spaceship Sprint
#changed time count to a bar
#made a differentiation, collecting stars will increase score, collecting fuel will increase time
#the smaller the star the more points it gives, the smaller the fuel the more time ti adds
#the larger the meteor the more time it reduces
#added best score so far
#made main screen and exit screen "prettier"
#all bubbles movee behind the score bar
#-added a story! After 200, 500, 800, and 1500 points they reach a new planet
#added spacey font type



#still to be done:
#-fix collision radius
#-make the main screen prettier (add instructions?)
#-make exit screen prettier
#adjust read.me
#-make pause screen prettier
#-add restart game or back to menu
#idea: after the last planet make the meteors more difficult



# ---------- main_bubblepopper.py ----------


from tkinter import *
import tkinter as tk
from tkinter import font
import pygame
from random import randint, random
from random import randint, sample
from math import sqrt
import math

# ---------- Window / Canvas ----------

# Window size
HEIGHT = 500
WIDTH = 800

# Create window
window = Tk()
window.title("Spaceship Sprint")

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
        
def twinkle_stars():
    # Only twinkle 10–20 random stars each tick
    num_to_twinkle = 15
    stars_to_twinkle = sample(star_ids, num_to_twinkle)
    
    for star in stars_to_twinkle:
        brightness = randint(120, 255)  # random white intensity
        hex_color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"
        canvas.itemconfig(star, fill=hex_color)
    
    # Schedule next twinkle
    window.after(120, twinkle_stars)

# Generate stars once at the beginning
create_starry_background()
twinkle_stars()


# ---------- Game States ----------

MENU = 'MENU'
GAME_RUNNING = 'GAME_RUNNING'
GAME_PAUSED = 'GAME_PAUSED'
GAME_OVER = 'GAME_OVER'

state = MENU

# --------- Font type ----------

from tkinter import font


# ---------- Sounds -----------
pygame.mixer.init()
sound_on = True  # sound starts on

# Load your sounds
sound_green = pygame.mixer.Sound("green_sound.mp3")  # positive bubble
sound_red = pygame.mixer.Sound("red_sound.wav")      # negative bubble
pygame.mixer.music.load("background.ogg")            # background music
pygame.mixer.music.set_volume(0.3)                   # adjust volume (0.0 to 1.0)
sound_game_over = pygame.mixer.Sound("game_over.mp3")# game over sound
sound_clap = pygame.mixer.Sound("clap.ogg") 		 # clap congratulations sound


def play_sound(sound):
    if sound_on:
        sound.play()
    else:
        sound.stop()

# Start/Stop background music
def start_music():
    pygame.mixer.music.play(-1)  # -1 = loop forever

def stop_music():
    pygame.mixer.music.stop()
    
def toggle_sound():
    global sound_on
    sound_on = not sound_on
    if sound_on:
        pygame.mixer.music.unpause()
        canvas.itemconfig(sound_btn_img, image=sound_on_img)
    else:
        pygame.mixer.music.pause()
        sound_game_over.stop()  # stop game over sound if playing
        canvas.itemconfig(sound_btn_img, image=sound_off_img)

#Images
from PIL import Image, ImageTk

# Load original image
rocket_orig = Image.open("rocket.png")
rocket_resized = rocket_orig.resize((50, 30))  # width, height in pixels
rocket_img = ImageTk.PhotoImage(rocket_resized)

fuel_orig = Image.open("fuel.png")
fuel_resized = fuel_orig.resize((20, 28))
fuel_img = ImageTk.PhotoImage(fuel_resized)

star_orig = Image.open("star.png")
star_resized = star_orig.resize((20, 20))
star_img = ImageTk.PhotoImage(star_resized)

meteor_orig = Image.open("meteorite.png")
meteor_resized = meteor_orig.resize((50, 50))
meteor_img = ImageTk.PhotoImage(meteor_resized)

sound_on_orig = Image.open("sound_on.png")
sound_on_resized = sound_on_orig.resize((15, 15))  
sound_on_img = ImageTk.PhotoImage(sound_on_resized)

sound_off_orig = Image.open("sound_off.png")
sound_off_resized = sound_off_orig.resize((15, 15))
sound_off_img = ImageTk.PhotoImage(sound_off_resized)

#---------- Player's Ship ----------

ROCKET_WIDTH = 50
ROCKET_HEIGHT = 30
SHIP_SPEED = 10

CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2

# Ship image
ship_body = canvas.create_image(CENTER_X, CENTER_Y, image=rocket_img)

# Radius = 1/4 of ship height (diameter = 1/2 height)
NOSE_RADIUS = ROCKET_HEIGHT / 4

# Center of collision circle = behind the nose
circle_center_x = CENTER_X + ROCKET_WIDTH / 2 - NOSE_RADIUS
circle_center_y = CENTER_Y

# Create collision circle
ship_nose_hitbox = canvas.create_oval(
    circle_center_x - NOSE_RADIUS,
    circle_center_y - NOSE_RADIUS,
    circle_center_x + NOSE_RADIUS,
    circle_center_y + NOSE_RADIUS,
    outline=''  
)
canvas.itemconfig(ship_nose_hitbox, state=HIDDEN)  # hide it

# Thruster/flame behind the ship
thruster = canvas.create_polygon(
    CENTER_X - 30, CENTER_Y - 5,
    CENTER_X - 30, CENTER_Y + 5,
    CENTER_X - 40, CENTER_Y,
    fill='orange'
)

# Thruster animation
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
for part in [ship_body, ship_nose_hitbox, thruster]:
    canvas.itemconfig(part, state=HIDDEN)

# ---------- Ship Movement ----------
def move_ship(event):
    if state != GAME_RUNNING:
        return

    if event.keysym == 'Up':
        dy = -SHIP_SPEED
    elif event.keysym == 'Down':
        dy = SHIP_SPEED
    else:
        return

    canvas.move(ship_body, 0, dy)
    canvas.move(ship_nose_hitbox, 0, dy)
    canvas.move(thruster, 0, dy)


key_up_pressed = False
key_down_pressed = False

def on_key_press(event):
    global key_up_pressed, key_down_pressed
    if event.keysym == "Up":
        key_up_pressed = True
    elif event.keysym == "Down":
        key_down_pressed = True

def on_key_release(event):
    global key_up_pressed, key_down_pressed
    if event.keysym == "Up":
        key_up_pressed = False
    elif event.keysym == "Down":
        key_down_pressed = False

canvas.bind_all('<KeyPress>', on_key_press)
canvas.bind_all('<KeyRelease>', on_key_release)

def smooth_move():
    if state == GAME_RUNNING:
        if key_up_pressed:
            canvas.move(ship_body, 0, -SHIP_SPEED)
            canvas.move(ship_nose_hitbox, 0, -SHIP_SPEED)
            canvas.move(thruster, 0, -SHIP_SPEED)

        if key_down_pressed:
            canvas.move(ship_body, 0, SHIP_SPEED)
            canvas.move(ship_nose_hitbox, 0, SHIP_SPEED)
            canvas.move(thruster, 0, SHIP_SPEED)

    window.after(20, smooth_move)

smooth_move()




# ---------- Bubbles (as images) ----------
bubble_ids = []
bubble_radii = []
bubble_speeds = []
bubble_types = []  # 'good' or 'bad'
bubble_images = []  # KEEP IMAGE REFERENCES so Tkinter doesn't delete them

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

    # Decide bubble type based on probabilities
    rand_val = random()
    if rand_val < 0.11:  # 11% chance for fuel (rare)
        ty = 'fuel'
    elif rand_val < good_chance:  # good_chance controls star frequency
        ty = 'star'
    else:
        ty = 'bad'  # meteors

    # Decide radius
    r = randint(MIN_BUBBLE_R, MAX_BUBBLE_R)

    # Assign image and resize while keeping ratio
    if ty == 'fuel':
        img_orig = fuel_orig
        new_width = int(r*2 * 0.6)  
        new_height = int(new_width * img_orig.height / img_orig.width)
    elif ty == 'star':
        img_orig = star_orig
        new_width = r*2
        new_height = r*2 
    else:
        img_orig = meteor_orig
        new_width = r*2
        new_height = r*2  # meteors are square

    # Resize dynamically
    img_resized = img_orig.resize((new_width, new_height))
    img = ImageTk.PhotoImage(img_resized)

    # Keep reference so Tkinter doesn't garbage collect it
    bubble_images.append(img)

    bubble_id = canvas.create_image(x, y, image=img)
    bubble_ids.append(bubble_id)
    bubble_radii.append(r)
    bubble_speeds.append(randint(3, 3 + r//2))
    bubble_types.append(ty)

    # Optional: slowly decrease star chance over time
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

# HUD positions
HUD_PADDING = 20
SCORE_X = HUD_PADDING
SCORE_Y = HUD_PADDING
TIME_BAR_WIDTH = 200
TIME_BAR_HEIGHT = 20
TIME_BAR_X = SCORE_X + 140  # place the bar a bit to the right of the score
TIME_BAR_Y = SCORE_Y

# Score text
score_text = canvas.create_text(SCORE_X, SCORE_Y, anchor='nw', text='SCORE: 0', fill='white', font=('Orbitron', 14))

# Time bar background
time_bar_bg = canvas.create_rectangle(
    TIME_BAR_X, TIME_BAR_Y,
    TIME_BAR_X + TIME_BAR_WIDTH, TIME_BAR_Y + TIME_BAR_HEIGHT,
    fill='gray40'
)

# Time bar fill
time_bar_fill = canvas.create_rectangle(
    TIME_BAR_X, TIME_BAR_Y,
    TIME_BAR_X + TIME_BAR_WIDTH, TIME_BAR_Y + TIME_BAR_HEIGHT,
    fill='green'
)



# Image button for sound
padding = 10
sound_img_width = 30 
sound_img_height = 30

sound_btn_img = canvas.create_image(
    WIDTH - padding - sound_img_width//2, 
    padding + sound_img_height//2, 
    image=sound_on_img
)
canvas.tag_bind(sound_btn_img, '<Button-1>', lambda e: toggle_sound())

def update_score_display(score):
    canvas.itemconfig(score_text, text=f"SCORE: {score}")

def update_time_display(time_left):
    proportion = max(0, time_left / start_time_account)
    canvas.coords(time_bar_fill,
                  TIME_BAR_X, TIME_BAR_Y,
                  TIME_BAR_X + TIME_BAR_WIDTH * proportion,
                  TIME_BAR_Y + TIME_BAR_HEIGHT)
    
    if proportion > 0.5:
        color = 'green'
    elif proportion > 0.2:
        color = 'yellow'
    else:
        color = 'red'
        
    canvas.itemconfig(time_bar_fill, fill=color)



# ---------- Time/Score management ----------

start_time_account = 30.0  # seconds initial
time_account = start_time_account
score = 0
best_score = 0

planets = [
    {"score": 200, "name": "Moon", "image": "moon.png"},
    {"score": 500, "name": "Saturn", "image": "planet.png"},
    {"score": 800, "name": "Mars", "image": "planet2.png"},
    {"score": 1500, "name": "Venus", "image": "planet3.png"},
]
current_planet_index = 0  # track which planet is next


# ---------- Collision handling (affects time_account and score) ----------

def check_collisions_and_apply():
    global time_account, score

    # Get ship nose collision circle center
    ship_coords = canvas.coords(ship_body)
    nose_x = ship_coords[0] + ROCKET_WIDTH / 2       # nose of the ship
    nose_y = ship_coords[1]

    # Circle center is behind nose by NOSE_RADIUS
    circle_center_x = nose_x - NOSE_RADIUS
    circle_center_y = nose_y

    for i in range(len(bubble_ids) - 1, -1, -1):
        bubble_x, bubble_y = get_center(bubble_ids[i])
        dist = sqrt((bubble_x - circle_center_x)**2 + (bubble_y - circle_center_y)**2)

        # Collision occurs if distance < sum of radii
        if dist < (bubble_radii[i] + NOSE_RADIUS):
            r = bubble_radii[i]  # bubble radius
            s = bubble_speeds[i]  # bubble speed

            if bubble_types[i] == 'fuel':
                # smaller fuel = more time
                seconds_change = max(1, (MAX_BUBBLE_R - r + 5) / 3)
                time_account += seconds_change
                play_sound(sound_green)

            elif bubble_types[i] == 'star':
                # smaller star = more score
                points = max(1, int((MAX_BUBBLE_R - r + 5) * 2))
                score += points
                play_sound(sound_green)

            else:  # meteor
                # bigger meteor = more time penalty
                seconds_change = (r + s) / 20.0
                time_account -= seconds_change
                play_sound(sound_red)

            delete_bubble(i)  # remove bubble

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
    
    menu_items = []

    # Background rectangle over the entire canvas
    bg = canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill='black', outline='')
    menu_items.append(bg)

    # Stars in the background
    star_ids_menu = []
    for _ in range(80):
        x = randint(20, WIDTH-20)
        y = randint(20, HEIGHT-20)
        r = randint(1, 3)
        star = canvas.create_oval(x-r, y-r, x+r, y+r, fill='white', outline='')
        star_ids_menu.append(star)
        menu_items.append(star)

    # Animate twinkling stars
    def twinkle_menu_stars():
        if state != MENU:
            return
        for star in star_ids_menu:
            brightness = randint(150, 255)
            hex_color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"
            canvas.itemconfig(star, fill=hex_color)
        window.after(200, twinkle_menu_stars)

    twinkle_menu_stars()

    # Title
    title = canvas.create_text(CENTER_X, 100, text='Spaceship Sprint', fill='white', font=('Orbitron', 50, 'bold'))
    menu_items.append(title)

    # Subtitle / Instructions
    subtitle = canvas.create_text(CENTER_X, 160, 
                                  text='Collect stars, avoid meteors, reach the moon!',
                                  fill='lightblue', font=('Orbitron', 18, 'italic'))
    menu_items.append(subtitle)

    # Start Button
    start_btn_color = '#1E90FF'  # blue
    start_btn_hover = '#63B8FF'  # lighter blue
    start_btn = canvas.create_rectangle(CENTER_X-120, 250, CENTER_X+120, 310, fill=start_btn_color, outline='white', width=2)
    start_txt = canvas.create_text(CENTER_X, 280, text='START GAME', fill='white', font=('Orbitron', 20, 'bold'))
    menu_items.extend([start_btn, start_txt])

    # Exit Button
    exit_btn_color = '#800080'  # purple
    exit_btn_hover = '#B266FF'  # lighter purple
    exit_btn = canvas.create_rectangle(CENTER_X-120, 330, CENTER_X+120, 390, fill=exit_btn_color, outline='white', width=2)
    exit_txt = canvas.create_text(CENTER_X, 360, text='EXIT GAME', fill='white', font=('Orbitron', 20, 'bold'))
    menu_items.extend([exit_btn, exit_txt])

    # Instructions Button
    instr_btn_color = '#228B22'  # green
    instr_btn_hover = '#32CD32'
    instr_btn = canvas.create_rectangle(CENTER_X-120, 410, CENTER_X+120, 470,
                                        fill=instr_btn_color, outline='white', width=2)
    instr_txt = canvas.create_text(CENTER_X, 440, text='INSTRUCTIONS',
                                   fill='white', font=('Orbitron', 20, 'bold'))
    menu_items.extend([instr_btn, instr_txt])




    # Bind
    canvas.tag_bind(instr_btn, '<Button-1>', lambda e: show_instructions())
    canvas.tag_bind(instr_txt, '<Button-1>', lambda e: show_instructions())

    # Hover Effects
    def on_enter_instr(e):
        canvas.itemconfig(instr_btn, fill=instr_btn_hover)
    def on_leave_instr(e):
        canvas.itemconfig(instr_btn, fill=instr_btn_color)

    canvas.tag_bind(instr_btn, '<Enter>', on_enter_instr)
    canvas.tag_bind(instr_txt, '<Enter>', on_enter_instr)
    canvas.tag_bind(instr_btn, '<Leave>', on_leave_instr)
    canvas.tag_bind(instr_txt, '<Leave>', on_leave_instr)

    # Best Score at the bottom
    best_score_txt = canvas.create_text(CENTER_X, HEIGHT - 30, text=f'BEST SCORE: {best_score}', fill='#FFD700', font=('Orbitron', 20, 'bold'))  # gold
    menu_items.append(best_score_txt)

    # Bind clicks
    canvas.tag_bind(start_btn, '<Button-1>', lambda e: start_game())
    canvas.tag_bind(start_txt, '<Button-1>', lambda e: start_game())
    canvas.tag_bind(exit_btn, '<Button-1>', lambda e: exit_game())
    canvas.tag_bind(exit_txt, '<Button-1>', lambda e: exit_game())

    # Hover Effects
    def on_enter_start(e):
        canvas.itemconfig(start_btn, fill=start_btn_hover)
    def on_leave_start(e):
        canvas.itemconfig(start_btn, fill=start_btn_color)

    def on_enter_exit(e):
        canvas.itemconfig(exit_btn, fill=exit_btn_hover)
    def on_leave_exit(e):
        canvas.itemconfig(exit_btn, fill=exit_btn_color)

    canvas.tag_bind(start_btn, '<Enter>', on_enter_start)
    canvas.tag_bind(start_txt, '<Enter>', on_enter_start)
    canvas.tag_bind(start_btn, '<Leave>', on_leave_start)
    canvas.tag_bind(start_txt, '<Leave>', on_leave_start)

    canvas.tag_bind(exit_btn, '<Enter>', on_enter_exit)
    canvas.tag_bind(exit_txt, '<Enter>', on_enter_exit)
    canvas.tag_bind(exit_btn, '<Leave>', on_leave_exit)
    canvas.tag_bind(exit_txt, '<Leave>', on_leave_exit)


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
    pause_overlay = canvas.create_text(CENTER_X, CENTER_Y, text='PAUSED', fill='yellow', font=('Orbitron', 40, 'bold'))


def hide_pause_overlay():
    global pause_overlay, pause_bg
    if pause_overlay:
        canvas.delete(pause_overlay)
        pause_overlay = None
    if pause_bg:
        canvas.delete(pause_bg)
        pause_bg = None



# -------- NEXT PLANET --------

# ---------- PLANET FLY-IN ----------
def planet_fly_in(planet):
    global state, planet_images, hidden_objects
    state = GAME_PAUSED

    # Hide all bubbles and HUD, but keep ship and score visible
    hidden_objects = bubble_ids[:] + [time_bar_bg, time_bar_fill, sound_btn_img]
    for obj in hidden_objects:
        canvas.itemconfig(obj, state=HIDDEN)

    # Make sure score is on top
    canvas.tag_raise(score_text)
    
    # Planet image
    planet_img_orig = Image.open(planet["image"])
    planet_width = 180
    planet_height = 180
    planet_img_resized = planet_img_orig.resize((planet_width, planet_height))
    planet_img = ImageTk.PhotoImage(planet_img_resized)
    if "planet_images" not in globals():
        global planet_images
        planet_images = []
    planet_images.append(planet_img)

    start_x = WIDTH + 100
    ship_x, ship_y = canvas.coords(ship_body)
    end_x = ship_x + ROCKET_WIDTH/2 + planet_width/2  # stop at nose
    end_y = ship_y

    planet_id = canvas.create_image(start_x, end_y, image=planet_img)

    # Play milestone clap
    stop_music()
    play_sound(sound_clap)

    def animate():
        nonlocal start_x
        if start_x > end_x:
            start_x -= 10
            canvas.coords(planet_id, start_x, end_y)
            window.after(50, animate)
        else:
            show_reach_planet_overlay(planet, planet_id)

    animate()


# ---------- SHOW PLANET OVERLAY ----------
def show_reach_planet_overlay(planet, planet_id):
    global game_over_items
    game_over_items = []

    # Semi-transparent rectangle (smaller, centered)
    rect_width = 550
    rect_height = 250
    rect = canvas.create_rectangle(
        CENTER_X - rect_width//2,
        CENTER_Y - rect_height//2,
        CENTER_X + rect_width//2,
        CENTER_Y + rect_height//2,
        fill='gray30',
        stipple='gray12',
        outline='white',
        width=2
    )

    # Texts centered
    txt = canvas.create_text(
        CENTER_X, CENTER_Y - 40,
        text=f"Congratulations!\nYou've reached the {planet['name']}!",
        fill='white',
        font=('Orbitron', 24, 'bold'),
        justify='center'
    )

    # Buttons centered
    next_btn = canvas.create_rectangle(CENTER_X - 180, CENTER_Y + 20, CENTER_X + 180, CENTER_Y + 60, fill='green', outline='white')
    next_txt = canvas.create_text(CENTER_X, CENTER_Y + 40, text='I want to reach the next planet', fill='white', font=('Orbitron', 14))

    exit_btn = canvas.create_rectangle(CENTER_X - 180, CENTER_Y + 70, CENTER_X + 180, CENTER_Y + 110, fill='purple', outline='white')
    exit_txt = canvas.create_text(CENTER_X, CENTER_Y + 90, text='Back to Menu', fill='white', font=('Orbitron', 14))

    game_over_items = [rect, txt, next_btn, next_txt, exit_btn, exit_txt, planet_id]

    # Bind buttons
    canvas.tag_bind(next_btn, '<Button-1>', lambda e: continue_to_next_planet(planet_id))
    canvas.tag_bind(next_txt, '<Button-1>', lambda e: continue_to_next_planet(planet_id))
    canvas.tag_bind(exit_btn, '<Button-1>', lambda e: back_to_menu())
    canvas.tag_bind(exit_txt, '<Button-1>', lambda e: back_to_menu())

# ---------- CONTINUE TO NEXT PLANET ----------
def continue_to_next_planet(planet_id=None):
    global state, time_account, game_over_items, current_planet_index
    # Remove overlay and planet
    clear_game_over()

    if planet_id:
        canvas.delete(planet_id)

    # Reset time and resume game
    time_account = start_time_account
    state = GAME_RUNNING
    current_planet_index += 1

    # Show ship/HUD again
    for obj in hidden_objects:
        canvas.itemconfig(obj, state=NORMAL)

    start_music()
    tick()



# --------GAME OVER ------
def show_game_over():
    global game_over_items, state, best_score
    state = GAME_OVER
    
    clear_game_over()
    
    if score > best_score:
        best_score = score
    
    stop_music()
    play_sound(sound_game_over)
    
    game_over_items = []

    # Bigger central rectangle
    rect_width = 500
    rect_height = 380
    rect = canvas.create_rectangle(
        CENTER_X - rect_width // 2,
        CENTER_Y - rect_height // 2,
        CENTER_X + rect_width // 2,
        CENTER_Y + rect_height // 2,
        fill='gray25',
        stipple='gray25',
        outline='white',
        width=2
    )
    game_over_items.append(rect)

    # Game Over title
    txt = canvas.create_text(CENTER_X, CENTER_Y - 120, text='GAME OVER', fill='#FF3333', font=('Orbitron', 48, 'bold'))
    game_over_items.append(txt)

    # Current score
    score_txt = canvas.create_text(CENTER_X, CENTER_Y - 55, text=f'SCORE: {score}', fill='white', font=('Orbitron', 24, 'bold'))
    game_over_items.append(score_txt)

    # Back to Menu Button (blue)
    back_btn_color = '#1E90FF'
    back_btn_hover = '#63B8FF'
    back_btn = canvas.create_rectangle(CENTER_X-120, CENTER_Y+10, CENTER_X+120, CENTER_Y+65, fill=back_btn_color, outline='white', width=2)
    back_txt = canvas.create_text(CENTER_X, CENTER_Y+37, text='Back to Menu', fill='white', font=('Orbitron', 22, 'bold'))
    game_over_items.extend([back_btn, back_txt])

    # Exit Button (purple)
    exit_btn_color = '#800080'
    exit_btn_hover = '#B266FF'
    exit_btn = canvas.create_rectangle(CENTER_X-120, CENTER_Y+85, CENTER_X+120, CENTER_Y+140, fill=exit_btn_color, outline='white', width=2)
    exit_txt = canvas.create_text(CENTER_X, CENTER_Y+112, text='Exit Game', fill='white', font=('Orbitron', 22, 'bold'))
    game_over_items.extend([exit_btn, exit_txt])

    # Best score
    best_txt = canvas.create_text(CENTER_X, CENTER_Y+170, text=f'BEST SCORE: {best_score}', fill='#FFD700', font=('Orbitron', 18, 'bold'))
    game_over_items.append(best_txt)

    # Bind clicks
    canvas.tag_bind(back_btn, '<Button-1>', lambda e: back_to_menu())
    canvas.tag_bind(back_txt, '<Button-1>', lambda e: back_to_menu())
    canvas.tag_bind(exit_btn, '<Button-1>', lambda e: exit_game())
    canvas.tag_bind(exit_txt, '<Button-1>', lambda e: exit_game())

    # Hover Effects
    def on_enter_back(e):
        canvas.itemconfig(back_btn, fill=back_btn_hover)
    def on_leave_back(e):
        canvas.itemconfig(back_btn, fill=back_btn_color)
    canvas.tag_bind(back_btn, '<Enter>', on_enter_back)
    canvas.tag_bind(back_txt, '<Enter>', on_enter_back)
    canvas.tag_bind(back_btn, '<Leave>', on_leave_back)
    canvas.tag_bind(back_txt, '<Leave>', on_leave_back)

    def on_enter_exit(e):
        canvas.itemconfig(exit_btn, fill=exit_btn_hover)
    def on_leave_exit(e):
        canvas.itemconfig(exit_btn, fill=exit_btn_color)
    canvas.tag_bind(exit_btn, '<Enter>', on_enter_exit)
    canvas.tag_bind(exit_txt, '<Enter>', on_enter_exit)
    canvas.tag_bind(exit_btn, '<Leave>', on_leave_exit)
    canvas.tag_bind(exit_txt, '<Leave>', on_leave_exit)


def clear_game_over():
    global game_over_items
    for it in game_over_items:
        canvas.delete(it)
    game_over_items = []

def back_to_menu():
    global best_score, score

    # Update best score if current score is higher
    if score > best_score:
        best_score = score

    # Stop any sounds
    sound_game_over.stop()

    # Reset game variables
    time_account = start_time_account
    score = 0

    # Clear planet overlay or other items
    clear_game_over()

    # Show menu
    show_menu()

def exit_game():
    pygame.mixer.quit()  # stop all sounds safely
    window.destroy()

def show_instructions():
    global state, menu_items
    clear_menu()
    state = MENU
    menu_items = []

    FRAME_MARGIN = 40
    MARGIN_MM = 15

    # --- OUTER FRAME ---
    frame = canvas.create_rectangle(
        FRAME_MARGIN, FRAME_MARGIN,
        WIDTH - FRAME_MARGIN, HEIGHT - FRAME_MARGIN,
        fill="black", outline="white", width=3
    )
    menu_items.append(frame)

    # --- TITLE ---
    title = canvas.create_text(
        CENTER_X, FRAME_MARGIN + 30,
        text="📘 HOW TO PLAY — Spaceship Sprint",
        fill="cyan",
        font=("Orbitron", 22, "bold")
    )
    menu_items.append(title)

    # --- LEFT-ALIGNED TEXT BLOCK (NO SCROLLING) ---
    left_x = FRAME_MARGIN + 30
    y = FRAME_MARGIN + 80
    line_gap = 22
    section_gap = 35

    def add_section(header, lines, y):
        header_id = canvas.create_text(
            left_x, y,
            text=header,
            fill="white",
            anchor="nw",
            font=("Orbitron", 16, "bold")
        )
        menu_items.append(header_id)
        y += line_gap

        for line in lines:
            line_id = canvas.create_text(
                left_x, y,
                text=line,
                fill="white",
                anchor="nw",
                font=("Orbitron", 12)
            )
            menu_items.append(line_id)
            y += line_gap

        return y + section_gap

    # ---- SECTIONS WITHOUT SCROLLING ----
    y = add_section("GOAL", [
        "Fly through space, collect stars to increase score,",
        "collect fuel to gain extra time, and avoid meteors."
    ], y)

    y = add_section("CONTROLS", [
        "⬆️  Press UP to move upward",
        "⬇️  Press DOWN to move downward",
        "⏸️  Press SPACE or 'P' to pause/unpause"
    ], y)

    # Items — shortened & reduced text
    y = add_section("ITEMS", [
        "⭐ Stars: Smaller stars = more points",
        "⛽ Fuel: Smaller fuels = more time",
        "☄️ Meteors: Larger meteors remove more time"
    ], y)

    # --- BACK BUTTON ---
    BACK_W = 100
    BACK_H = 35

    back_btn_x1 = WIDTH - FRAME_MARGIN - BACK_W - MARGIN_MM
    back_btn_x2 = back_btn_x1 + BACK_W

    back_btn_y2 = HEIGHT - FRAME_MARGIN - MARGIN_MM
    back_btn_y1 = back_btn_y2 - BACK_H

    back_btn = canvas.create_rectangle(
        back_btn_x1, back_btn_y1,
        back_btn_x2, back_btn_y2,
        fill="#1E90FF", outline="white", width=2
    )
    back_txt = canvas.create_text(
        (back_btn_x1 + back_btn_x2) // 2,
        (back_btn_y1 + back_btn_y2) // 2,
        text="BACK",
        fill="white",
        font=("Orbitron", 14, "bold")
    )

    canvas.tag_raise(back_btn)
    canvas.tag_raise(back_txt)

    menu_items.extend([back_btn, back_txt])

    canvas.tag_bind(back_btn, "<Button-1>", lambda e: show_menu())
    canvas.tag_bind(back_txt, "<Button-1>", lambda e: show_menu())



# ---------- Start / Pause / Run logic ----------
def start_game():
    global state, time_account, score, current_planet_index
    # reset game state, clear menu
    clear_menu()
    time_account = start_time_account
    score = 0
    current_planet_index = 0
    update_score_display(score)
    update_time_display(time_account)
    
    # SHOW SHIP & HUD 
    for part in [ship_body, ship_nose_hitbox, thruster]:
        canvas.itemconfig(part, state=NORMAL)
    canvas.itemconfig(score_text, state=NORMAL)
    
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

TICK_MS = 50  # 50 ms per tick

difficulty_level = 0  # increases over time
good_chance = 0.3  # start with 30% good

def tick():
    global state, time_account, score, good_chance, current_planet_index

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

    # raise HUD and ship on top of bubbles
    canvas.tag_raise(score_text)
    canvas.tag_raise(time_bar_bg)
    canvas.tag_raise(time_bar_fill)
    canvas.tag_raise(sound_btn_img)
    canvas.tag_raise(ship_body)
    canvas.tag_raise(ship_nose_hitbox)
    canvas.tag_raise(thruster)

    # decrease time account by tick
    time_account -= (TICK_MS / 1000.0)
    update_score_display(score)
    update_time_display(time_account)

    # check planet milestone
    if current_planet_index < len(planets):
        if score >= planets[current_planet_index]["score"]:
            planet_fly_in(planets[current_planet_index])
            return  # pause the tick loop while planet animation is ongoing

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
