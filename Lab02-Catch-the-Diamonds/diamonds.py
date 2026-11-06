from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

WIN_W, WIN_H = 400, 640

DIAMOND_W, DIAMOND_H = 20, 36
CATCHER_W, CATCHER_H = 120, 20
CATCHER_Y = 15
CATCHER_STEP = 20
BTN_SIZE = 40
BTN_Y = WIN_H - BTN_SIZE - 20
BTN_RESTART_X = 20
BTN_PAUSE_X = (WIN_W - BTN_SIZE) // 2
BTN_EXIT_X = WIN_W - BTN_SIZE - 20

START_SPEED = 150
SPEED_STEP = 20
MAX_SPEED = 600

catcher_x = (WIN_W - CATCHER_W) // 2
diamond_x, diamond_y = 0, 0
diamond_color = (1.0, 1.0, 0.0)
diamond_speed = START_SPEED
score = 0
game_over = False
paused = False
last_time = 0.0


def find_zone(dx, dy):
    if abs(dx) >= abs(dy):
        if dx >= 0 and dy >= 0:
            return 0
        elif dx < 0 and dy >= 0:
            return 3
        elif dx < 0 and dy < 0:
            return 4
        else:
            return 7
    else:
        if dx >= 0 and dy >= 0:
            return 1
        elif dx < 0 and dy >= 0:
            return 2
        elif dx < 0 and dy < 0:
            return 5
        else:
            return 6


def to_zone0(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return y, -x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return -y, x
    else:
        return x, -y


def from_zone0(x, y, zone):
    if zone == 0:
        return x, y
    elif zone == 1:
        return y, x
    elif zone == 2:
        return -y, x
    elif zone == 3:
        return -x, y
    elif zone == 4:
        return -x, -y
    elif zone == 5:
        return -y, -x
    elif zone == 6:
        return y, -x
    else:
        return x, -y


def midpoint_zone0(x1, y1, x2, y2, zone):
    dx = x2 - x1
    dy = y2 - y1
    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)
    x = x1
    y = y1
    glBegin(GL_POINTS)
    while x <= x2:
        ox, oy = from_zone0(x, y, zone)
        glVertex2f(ox, oy)
        if d > 0:
            d = d + incNE
            y = y + 1
        else:
            d = d + incE
        x = x + 1
    glEnd()


def draw_line(x1, y1, x2, y2):
    x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
    zone = find_zone(x2 - x1, y2 - y1)
    a1, b1 = to_zone0(x1, y1, zone)
    a2, b2 = to_zone0(x2, y2, zone)
    midpoint_zone0(a1, b1, a2, b2, zone)


def has_collided(x1, y1, w1, h1, x2, y2, w2, h2):
    return (x1 < x2 + w2 and
            x1 + w1 > x2 and
            y1 < y2 + h2 and
            y1 + h1 > y2)


def inside_box(mx, my, x, y, w, h):
    return x <= mx <= x + w and y <= my <= y + h


def convert_coordinate(x, y):
    return x, WIN_H - y


