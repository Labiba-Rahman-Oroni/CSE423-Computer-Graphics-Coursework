

######task_2_amazing_box########

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# ===== Global Variables =====
WINDOW_WIDTH, WINDOW_HEIGHT = 600, 600  
POINT_SIZE = 5
speed = 1.0     
SPEED_STEP = 0.5
MIN_SPEED = 0.5
MAX_SPEED = 8.0
points = []     
blinking = False      
blink_counter = 0      
BLINK_PERIOD = 60       
frozen = False          


HALF_W = WINDOW_WIDTH / 2
HALF_H = WINDOW_HEIGHT / 2

POINT_HALF = POINT_SIZE / 2
LEFT_WALL = -HALF_W + POINT_HALF
RIGHT_WALL = HALF_W - POINT_HALF
BOTTOM_WALL = -HALF_H + POINT_HALF
TOP_WALL = HALF_H - POINT_HALF


def setup_projection():
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-HALF_W, HALF_W, -HALF_H, HALF_H, 0, 1)
    glMatrixMode(GL_MODELVIEW)


def draw_point(x, y, size):
    glPointSize(size)
    glBegin(GL_POINTS)
    glVertex2f(x, y)
    glEnd()


def convert_coordinate(x, y):
    a = x - HALF_W
    b = HALF_H - y
    return a, b


def mouse_listener(button, state, x, y):
    global blinking, blink_counter
    if frozen:
        return
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        px, py = convert_coordinate(x, y)
        px = max(LEFT_WALL, min(RIGHT_WALL, px))
        py = max(BOTTOM_WALL, min(TOP_WALL, py))
        r = random.uniform(0.3, 1.0)
        g = random.uniform(0.3, 1.0)
        b = random.uniform(0.3, 1.0)
        dx = random.choice([-1, 1])
        dy = random.choice([-1, 1])
        points.append([px, py, r, g, b, dx, dy])
    elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        blinking = not blinking
        blink_counter = 0
        print("Blinking:", blinking)
    glutPostRedisplay()


def special_key_listener(key, x, y):
    global speed
    if frozen:
        return
    if key == GLUT_KEY_UP:
        speed = min(MAX_SPEED, speed + SPEED_STEP)
        print("Speed:", speed)
    elif key == GLUT_KEY_DOWN:
        speed = max(MIN_SPEED, speed - SPEED_STEP)
        print("Speed:", speed)
    glutPostRedisplay()


def keyboard_listener(key, x, y):
    global frozen
    if key == b' ':
        frozen = not frozen
        print("Frozen:", frozen)
    glutPostRedisplay()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    setup_projection()

    for p in points:
        if blinking and blink_counter >= BLINK_PERIOD // 2:
            glColor3f(0.0, 0.0, 0.0)          
        else:
            glColor3f(p[2], p[3], p[4])      
        draw_point(p[0], p[1], POINT_SIZE)

    glutSwapBuffers()


def animate():
    global blink_counter
    if frozen:
        return

    if blinking:
        blink_counter = blink_counter + 1
        if blink_counter >= BLINK_PERIOD:
            blink_counter = 0

    for p in points:
        p[0] = p[0] + p[5] * speed
        p[1] = p[1] + p[6] * speed

        if p[0] > RIGHT_WALL:
            p[0] = RIGHT_WALL
            p[5] = -p[5]
        elif p[0] < LEFT_WALL:
            p[0] = LEFT_WALL
            p[5] = -p[5]

        if p[1] > TOP_WALL:
            p[1] = TOP_WALL
            p[6] = -p[6]
        elif p[1] < BOTTOM_WALL:
            p[1] = BOTTOM_WALL
            p[6] = -p[6]

    glutPostRedisplay()


def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Task 2: Amazing Box")
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutMouseFunc(mouse_listener)
    glutSpecialFunc(special_key_listener)
    glutKeyboardFunc(keyboard_listener)
    glutMainLoop()


if __name__ == "__main__":
    main()
    




