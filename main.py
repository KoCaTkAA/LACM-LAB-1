import pygame
import math
import numpy as np
from pygame.locals import *
# мими мямя
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("3D")
clock = pygame.time.Clock()

# цвета
background = (255, 255, 255)
grid = (50, 50, 70)
surface = (100, 150, 200)

# параметры поверхности Мёбиуса
alpha = 2.0
beta = 1.0
u_min, u_max = 0, 2 * math.pi
v_min, v_max = -0.5, 0.5
u_steps, v_steps = 50, 10

# параметры камеры
camera_pos = np.array([0, 0, -2])
camera_angle_x = 0
camera_angle_y = 0
zoom = 200

light_pos = np.array([10, 10, 10])


def calculating_coordinates(u, v, alpha, beta):
    x = (alpha + v * math.cos(u/2)) * math.cos(u)
    y = (alpha + v * math.cos(u/2)) * math.sin(u)
    z = beta * v * math.sin(u/2)
    return np.array([x, y, z])


def vector_product(a, b):
    cx = a[1] * b[2] - a[2] * b[1]
    cy = a[2] * b[0] - a[0] * b[2]
    cz = a[0] * b[1] - a[1] * b[0]
    return np.array([cx, cy, cz])


def scalar_product(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def vector_len(v):
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def normal_triangle(p1, p2, p3):
    v1 = np.array([p1[0] - p2[0], p1[1] - p2[1], p1[2] - p2[2]])
    v2 = np.array([p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2]])
    normal = vector_product(v1, v2)
    normal_len = vector_len(normal)
    if normal_len == 0:
        return normal
    return normal / normal_len


def calculate_lighting(normal, light_pos, base_color):
    light_dir = light_pos / vector_len(light_pos)
    intensity = abs(scalar_product(normal, light_dir))
    intensity = max(0, min(1, intensity))

    ratio = 0.3
    intensity = ratio + (1 - ratio) * intensity

    return tuple(int(c * intensity) for c in base_color)


# треугольнички
def generate_polygons():
    points = []
    polygons = []
    for i in range(u_steps):
        u = u_min + (u_max - u_min) * i / (u_steps - 1)
        row = []
        for j in range(v_steps):
            v = v_min + (v_max - v_min) * j / (v_steps - 1)
            point = calculating_coordinates(u, v, alpha, beta)
            row.append(point)
        points.append(row)

    for i in range(u_steps - 1):
        for j in range(v_steps - 1):
            p1 = points[i][j]
            p2 = points[i + 1][j]
            p3 = points[i + 1][j + 1]
            p4 = points[i][j + 1]

            polygons.append((p1, p2, p3))
            polygons.append((p3, p4, p1))

    return polygons


def project_point(point):
    rot_x = np.array([
        [1, 0, 0],
        [0, math.cos(camera_angle_x), -math.sin(camera_angle_x)],
        [0, math.sin(camera_angle_x), math.cos(camera_angle_x)]
    ])

    rot_y = np.array([
        [math.cos(camera_angle_y), 0, math.sin(camera_angle_y)],
        [0, 1, 0],
        [-math.sin(camera_angle_y), 0, math.cos(camera_angle_y)]
    ])

    rotated = scalar_product(rot_y, scalar_product(rot_x, point - camera_pos))

    if rotated[2] != 0:
        z = 1 / rotated[2]
    else:
        z = 1

    perspective = np.array([
        [z, 0, 0],
        [0, z, 0]
    ])

    projected = np.dot(perspective, rotated)

    x = int(projected[0] * zoom + width / 2)
    y = int(-projected[1] * zoom + height / 2)

    return (x, y)


def draw_surface(polygons):
    for poly in polygons:
        if len(poly) == 3:
            p1, p2, p3 = poly

            normal = normal_triangle(p1, p2, p3)

            color = calculate_lighting(normal, light_pos, surface)

            points_2d = [project_point(p) for p in poly]

            pygame.draw.polygon(screen, color, points_2d)
            pygame.draw.polygon(screen, (0, 0, 0), points_2d, 1)


running = True
dragging = False
last_mouse_pos = None
polygons = generate_polygons()

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_LEFT:
                camera_angle_y -= 0.1
            elif event.key == K_RIGHT:
                camera_angle_y += 0.1
            elif event.key == K_UP:
                camera_angle_x -= 0.1
            elif event.key == K_DOWN:
                camera_angle_x += 0.1
            elif event.key == K_PLUS or event.key == K_EQUALS:
                zoom *= 1.1
            elif event.key == K_MINUS:
                zoom /= 1.1

    screen.fill(background)

    draw_surface(polygons)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()