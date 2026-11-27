"""
Artistic Math Visualizer: Plot button + equation input + function plotter.
Uses Python's built-in Tkinter for its drawing window.

How it works:
  1. The canvas shows a title, axes, and a "Plot" button.
  2. Click the button, then type an equation in the TERMINAL (e.g. x^2, sin(x), 1/x).
  3. The curve is drawn. Click the button again for another equation.
  4. Type  q  at the prompt to quit.
"""

import ast
import math
from tk_canvas import Canvas

# ------------------------------------------------------------------ layout
CANVAS_WIDTH = 600
CANVAS_HEIGHT = 500
SCALE = 50                                # pixels per math unit
ORIGIN_X = CANVAS_WIDTH // 2
ORIGIN_Y = CANVAS_HEIGHT // 2
BUTTON = (480, 10, 590, 50)               # left, top, right, bottom
TITLE_POS = (12, 14)

# ------------------------------------------------------------- safe parser
FUNCS = {name: getattr(math, name) for name in
         ["sin", "cos", "tan", "sqrt", "exp", "log", "atan",
          "sinh", "cosh", "tanh", "floor", "ceil"]}
FUNCS["abs"] = abs
CONSTS = {"pi": math.pi, "e": math.e}
ALLOWED = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Call, ast.Name,
           ast.Load, ast.Constant, ast.Add, ast.Sub, ast.Mult,
           ast.Div, ast.Pow, ast.USub, ast.UAdd, ast.Mod)


def compile_expr(text):
    """Turn user text into a function f(x). Raises ValueError if unsafe/unknown."""
    tree = ast.parse(text.replace("^", "**"), mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, ALLOWED):
            raise ValueError("unsupported syntax")
        if isinstance(node, ast.Constant) and not isinstance(node.value, (int, float)):
            raise ValueError("only numbers allowed")
        if isinstance(node, ast.Name) and not (
                node.id in FUNCS or node.id in CONSTS or node.id == "x"):
            raise ValueError(f"unknown name: {node.id}")
        if isinstance(node, ast.Call) and not (
                isinstance(node.func, ast.Name) and node.func.id in FUNCS):
            raise ValueError("unknown function")
    code = compile(tree, "<expr>", "eval")

    def f(x):
        env = dict(FUNCS)
        env.update(CONSTS)
        env["x"] = x
        try:
            value = float(eval(code, {"__builtins__": {}}, env))
            return value if math.isfinite(value) else None
        except Exception:
            return None                   # undefined here, e.g. 1/0
    return f


# ----------------------------------------------------------------- drawing
def inside(x, y, box):
    left, top, right, bottom = box
    return left <= x <= right and top <= y <= bottom


def draw_axes(canvas):
    canvas.create_line(0, ORIGIN_Y, CANVAS_WIDTH, ORIGIN_Y, color="gray")
    canvas.create_line(ORIGIN_X, 0, ORIGIN_X, CANVAS_HEIGHT, color="gray")
    # tick marks and numbers at every whole unit
    for k in range(-(ORIGIN_X // SCALE), ORIGIN_X // SCALE + 1):
        if k == 0:
            continue
        sx = ORIGIN_X + k * SCALE
        canvas.create_line(sx, ORIGIN_Y - 3, sx, ORIGIN_Y + 3, color="gray")
        canvas.create_text(sx - 3, ORIGIN_Y + 6, text=str(k),
                           font_size=8, color="gray")


def draw_interface(canvas, status=""):
    left, top, right, bottom = BUTTON
    canvas.create_rectangle(left, top, right, bottom, color="lightblue")
    canvas.create_text(left + 38, top + 12, text="Plot", font_size=16, color="black")
    canvas.create_text(TITLE_POS[0], TITLE_POS[1], text="Artistic Math Visualizer",
                       font_size=12, color="black")
    if status:
        canvas.create_text(12, CANVAS_HEIGHT - 22, text=status,
                           font_size=11, color="black")


def plot_function(canvas, f, label):
    """Redraw everything: clear, axes, curve, interface (so the button stays)."""
    canvas.clear()
    draw_axes(canvas)

    prev = None
    for px in range(-ORIGIN_X, CANVAS_WIDTH - ORIGIN_X + 1):
        y = f(px / SCALE)
        if y is None:
            prev = None                   # gap where the function is undefined
            continue
        sx = ORIGIN_X + px
        sy = ORIGIN_Y - y * SCALE
        on_screen = -CANVAS_HEIGHT < sy < 2 * CANVAS_HEIGHT
        # skip off-screen points and huge jumps (asymptotes like tan or 1/x)
        if prev and on_screen and abs(sy - prev[1]) < CANVAS_HEIGHT:
            canvas.create_line(prev[0], prev[1], sx, sy, color="blue")
        prev = (sx, sy) if on_screen else None

    draw_interface(canvas, status=f"y = {label}")


# -------------------------------------------------------------------- main
def main():
    canvas = Canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    draw_axes(canvas)
    draw_interface(canvas, status="Click Plot, then type an equation in the terminal")
    print("Click the Plot button on the canvas.")

    while True:
        canvas.wait_for_click()
        x, y = canvas.get_mouse_x(), canvas.get_mouse_y()
        if not inside(x, y, BUTTON):
            continue                      # ignore clicks outside the button

        text = input("y = (type an equation in x, or q to quit): ").strip()
        if text.lower() == "q":
            break
        try:
            f = compile_expr(text)
        except Exception as err:
            print("  Could not read that:", err)
            continue
        plot_function(canvas, f, text)
        print("Plotted. Click Plot again for another equation.")


if __name__ == "__main__":
    main()