def draw_diamond():
    x = int(diamond_x)
    y = int(diamond_y)
    r, g, b = diamond_color
    glColor3f(r, g, b)
    top = (x + DIAMOND_W // 2, y + DIAMOND_H)
    right = (x + DIAMOND_W, y + DIAMOND_H // 2)
    bottom = (x + DIAMOND_W // 2, y)
    left = (x, y + DIAMOND_H // 2)
    draw_line(top[0], top[1], right[0], right[1])
    draw_line(right[0], right[1], bottom[0], bottom[1])
    draw_line(bottom[0], bottom[1], left[0], left[1])
    draw_line(left[0], left[1], top[0], top[1])


def draw_catcher():
    if game_over:
        glColor3f(1.0, 0.0, 0.0)
    else:
        glColor3f(1.0, 1.0, 1.0)
    x = int(catcher_x)
    y = CATCHER_Y
    inset = 15
    draw_line(x, y + CATCHER_H, x + CATCHER_W, y + CATCHER_H)
    draw_line(x + CATCHER_W, y + CATCHER_H, x + CATCHER_W - inset, y)
    draw_line(x + CATCHER_W - inset, y, x + inset, y)
    draw_line(x + inset, y, x, y + CATCHER_H)


def draw_restart_button():
    glColor3f(0.0, 0.85, 0.85)
    x, y, s = BTN_RESTART_X, BTN_Y, BTN_SIZE
    cy = y + s // 2
    draw_line(x, cy, x + s, cy)
    draw_line(x, cy, x + s // 2, y + s)
    draw_line(x, cy, x + s // 2, y)


def draw_pause_button():
    glColor3f(1.0, 0.75, 0.0)
    x, y, s = BTN_PAUSE_X, BTN_Y, BTN_SIZE
    if paused:
        draw_line(x, y, x, y + s)
        draw_line(x, y + s, x + s, y + s // 2)
        draw_line(x + s, y + s // 2, x, y)
    else:
        cx = x + s // 2
        draw_line(cx - 5, y, cx - 5, y + s)
        draw_line(cx + 5, y, cx + 5, y + s)


def draw_exit_button():
    glColor3f(1.0, 0.0, 0.0)
    x, y, s = BTN_EXIT_X, BTN_Y, BTN_SIZE
    draw_line(x, y, x + s, y + s)
    draw_line(x, y + s, x + s, y)


def spawn_diamond():
    global diamond_x, diamond_y, diamond_color
    diamond_x = random.randint(0, WIN_W - DIAMOND_W)
    diamond_y = WIN_H - DIAMOND_H
    diamond_color = (random.uniform(0.4, 1.0),
                     random.uniform(0.4, 1.0),
                     random.uniform(0.4, 1.0))


def restart_game():
    global score, diamond_speed, game_over, paused, catcher_x
    score = 0
    diamond_speed = START_SPEED
    game_over = False
    paused = False
    catcher_x = (WIN_W - CATCHER_W) // 2
    spawn_diamond()


def animate():
    global last_time, diamond_y, diamond_speed, score, game_over
    now = time.time()
    dt = now - last_time
    last_time = now
    if dt > 0.05:
        dt = 0.05

    if not paused and not game_over:
        diamond_y -= diamond_speed * dt

        if has_collided(diamond_x, diamond_y, DIAMOND_W, DIAMOND_H,
                        catcher_x, CATCHER_Y, CATCHER_W, CATCHER_H):
            score += 1
            print("Score:", score)
            diamond_speed = min(diamond_speed + SPEED_STEP, MAX_SPEED)
            spawn_diamond()
        elif diamond_y + DIAMOND_H < 0:
            game_over = True
            print("Game Over! Score:", score)
            score = 0
            diamond_speed = START_SPEED

    glutPostRedisplay()


def special_key_listener(key, x, y):
    global catcher_x
    if paused or game_over:
        return
    if key == GLUT_KEY_LEFT:
        catcher_x = max(0, catcher_x - CATCHER_STEP)
    elif key == GLUT_KEY_RIGHT:
        catcher_x = min(WIN_W - CATCHER_W, catcher_x + CATCHER_STEP)
    glutPostRedisplay()


def mouse_listener(button, state, x, y):
    global paused
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        mx, my = convert_coordinate(x, y)
        if inside_box(mx, my, BTN_RESTART_X, BTN_Y, BTN_SIZE, BTN_SIZE):
            print("Starting over!")
            restart_game()
        elif inside_box(mx, my, BTN_PAUSE_X, BTN_Y, BTN_SIZE, BTN_SIZE):
            paused = not paused
        elif inside_box(mx, my, BTN_EXIT_X, BTN_Y, BTN_SIZE, BTN_SIZE):
            print("Goodbye! Score:", score)
            glutLeaveMainLoop()


def setup_projection():
    glViewport(0, 0, WIN_W, WIN_H)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, WIN_W, 0, WIN_H, 0, 1)
    glMatrixMode(GL_MODELVIEW)


def display():
    glClearColor(0, 0, 0, 1)
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    setup_projection()
    glPointSize(2)

    draw_restart_button()
    draw_pause_button()
    draw_exit_button()
    draw_catcher()
    if not game_over:
        draw_diamond()

    glutSwapBuffers()


def main():
    global last_time
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA)
    glutInitWindowSize(WIN_W, WIN_H)
    glutInitWindowPosition(100, 50)
    glutCreateWindow(b"Catch the Diamonds!")

    spawn_diamond()
    last_time = time.time()

    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)
    glutMainLoop()


if __name__ == "__main__":
    main()