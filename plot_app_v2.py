"""
Artistic Math Visualizer v2: overlay curves + tangent animation.
Uses Python's built-in Tkinter for its drawing window.

Requires plot_app.py in the same folder (it provides the safe equation
parser, axes, and layout constants).

Buttons on the canvas:
  Plot     type an equation in the terminal; it is ADDED as a new colored curve
  Tangent  animates a tangent line sliding along the most recent curve
  Clear    removes all curves

At the Plot prompt, type  q  to quit.
"""

import time
from tk_canvas import Canvas
from plot_app import (CANVAS_WIDTH, CANVAS_HEIGHT, SCALE, ORIGIN_X, ORIGIN_Y,
                      TITLE_POS, compile_expr, draw_axes, inside)

# left, top, right, bottom
BUTTONS = {
    "Plot": (330, 10, 410, 50),
    "Tangent": (420, 10, 500, 50),
    "Clear": (510, 10, 590, 50),
}
COLORS = ["blue", "red", "green", "purple"]
MAX_CURVES = len(COLORS)


# ----------------------------------------------------------------- drawing
def draw_buttons(canvas):
    for name, (left, top, right, bottom) in BUTTONS.items():
        canvas.create_rectangle(left, top, right, bottom, color="lightblue")
        canvas.create_text(left + 8, top + 12, text=name,
                           font_size=14, color="black")


def draw_curve(canvas, f, color):
    prev = None
    for px in range(-ORIGIN_X, CANVAS_WIDTH - ORIGIN_X + 1):
        y = f(px / SCALE)
        if y is None:
            prev = None                    # undefined here (e.g. 1/0)
            continue
        sx, sy = ORIGIN_X + px, ORIGIN_Y - y * SCALE
        on_screen = -CANVAS_HEIGHT < sy < 2 * CANVAS_HEIGHT
        if prev and on_screen and abs(sy - prev[1]) < CANVAS_HEIGHT:
            canvas.create_line(prev[0], prev[1], sx, sy, color=color)
        prev = (sx, sy) if on_screen else None


def redraw(canvas, curves, status=""):
    """Clear everything, then draw axes, all curves, buttons, legend."""
    canvas.clear()
    draw_axes(canvas)
    for label, f, color in curves:
        draw_curve(canvas, f, color)
    canvas.create_text(TITLE_POS[0], TITLE_POS[1], text="Artistic Math Visualizer",
                       font_size=12, color="black")
    draw_buttons(canvas)
    for i, (label, f, color) in enumerate(curves):
        canvas.create_text(12, CANVAS_HEIGHT - 20 * (len(curves) - i),
                           text=f"y = {label}", font_size=12, color=color)
    if status:
        canvas.create_text(12, 34, text=status, font_size=11, color="black")


# --------------------------------------------------------------- animation
def animate_tangent(canvas, f):
    """Slide a tangent line along the curve. Slope = numerical derivative."""
    h = 1e-4
    half = 1.0                             # tangent extends 1 unit each side
    for px in range(-ORIGIN_X, CANVAS_WIDTH - ORIGIN_X + 1, 2):
        x = px / SCALE
        y, y_up, y_down = f(x), f(x + h), f(x - h)
        if y is None or y_up is None or y_down is None:
            continue
        slope = (y_up - y_down) / (2 * h)
        sy = ORIGIN_Y - y * SCALE
        if not (0 <= sy <= CANVAS_HEIGHT) or abs(slope) > 10:
            continue                       # off screen or too steep to show
        sx = ORIGIN_X + px
        shapes = [
            canvas.create_line(sx - half * SCALE, ORIGIN_Y - (y - slope * half) * SCALE,
                               sx + half * SCALE, ORIGIN_Y - (y + slope * half) * SCALE,
                               color="orange"),
            canvas.create_oval(sx - 5, sy - 5, sx + 5, sy + 5, color="red"),
            canvas.create_text(12, 54, text=f"x = {x:5.2f}   slope = {slope:6.2f}",
                               font_size=12, color="black"),
        ]
        canvas.update()
        time.sleep(1 / 60)
        for shape in shapes:               # erase this frame before the next
            canvas.delete(shape)
        canvas.update()


# -------------------------------------------------------------------- main
def main():
    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    curves = []                            # list of (label, f, color)
    redraw(canvas, curves, "Click Plot, then type an equation in the terminal")
    print("Click a button on the canvas.")

    while True:
        canvas.wait_for_click()
        x, y = canvas.get_mouse_x(), canvas.get_mouse_y()
        clicked = next((name for name, box in BUTTONS.items()
                        if inside(x, y, box)), None)
        if clicked is None:
            continue

        if clicked == "Plot":
            text = input("y = (equation in x, or q to quit): ").strip()
            if text.lower() == "q":
                break
            try:
                f = compile_expr(text)
            except Exception as err:
                print("  Could not read that:", err)
                continue
            if len(curves) == MAX_CURVES:
                curves.pop(0)              # drop the oldest curve
            used = {c[2] for c in curves}
            color = next(c for c in COLORS if c not in used)
            curves.append((text, f, color))
            redraw(canvas, curves)
            print(f"Added '{text}' ({color}). {len(curves)} curve(s) shown.")

        elif clicked == "Tangent":
            if not curves:
                print("Plot a curve first.")
                continue
            label, f, color = curves[-1]
            print(f"Tangent animation on y = {label}")
            animate_tangent(canvas, f)
            redraw(canvas, curves)

        elif clicked == "Clear":
            curves = []
            redraw(canvas, curves, "Cleared. Click Plot to start again")
            print("Cleared.")


if __name__ == "__main__":
    main()
