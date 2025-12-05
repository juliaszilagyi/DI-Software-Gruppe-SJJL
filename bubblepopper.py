# ---------- DI-Software-Gruppe-SJJL // pair1SL ----------
# ---------- Straub Sarah, SZILÁGYI Júlia ----------


# ---------- main_bubblepopper.py ----------


from tkinter import *
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


# ---------- Game States ----------

MENU = 'MENU'
GAME_RUNNING = 'GAME_RUNNING'
GAME_PAUSED = 'GAME_PAUSED'
GAME_OVER = 'GAME_OVER'

state = MENU

# ---------- Players Ship ----------

SHIP_RADIUS = 15
SHIP_SPEED = 20
CENTER_X = WIDTH / 2
CENTER_Y = HEIGHT / 2

ship_body = canvas.create_polygon(7, 2, 7, 28, 30, 15, fill='white')
ship_hitbox = canvas.create_oval(0, 0, 30, 30, outline='white')  # collision circle
canvas.move(ship_body, CENTER_X, CENTER_Y)
canvas.move(ship_hitbox, CENTER_X, CENTER_Y)

def move_ship(event):
    if state != GAME_RUNNING:
        return
    if event.keysym == 'Up':
        canvas.move(ship_body, 0, -SHIP_SPEED)
        canvas.move(ship_hitbox, 0, -SHIP_SPEED)
    elif event.keysym == 'Down':
        canvas.move(ship_body, 0, SHIP_SPEED)
        canvas.move(ship_hitbox, 0, SHIP_SPEED)
    elif event.keysym == 'Left':
        canvas.move(ship_body, -SHIP_SPEED, 0)
        canvas.move(ship_hitbox, -SHIP_SPEED, 0)
    elif event.keysym == 'Right':
        canvas.move(ship_body, SHIP_SPEED, 0)
        canvas.move(ship_hitbox, SHIP_SPEED, 0)

canvas.bind_all('<Key>', move_ship)

# ---------- Bubbles ----------

bubble_ids = []
bubble_radii = []
bubble_speeds = []
bubble_types = []  # 'good' or 'bad'

MIN_BUBBLE_R = 10
MAX_BUBBLE_R = 30
MAX_BUBBLE_SPEED = 15
SPAWN_OFFSET = 100
BUBBLE_CHANCE = 10  # 1 in 10 each tick

# Create a new bubble
def create_bubble():
    x = WIDTH + SPAWN_OFFSET
    y = randint(0, HEIGHT)
    r = randint(MIN_BUBBLE_R, MAX_BUBBLE_R)
    
    # decide good/bad: 70% good, 30% bad
    ty = 'good' if random() < 0.7 else 'bad'
    color = 'green' if ty == 'good' else 'tomato'
    bubble_id = canvas.create_oval(x - r, y - r, x + r, y + r, outline=color, width=2)
    bubble_ids.append(bubble_id)
    bubble_radii.append(r)
    bubble_speeds.append(randint(3, MAX_BUBBLE_SPEED))
    bubble_types.append(ty)

# Move all bubbles leftwards
def move_bubbles():
    for i in range(len(bubble_ids)):
        canvas.move(bubble_ids[i], -bubble_speeds[i], 0)

# Get center coordinates of an object
def get_center(obj_id):
    pos = canvas.coords(obj_id)
    if not pos:
        return -9999, -9999
    x = (pos[0] + pos[2]) / 2
    y = (pos[1] + pos[3]) / 2
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

# Remove bubbles that moved off-screen
def cleanup_bubbles():
    for i in range(len(bubble_ids) - 1, -1, -1):
        x, y = get_center(bubble_ids[i])
        if x < -SPAWN_OFFSET:
            delete_bubble(i)

# Compute distance between two objects
def distance(id1, id2):
    x1, y1 = get_center(id1)
    x2, y2 = get_center(id2)
    return sqrt((x2 - x1)**2 + (y2 - y1)**2)


# ---------- HUD ----------

