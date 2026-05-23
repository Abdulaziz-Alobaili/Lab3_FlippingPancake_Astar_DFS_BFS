import tkinter as tk
from tkinter import messagebox
import collections
import heapq




def is_goal(state):
    return list(state) == sorted(state)


def get_successors(state):
    successors = []
    for i in range(2, len(state) + 1):
        new_state = state[:i][::-1] + state[i:]
        successors.append((new_state, i))
    return successors


def gap_heuristic(state):
    gaps = 0
    n = len(state)
    for i in range(n - 1):
        if abs(state[i] - state[i + 1]) > 1:
            gaps += 1
    if state[-1] != n:
        gaps += 1
    return gaps


def solve_bfs(start_state):
    queue = collections.deque([(start_state, [])])
    visited = {start_state}
    nodes = 0
    while queue:
        state, path = queue.popleft()
        nodes += 1
        if is_goal(state): return path, nodes
        for next_state, flip_index in get_successors(state):
            if next_state not in visited:
                visited.add(next_state)
                queue.append((next_state, path + [flip_index]))
    return None, nodes


def solve_dfs(start_state):
    stack = [(start_state, [])]
    visited = {start_state}
    nodes = 0
    while stack:
        state, path = stack.pop()
        nodes += 1
        if is_goal(state): return path, nodes
        for next_state, flip_index in get_successors(state):
            if next_state not in visited:
                visited.add(next_state)
                stack.append((next_state, path + [flip_index]))
    return None, nodes


def solve_astar(start_state):
    pq = []
    counter = 0
    g_score = {start_state: 0}
    heapq.heappush(pq, (gap_heuristic(start_state), counter, start_state, []))
    nodes = 0

    while pq:
        f, _, state, path = heapq.heappop(pq)
        nodes += 1
        if is_goal(state): return path, nodes
        for next_state, flip_index in get_successors(state):
            new_g = g_score[state] + 1
            if next_state not in g_score or new_g < g_score[next_state]:
                g_score[next_state] = new_g
                counter += 1
                heapq.heappush(pq, (new_g + gap_heuristic(next_state), counter, next_state, path + [flip_index]))
    return None, nodes


# Tkinter

class PancakeVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pancake Sorting Visualizer")

        # UI Frame
        ui_frame = tk.Frame(root, padx=10, pady=10)
        ui_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(ui_frame, text="Stack (comma-separated):").grid(row=0, column=0, sticky=tk.W)
        self.stack_entry = tk.Entry(ui_frame, width=20)
        self.stack_entry.insert(0, "3, 1, 4, 2")
        self.stack_entry.grid(row=0, column=1, padx=5)

        tk.Label(ui_frame, text="Algorithm:").grid(row=0, column=2, sticky=tk.W)
        self.algo_var = tk.StringVar(value="A*")
        tk.OptionMenu(ui_frame, self.algo_var, "A*", "BFS", "DFS").grid(row=0, column=3, padx=5)

        self.solve_btn = tk.Button(ui_frame, text="Solve & Animate", command=self.start_solving)
        self.solve_btn.grid(row=0, column=4, padx=10)

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(ui_frame, textvariable=self.status_var, fg="blue").grid(row=1, column=0, columnspan=5, sticky=tk.W,
                                                                         pady=5)

        # Canvas
        self.canvas_width = 400
        self.canvas_height = 400
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(padx=10, pady=10)

        self.current_stack = []
        self.draw_stack([3, 1, 4, 2])

    def draw_stack(self, stack, spatula_index=None):
        self.canvas.delete("all")
        if not stack: return

        n = len(stack)
        max_val = max(stack)

        pancake_height = 30
        max_width = self.canvas_width - 100

        # Draw plate
        plate_y = self.canvas_height - 30
        self.canvas.create_line(20, plate_y, self.canvas_width - 20, plate_y, width=4, fill="gray")

        # Draw pancakes
        for i, val in enumerate(stack):
            width = (val / max_val) * max_width
            x0 = (self.canvas_width - width) / 2
            x1 = x0 + width
            # Calculate Y from bottom up
            y1 = plate_y - ((n - i) * pancake_height)
            y0 = y1 - (pancake_height - 4)

            # Pancake color
            color = "#f4a460" if val != i + 1 else "#3cb371"  # Green if in correct sorted position
            self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="saddlebrown", width=2)
            self.canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=str(val), font=("Arial", 12, "bold"))

            # Draw Spatula
            if spatula_index is not None and i == spatula_index - 1:
                sy = y1 + 2
                self.canvas.create_line(10, sy, self.canvas_width - 10, sy, width=3, fill="red", dash=(4, 4))
                self.canvas.create_text(40, sy - 10, text="Spatula", fill="red")

    def start_solving(self):
        try:
            # Parse input
            start_state = tuple(int(x.strip()) for x in self.stack_entry.get().split(","))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid comma-separated integers.")
            return

        self.current_stack = list(start_state)
        self.draw_stack(self.current_stack)
        algo = self.algo_var.get()

        self.status_var.set(f"Solving using {algo}...")
        self.root.update()

        path, nodes = None, 0
        if algo == "BFS":
            path, nodes = solve_bfs(start_state)
        elif algo == "DFS":
            path, nodes = solve_dfs(start_state)
        elif algo == "A*":
            path, nodes = solve_astar(start_state)

        if path is None:
            self.status_var.set("No solution found.")
            return

        self.solve_btn.config(state=tk.DISABLED)
        self.status_var.set(f"Found {len(path)} flips. Nodes expanded: {nodes}. Animating...")

        # Start animation loop
        self.animate_path(path, 0)

    def animate_path(self, path, step):
        if step >= len(path):
            self.status_var.set(self.status_var.get().replace("Animating...", "Done!"))
            self.solve_btn.config(state=tk.NORMAL)
            self.draw_stack(self.current_stack)
            return

        flip_index = path[step]

        # 1. Draw spatula
        self.draw_stack(self.current_stack, spatula_index=flip_index)

        # 2. Wait, then apply flip and redraw
        def execute_flip():
            self.current_stack[:flip_index] = reversed(self.current_stack[:flip_index])
            self.draw_stack(self.current_stack)

            # Schedule next step
            self.root.after(800, lambda: self.animate_path(path, step + 1))

        self.root.after(800, execute_flip)



root = tk.Tk()
app = PancakeVisualizer(root)
root.mainloop()