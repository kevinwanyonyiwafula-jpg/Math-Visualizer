import tkinter as tk


class Canvas:
    def __init__(self, width, height):
        self._root = tk.Tk()
        self._root.title("Math Visualizer")
        self._canvas = tk.Canvas(
            self._root,
            width=width,
            height=height,
            highlightthickness=0,
        )
        self._canvas.pack()
        self._last_click = (0, 0)
        self._click_count = tk.IntVar(master=self._root, value=0)
        self._closed = False
        self._canvas.bind("<Button-1>", self._record_click)
        self._root.protocol("WM_DELETE_WINDOW", self._close)

    def _record_click(self, event):
        self._last_click = (event.x, event.y)
        self._click_count.set(self._click_count.get() + 1)

    def _close(self):
        self._closed = True
        self._click_count.set(self._click_count.get() + 1)

    def create_line(self, x1, y1, x2, y2, color="black"):
        return self._canvas.create_line(x1, y1, x2, y2, fill=color)

    def create_rectangle(self, left, top, right, bottom, color="black"):
        return self._canvas.create_rectangle(
            left, top, right, bottom, fill=color, outline=color
        )

    def create_text(self, x, y, text, font_size=12, color="black"):
        return self._canvas.create_text(
            x,
            y,
            text=text,
            anchor="nw",
            font=("TkDefaultFont", font_size),
            fill=color,
        )

    def create_oval(self, left, top, right, bottom, color="black"):
        return self._canvas.create_oval(
            left, top, right, bottom, fill=color, outline=color
        )

    def clear(self):
        self._canvas.delete("all")

    def delete(self, shape):
        self._canvas.delete(shape)

    def update(self):
        if not self._closed:
            self._root.update_idletasks()

    def wait_for_click(self):
        if self._closed:
            self._root.destroy()
            raise SystemExit

        self.update()
        self._root.wait_variable(self._click_count)
        if self._closed:
            self._root.destroy()
            raise SystemExit

    def get_mouse_x(self):
        return self._last_click[0]

    def get_mouse_y(self):
        return self._last_click[1]
