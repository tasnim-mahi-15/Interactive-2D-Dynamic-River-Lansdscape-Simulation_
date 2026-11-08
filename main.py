import math
import random
import sys
import pygame

# --- Initialize PyGame ---
pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(
    "River Sunset - Wind Control (A=Left, D=Right [Works when Paused too!]),"
    " Sun Up/Down (UP/DOWN), River Current (LEFT/RIGHT), Birds Dir (Q=Left,"
    " W=Right),Controls: Day/Night (N), Rain (R), Clouds (C), Pause (SPACE)"
)
clock = pygame.time.Clock()


# --- Custom Algorithm Implementations ---

#---DDA Algorithm implementation

def dda_line(surface, x1, y1, x2, y2, color, thickness=1):
    """Implementation of DDA Line Algorithm."""
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    dx = x2 - x1
    dy = y2 - y1

    steps = max(abs(dx), abs(dy))
    if steps == 0:
        if 0 <= x1 < WIDTH and 0 <= y1 < HEIGHT:
            pygame.draw.circle(surface, color, (x1, y1), max(1, thickness // 2))
        return

    x_inc = dx / steps
    y_inc = dy / steps

    x, y = float(x1), float(y1)
    r_radius = max(1, thickness // 2)

    for _ in range(steps + 1):
        rx, ry = round(x), round(y)
        if 0 <= rx < WIDTH and 0 <= ry < HEIGHT:
            if thickness <= 1:
                surface.set_at((rx, ry), color)  # memory writing function
            else:
                pygame.draw.circle(surface, color, (rx, ry), r_radius)
        x += x_inc
        y += y_inc

#-----bresenham_line_Drawing Algorithm implementation

def bresenham_line(surface, x1, y1, x2, y2, color, thickness=1):
    """Implementation of Bresenham Line Drawing Algorithm (Generalized for all octants)."""
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    dx = x2 - x1
    dy = y2 - y1

    sx = 1 if dx > 0 else -1
    sy = 1 if dy > 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    x = x1
    y = y1
    r_radius = max(1, thickness // 2)

    def draw_pixel(px, py):
        if 0 <= px < WIDTH and 0 <= py < HEIGHT:
            if thickness <= 1:
                surface.set_at((px, py), color)
            else:
                pygame.draw.circle(surface, color, (px, py), r_radius)

    draw_pixel(x, y)

    if dx > dy:
        pk = 2 * dy - dx
        for _ in range(dx):
            if pk < 0:
                x += sx
                pk += 2 * dy
            else:
                x += sx
                y += sy
                pk += 2 * dy - 2 * dx
            draw_pixel(x, y)
    else:
        pk = 2 * dx - dy
        for _ in range(dy):
            if pk < 0:
                y += sy
                pk += 2 * dx
            else:
                x += sx
                y += sy
                pk += 2 * dx - 2 * dy
            draw_pixel(x, y)



#-----Midpoint Circel Algorithm implementation

def midpoint_circle(surface, xc, yc, r, color, fill=True):
    """Implementation of Midpoint Circle Algorithm."""
    xc, yc, r = int(xc), int(yc), int(r)
    if r <= 0:
        return

    x = 0
    y = r
    pk = 1 - r

    def draw_symmetric_lines(x_val, y_val):
        if fill:
            pygame.draw.line(
                surface, color, (xc - x_val, yc + y_val), (xc + x_val, yc + y_val)
            )
            pygame.draw.line(
                surface, color, (xc - x_val, yc - y_val), (xc + x_val, yc - y_val)
            )
            pygame.draw.line(
                surface, color, (xc - y_val, yc + x_val), (xc + y_val, yc + x_val)
            )
            pygame.draw.line(
                surface, color, (xc - y_val, yc - x_val), (xc + y_val, yc - x_val)
            )
        else:
            points = [
                (xc + x_val, yc + y_val),
                (xc - x_val, yc + y_val),
                (xc + x_val, yc - y_val),
                (xc - x_val, yc - y_val),
                (xc + y_val, yc + x_val),
                (xc - y_val, yc + x_val),
                (xc + y_val, yc - x_val),
                (xc - y_val, yc - x_val),
            ]
            for px, py in points:
                if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                    surface.set_at((px, py), color)

    draw_symmetric_lines(x, y)

    while x < y:
        x += 1
        if pk < 0:
            pk = pk + 2 * x + 1
        else:
            y -= 1
            pk = pk + 2 * x - 2 * y + 1
        draw_symmetric_lines(x, y)


def get_bezier_point(p0, p1, p2, t):
    """Computes a 2D quadratic Bézier curve point."""
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t**2 * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t**2 * p2[1]
    return (x, y)


# --- Scene State ---


class SceneState:

    def __init__(self):
        self.is_day = True
        self.is_raining = True
        self.show_clouds = True
        self.is_paused = False

        self.river_current = 1.0
        self.wind_force = 3.0  # বাতাসের মূল মান

        self.sun_x = 500
        self.sun_y = 140
        self.sun_radius = 45
        self.sun_ray_ang = 0

        self.birds_x = 0
        self.birds_y = 0
        self.bird_dir = 1

        self.left_tree_x, self.left_tree_y = 150, 495
        self.right_tree_x, self.right_tree_y = 820, 500

        self.boat_x = -150
        self.anim_time = 0

        self.raindrops = [
            [
                random.randint(-100, WIDTH + 100),
                random.randint(-HEIGHT, HEIGHT),
                random.randint(18, 26),
                random.uniform(11, 15),
            ]
            for _ in range(200)
        ]

        self.clouds = [
            [
                random.randint(-200, WIDTH),
                random.randint(30, 150),
                1.2,
                (random.randint(30, 50), random.randint(20, 30)),
            ]
            for _ in range(6)
        ]

    def get_sky_colors(self):
        if self.is_day:
            return (50, 130, 240), (180, 220, 255)
        else:
            return (110, 25, 95), (250, 120, 50)

    def get_land_color(self):
        return (40, 160, 50) if self.is_day else (35, 12, 25)

    def get_palm_color(self):
        return (30, 100, 30) if self.is_day else (25, 15, 30)

    def get_sun_color(self):
        return (255, 245, 150) if self.is_day else (255, 80, 20)

    def get_boat_color(self):
        return (110, 65, 25) if self.is_day else (20, 12, 10)


state = SceneState()


# --- Drawing Helpers ---


def draw_background(surface):
    top_color, bottom_color = state.get_sky_colors()

    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))


def draw_back_mountains(surface):
    color = (130, 160, 200) if state.is_day else (65, 25, 60)
    pts = [
        (-50, 410),
        (100, 250),
        (280, 350),
        (500, 330),
        (720, 240),
        (900, 340),
        (1050, 250),
        (1050, 410),
    ]
    pygame.draw.polygon(surface, color, pts)


def draw_front_mountains(surface):
    color = (80, 125, 135) if state.is_day else (40, 18, 45)
    pts = [
        (-50, 410),
        (220, 240),
        (410, 350),
        (500, 370),
        (590, 350),
        (780, 220),
        (1050, 410),
    ]
    pygame.draw.polygon(surface, color, pts)


def draw_bright_sun(surface):
    sun_color = state.get_sun_color()
    midpoint_circle(
        surface, state.sun_x, state.sun_y, state.sun_radius, sun_color, fill=True
    )

    if state.is_day:
        num_rays = 12
        ray_len = state.sun_radius + 35
        if not state.is_paused:
            state.sun_ray_ang += 0.005

        for i in range(num_rays):
            angle = (2 * math.pi / num_rays) * i + state.sun_ray_ang
            start_x = state.sun_x + math.cos(angle) * (state.sun_radius + 5)
            start_y = state.sun_y + math.sin(angle) * (state.sun_radius + 5)
            end_x = state.sun_x + math.cos(angle) * ray_len
            end_y = state.sun_y + math.sin(angle) * ray_len
            dda_line(
                surface,
                start_x,
                start_y,
                end_x,
                end_y,
                (255, 255, 200),
                thickness=2,
            )


def draw_clouds(surface):
    if not state.show_clouds:
        return

    cloud_color = (255, 255, 255) if state.is_day else (200, 170, 180)

    for cloud in state.clouds:
        if not state.is_paused:
            cloud_speed = cloud[2] + (state.wind_force * 0.02)
            cloud[0] += cloud_speed

            if cloud[0] > WIDTH + 150:
                cloud[0] = -200
            elif cloud[0] < -250:
                cloud[0] = WIDTH + 100

        x, y = int(cloud[0]), int(cloud[1])
        w, h = cloud[3]

        midpoint_circle(surface, x, y, w, cloud_color, fill=True)
        midpoint_circle(surface, x + w // 2, y - h // 3, w, cloud_color, fill=True)
        midpoint_circle(surface, x + w, y, w, cloud_color, fill=True)


def draw_distant_forest(surface):
    forest_color = state.get_land_color()
    dark_shade = (
        max(0, forest_color[0] - 15),
        max(0, forest_color[1] - 30),
        max(0, forest_color[2] - 15),
    )

    pygame.draw.rect(surface, dark_shade, (0, 385, WIDTH, 25))

    for x in range(0, WIDTH + 30, 25):
        tree_h = 25 + ((x * 7) % 20)
        tree_w = 18 + ((x * 3) % 10)
        midpoint_circle(
            surface, x, 400 - tree_h // 2, tree_w, forest_color, fill=True
        )
        bresenham_line(surface, x, 410, x, 400 - tree_h // 2, dark_shade, thickness=2)


def draw_flowing_river(surface):
    time_ms = state.anim_time * 0.0015 * state.river_current

    river_color = (120, 180, 235) if state.is_day else (130, 40, 60)
    highlight_color = (230, 245, 255) if state.is_day else (255, 140, 70)

    top_bank_y, bottom_bank_y = 410, 480
    pygame.draw.rect(
        surface, river_color, (0, top_bank_y, WIDTH, bottom_bank_y - top_bank_y)
    )

    for i in range(22):
        speed = (1.0 + (i % 3) * 0.3) * state.river_current
        x1 = int((i * 55 + time_ms * speed * 25) % (WIDTH + 150)) - 100
        y = top_bank_y + (i * 3) % (bottom_bank_y - top_bank_y - 5)
        length = 30 + (i % 5) * 15 + int(state.river_current * 3)

        dist_from_sun_x = abs((x1 + length // 2) - state.sun_x)
        if dist_from_sun_x < 130:
            if state.is_day:
                current_highlight = (255, 255, 210)
            else:
                current_highlight = (255, max(0, 160 - int(dist_from_sun_x * 0.8)), 50)
            dda_line(
                surface,
                x1,
                y,
                x1 + length + 10,
                y,
                current_highlight,
                thickness=3,
            )
        else:
            dda_line(surface, x1, y, x1 + length, y, highlight_color, thickness=2)


def draw_foreground_land(surface):
    land_color = (45, 140, 50) if state.is_day else (25, 12, 20)
    pygame.draw.polygon(
        surface, land_color, [(0, 480), (WIDTH, 480), (WIDTH, HEIGHT), (0, HEIGHT)]
    )


def draw_animated_boat(surface):
    time_ms = state.anim_time

    if not state.is_paused:
        state.boat_x += 0.8 * state.river_current
        if state.boat_x > WIDTH + 150:
            state.boat_x = -150

    bobbing = math.sin(time_ms * 0.002 * state.river_current) * (
        1.5 * min(3.0, state.river_current)
    )
    bx = state.boat_x
    by = 440 + bobbing

    boat_color = state.get_boat_color()
    hood_color = (60, 35, 15) if state.is_day else (15, 8, 6)
    note_color = (30, 30, 30) if state.is_day else (255, 220, 130)
    splash_color = (240, 250, 255) if state.is_day else (220, 235, 255)

    hull_pts = [
        (bx, by),
        (bx + 18, by + 10),
        (bx + 68, by + 10),
        (bx + 88, by),
        (bx + 58, by - 3),
        (bx + 22, by - 3),
    ]
    pygame.draw.polygon(surface, boat_color, hull_pts)
    pygame.draw.polygon(
        surface,
        (30, 15, 5) if state.is_day else (10, 5, 2),
        hull_pts,
        width=1,
    )

    hood_pts = [
        (bx + 32, by - 3),
        (bx + 37, by - 18),
        (bx + 58, by - 18),
        (bx + 63, by - 3),
    ]
    pygame.draw.polygon(surface, hood_color, hood_pts)

    row_phase = time_ms * 0.003 * state.river_current
    lean_factor = math.sin(row_phase)

    man_x = bx + 22 + lean_factor * 2.5
    man_y = by - 5

    man_skin_color = (215, 145, 95) if state.is_day else boat_color
    man_shirt_color = (220, 50, 40) if state.is_day else boat_color
    hat_color = (190, 140, 60) if state.is_day else (40, 25, 10)
    oar_color = (60, 35, 15) if state.is_day else boat_color

    midpoint_circle(
        surface,
        man_x,
        man_y,
        4,
        (30, 80, 150) if state.is_day else boat_color,
        fill=True,
    )

    shirt_pts = [
        (man_x - 4, man_y - 2),
        (man_x + 4, man_y - 2),
        (man_x + 3 - lean_factor * 2, man_y - 12),
        (man_x - 3 - lean_factor * 2, man_y - 12),
    ]
    pygame.draw.polygon(surface, man_shirt_color, shirt_pts)

    head_x = man_x - lean_factor * 2
    head_y = man_y - 16
    midpoint_circle(surface, head_x, head_y, 5, man_skin_color, fill=True)

    hat_pts = [
        (head_x - 9, head_y - 1),
        (head_x, head_y - 8),
        (head_x + 9, head_y - 1),
    ]
    pygame.draw.polygon(surface, hat_color, hat_pts)

    hand_x = head_x - 1 + lean_factor * 2
    hand_y = head_y + 8

    bresenham_line(
        surface,
        head_x,
        head_y + 4,
        hand_x + 4,
        hand_y + 1,
        man_skin_color,
        thickness=2,
    )

    oar_tip_x = hand_x - 22 + math.cos(row_phase) * 15
    oar_tip_y = hand_y + 6 + math.sin(row_phase) * 9

    bresenham_line(
        surface,
        hand_x + 6,
        hand_y - 2,
        oar_tip_x,
        oar_tip_y,
        oar_color,
        thickness=2,
    )

    bresenham_line(
        surface,
        head_x,
        head_y + 5,
        hand_x - 1,
        hand_y + 1,
        man_skin_color,
        thickness=2,
    )

    blade_angle = math.atan2(oar_tip_y - hand_y, oar_tip_x - hand_x)
    blade_bx = oar_tip_x + math.cos(blade_angle) * 10
    blade_by = oar_tip_y + math.sin(blade_angle) * 10
    bresenham_line(
        surface,
        oar_tip_x,
        oar_tip_y,
        blade_bx,
        blade_by,
        oar_color,
        thickness=4,
    )

    if math.sin(row_phase) > 0.2:
        dda_line(
            surface,
            oar_tip_x - 5,
            oar_tip_y + 1,
            oar_tip_x + 5,
            oar_tip_y + 1,
            splash_color,
            thickness=1,
        )

    for n in range(3):
        t_note = ((time_ms * 0.001) + n * 0.8) % 2.5
        nx = man_x + 10 + t_note * 12
        ny = head_y - 8 - t_note * 20 + math.sin(t_note * 4) * 5

        if 0 <= nx < WIDTH and 0 <= ny < HEIGHT and t_note < 2.2:
            midpoint_circle(surface, nx, ny, 2, note_color, fill=True)
            bresenham_line(surface, nx + 2, ny, nx + 2, ny - 6, note_color, thickness=2)


def draw_heavy_rain(surface):
    if not state.is_raining:
        return

    rain_color = (210, 230, 255) if state.is_day else (180, 200, 240)
    ripple_color = (230, 245, 255)

    for drop in state.raindrops:
        if not state.is_paused:
            drop[0] += state.wind_force * 0.25
            drop[1] += drop[3]

        x, y, length, _ = drop
        end_x = x + (state.wind_force * 0.3)
        end_y = y + length

        dda_line(surface, x, y, end_x, end_y, rain_color, thickness=1)

        if 410 <= end_y <= 480 and random.random() < 0.2:
            dda_line(
                surface,
                end_x - 3,
                end_y,
                end_x + 3,
                end_y,
                ripple_color,
                thickness=1,
            )

        if not state.is_paused:
            if drop[1] > HEIGHT or drop[0] > WIDTH + 100 or drop[0] < -100:
                drop[1] = random.randint(-40, -10)
                drop[0] = random.randint(-100, WIDTH + 100)


def draw_real_palm_tree(surface, base_x, base_y, height, curve_bend, dynamic_sway):
    dynamic_bend = curve_bend + dynamic_sway
    palm_color = state.get_palm_color()
    trunk_color = (100, 70, 40) if state.is_day else (20, 10, 15)

    p0 = (base_x, base_y)
    p1 = (base_x + dynamic_bend * 0.6, base_y - height * 0.5)
    p2 = (base_x + dynamic_bend, base_y - height)

    top_x, top_y = p2[0], p2[1]

    steps = 18
    pts = [get_bezier_point(p0, p1, p2, i / steps) for i in range(steps + 1)]

    for i in range(len(pts) - 1):
        thickness = int(16 * (1 - (i / len(pts)) * 0.7))
        p_start, p_end = pts[i], pts[i + 1]
        bresenham_line(
            surface,
            p_start[0],
            p_start[1],
            p_end[0],
            p_end[1],
            trunk_color,
            thickness=max(2, thickness),
        )

    num_fronds = 16
    for i in range(num_fronds):
        angle_deg = (360 / num_fronds) * i + (i % 3) * 5 + (dynamic_sway * 0.5)
        rad = math.radians(angle_deg)
        length = 65 + (i % 4) * 12

        f0 = (top_x, top_y)
        f1 = (
            top_x + math.cos(rad) * length * 0.6,
            top_y + math.sin(rad) * length * 0.6,
        )
        f2 = (top_x + math.cos(rad) * length, top_y + math.sin(rad) * length + 25)

        stem_pts = [get_bezier_point(f0, f1, f2, s / 10) for s in range(11)]

        for k in range(len(stem_pts) - 1):
            bresenham_line(
                surface,
                stem_pts[k][0],
                stem_pts[k][1],
                stem_pts[k + 1][0],
                stem_pts[k + 1][1],
                palm_color,
                thickness=2,
            )

        for k in range(2, len(stem_pts) - 1):
            sx, sy = stem_pts[k]
            leaf_len = 18 * (1 - (k / len(stem_pts)) * 0.5)
            bresenham_line(
                surface, sx, sy, sx - 10, sy + leaf_len, palm_color, thickness=1
            )
            bresenham_line(
                surface, sx, sy, sx + 10, sy + leaf_len, palm_color, thickness=1
            )

    if state.is_day:
        fruit_color = (25, 15, 30)
        cap_color = (180, 140, 40)
        highlight = (230, 120, 20)
    else:
        fruit_color = (10, 5, 8)
        cap_color = (40, 25, 15)
        highlight = fruit_color

    fruit_offsets = [
        (-6, 8),
        (6, 9),
        (0, 14),
        (-10, 12),
        (10, 13),
        (-4, 19),
        (5, 20),
    ]
    for ox, oy in fruit_offsets:
        fx, fy = top_x + ox, top_y + oy
        midpoint_circle(surface, fx, fy - 2, 4, cap_color, fill=True)
        midpoint_circle(surface, fx, fy, 5, fruit_color, fill=True)
        if state.is_day:
            midpoint_circle(surface, fx, fy + 2, 2, highlight, fill=True)


def draw_bottom_foreground_kashful(surface, dynamic_sway_offset):
    time_sec = state.anim_time * 0.0015
    base_y = HEIGHT
    start_x = -20

    white_fluff = (255, 255, 255) if state.is_day else (250, 255, 250)
    light_yellow = (250, 245, 200) if state.is_day else (235, 225, 160)

    num_kash = 95
    for i in range(num_kash):
        x = start_x + (i * 11) + ((i * 5) % 7)
        plume_height = 80 + ((i * 13) % 45)

        sway = math.sin(time_sec + i * 0.25) * 4 + dynamic_sway_offset

        p0 = (x, base_y)
        p1 = (x + sway * 0.4, base_y - plume_height * 0.5)
        p2 = (x + sway, base_y - plume_height)

        steps = 14
        stem_pts = [
            get_bezier_point(p0, p1, p2, s / steps) for s in range(steps + 1)
        ]

        for idx, (nx, ny) in enumerate(stem_pts):
            progress = idx / len(stem_pts)
            spike_len = (1.2 - progress * 0.6) * 16

            for side in [-1, 1]:
                num_spikes = 3
                for sp in range(num_spikes):
                    angle = math.radians(-90 + side * (30 + sp * 15) + (sway * 0.2))
                    length = spike_len + (sp % 2) * 3
                    end_x = nx + math.cos(angle) * length
                    end_y = ny + math.sin(angle) * length
                    color = white_fluff if (idx + sp) % 3 != 0 else light_yellow
                    dda_line(surface, nx, ny, end_x, end_y, color, thickness=1)


def draw_animated_birds(surface):
    time_ms = state.anim_time
    wing_flap = math.sin(time_ms * 0.006) * 6
    bird_color = (20, 20, 20) if state.is_day else state.get_land_color()

    bird_offsets = [
        (-80, -20),
        (-50, -40),
        (-10, -25),
        (30, -35),
        (70, -10),
        (-30, -60),
        (10, -50),
        (90, -40),
    ]

    if not state.is_paused:
        state.birds_x += (1.5 + (state.wind_force * 0.02)) * state.bird_dir

        if state.bird_dir == 1 and state.birds_x > WIDTH + 400:
            state.birds_x = -500
        elif state.bird_dir == -1 and state.birds_x < -WIDTH - 400:
            state.birds_x = 500

    base_x = 420 + state.birds_x
    base_y = 150 + state.birds_y

    for ox, oy in bird_offsets:
        bx, by = base_x + ox, base_y + oy
        if -150 <= bx <= WIDTH + 150:
            d = state.bird_dir
            bresenham_line(
                surface,
                bx - (12 * d),
                by - 6 + wing_flap,
                bx,
                by,
                bird_color,
                thickness=2,
            )
            bresenham_line(
                surface,
                bx,
                by,
                bx + (12 * d),
                by - 6 + wing_flap,
                bird_color,
                thickness=2,
            )


# --- Main Game Loop ---
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_n:
                state.is_day = not state.is_day
                state.sun_y = 140 if state.is_day else 380
            elif event.key == pygame.K_r:
                state.is_raining = not state.is_raining
            elif event.key == pygame.K_c:
                state.show_clouds = not state.show_clouds
            elif event.key == pygame.K_SPACE:
                state.is_paused = not state.is_paused
            elif event.key == pygame.K_q:
                state.bird_dir = -1
            elif event.key == pygame.K_w:
                state.bird_dir = 1

    keys = pygame.key.get_pressed()

    if keys[pygame.K_d]:
        state.wind_force = min(35.0, state.wind_force + 0.8)
    if keys[pygame.K_a]:
        state.wind_force = max(-35.0, state.wind_force - 0.8)

    if not state.is_paused:
        if keys[pygame.K_UP]:
            state.sun_y = max(50, state.sun_y - 2.0)
        if keys[pygame.K_DOWN]:
            state.sun_y = min(410, state.sun_y + 2.0)

        if keys[pygame.K_RIGHT]:
            state.river_current = min(4.5, state.river_current + 0.05)
        if keys[pygame.K_LEFT]:
            state.river_current = max(0.2, state.river_current - 0.05)

        state.anim_time += clock.get_time()

    t_ticks = state.anim_time
    palm_wind_sway = (math.sin(t_ticks * 0.0015) * 4) + (state.wind_force * 0.8)
    kashful_wind_sway = state.wind_force * 1.0

    # --- RENDER LAYERS ---
    draw_background(screen)
    draw_back_mountains(screen)
    draw_bright_sun(screen)
    draw_front_mountains(screen)
    draw_clouds(screen)
    draw_distant_forest(screen)
    draw_flowing_river(screen)
    draw_animated_boat(screen)
    draw_animated_birds(screen)
    draw_foreground_land(screen)

    lx, ly = state.left_tree_x, state.left_tree_y
    draw_real_palm_tree(screen, lx - 40, ly, 200, -45, palm_wind_sway)
    draw_real_palm_tree(screen, lx + 20, ly + 10, 250, -25, palm_wind_sway * 0.8)
    draw_real_palm_tree(screen, lx + 80, ly + 15, 210, 35, palm_wind_sway * 1.1)

    rx, ry = state.right_tree_x, state.right_tree_y
    draw_real_palm_tree(screen, rx - 30, ry, 260, -35, palm_wind_sway)
    draw_real_palm_tree(screen, rx + 40, ry + 10, 210, 25, palm_wind_sway * 0.9)
    draw_real_palm_tree(screen, rx + 100, ry + 15, 240, 45, palm_wind_sway * 1.2)

    draw_bottom_foreground_kashful(screen, kashful_wind_sway)
    draw_heavy_rain(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