canvas.create_text(50, 30, text='TIME', fill='white')
canvas.create_text(150, 30, text='SCORE', fill='white')

time_text = canvas.create_text(50, 50, fill='white')
score_text = canvas.create_text(150, 50, fill='white')

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
    for i in range(len(bubble_ids) - 1, -1, -1):
        if distance(ship_hitbox, bubble_ids[i]) < (SHIP_RADIUS + bubble_radii[i]):
            # effect depends on bubble type
            r = bubble_radii[i]
            s = bubble_speeds[i]
            # compute seconds change (example formula)
            seconds_change = (r + s) / 10.0
            if bubble_types[i] == 'good':
                time_account += seconds_change
                score += int(r + s)
            else:
                time_account -= seconds_change
                score += int((r + s) / 2)  # maybe penalty still gives little score
            delete_bubble(i)
            

# ---------- Menu / Buttons / Overlays ----------
menu_items = []
pause_overlay = None
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
    # title
    title = canvas.create_text(CENTER_X, 120, text='Bubble Popper', fill='white', font=('Helvetica', 40, 'bold'))
    # Start button (simple rectangle with text)
    btn_x = CENTER_X
    start_btn = canvas.create_rectangle(btn_x - 100, 200, btn_x + 100, 250, fill='gray20', outline='white')
    start_txt = canvas.create_text(btn_x, 225, text='Start Game', fill='white', font=('Helvetica', 16))
    # Exit button
    exit_btn = canvas.create_rectangle(btn_x - 100, 270, btn_x + 100, 320, fill='gray20', outline='white')
    exit_txt = canvas.create_text(btn_x, 295, text='Exit Game', fill='white', font=('Helvetica', 16))

    menu_items = [title, start_btn, start_txt, exit_btn, exit_txt]

    # Bind clicks - we check click coordinates in handler
    canvas.tag_bind(start_btn, '<Button-1>', lambda e: start_game())
    canvas.tag_bind(start_txt, '<Button-1>', lambda e: start_game())
    canvas.tag_bind(exit_btn, '<Button-1>', lambda e: exit_game())
    canvas.tag_bind(exit_txt, '<Button-1>', lambda e: exit_game())

def show_pause_overlay():
    global pause_overlay
    if pause_overlay is not None:
        return
    pause_overlay = canvas.create_text(CENTER_X, CENTER_Y, text='PAUSED', fill='yellow', font=('Helvetica', 40, 'bold'))

def hide_pause_overlay():
    global pause_overlay
    if pause_overlay:
        canvas.delete(pause_overlay)
        pause_overlay = None

def show_game_over():
    global game_over_items, state
    state = GAME_OVER
    # clear moving objects? we'll leave them but disable updates
    txt = canvas.create_text(CENTER_X, CENTER_Y - 20, text='GAME OVER', fill='white', font=('Helvetica', 40, 'bold'))
    score_txt = canvas.create_text(CENTER_X, CENTER_Y + 10, text=f'SCORE: {score}', fill='white', font=('Helvetica', 20))
    back_btn = canvas.create_rectangle(CENTER_X - 90, CENTER_Y + 50, CENTER_X + 90, CENTER_Y + 90, fill='gray20', outline='white')
    back_txt = canvas.create_text(CENTER_X, CENTER_Y + 70, text='Back to Menu', fill='white')
    exit_btn = canvas.create_rectangle(CENTER_X - 90, CENTER_Y + 100, CENTER_X + 90, CENTER_Y + 140, fill='gray20', outline='white')
    exit_txt = canvas.create_text(CENTER_X, CENTER_Y + 120, text='Exit Game', fill='white')

    game_over_items = [txt, score_txt, back_btn, back_txt, exit_btn, exit_txt]
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
    # clear existing bubbles
    for i in range(len(bubble_ids) - 1, -1, -1):
        delete_bubble(i)
    state = GAME_RUNNING
    # if you have music, start here (person B)
    # start_music()
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

def tick():
    global state, time_account, score
    if state != GAME_RUNNING:
        return
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