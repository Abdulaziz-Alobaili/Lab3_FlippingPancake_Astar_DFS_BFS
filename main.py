import tkinter as tk
from tkinter import messagebox
import collections
import heapq


# --- Algorithms ---

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


# --- Tkinter GUI ---

class MultiPancakeVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pancake Sorting - Simultaneous Comparison")

        # Configuration
        self.algos = ["BFS", "DFS", "A*"]
        self.canvas_w = 320
        self.canvas_h = 350
        self.anim_speed = 400  # ms per animation phase

        # State tracking
        self.current_stacks = {}
        self.paths = {}
        self.nodes_expanded = {}
        self.anim_steps = {}

        # UI Top Frame
        ui_frame = tk.Frame(root, padx=10, pady=10)
        ui_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(ui_frame, text="Stack (comma-separated):", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.stack_entry = tk.Entry(ui_frame, width=20, font=("Arial", 12))
        self.stack_entry.insert(0, "3, 1, 4, 2")
        self.stack_entry.pack(side=tk.LEFT, padx=10)

        self.solve_btn = tk.Button(ui_frame, text="Run All Algorithms", bg="#4CAF50", fg="white",
                                   font=("Arial", 10, "bold"), command=self.start_solving)
        self.solve_btn.pack(side=tk.LEFT, padx=10)

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(ui_frame, textvariable=self.status_var, fg="blue", font=("Arial", 10)).pack(side=tk.LEFT, padx=20)

        # Canvases Frame
        self.canvas_frame = tk.Frame(root, padx=10, pady=10)
        self.canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.canvases = {}
        self.label_vars = {}

        for algo in self.algos:
            col_frame = tk.Frame(self.canvas_frame, bd=2, relief=tk.GROOVE)
            col_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH, expand=True)

            self.label_vars[algo] = tk.StringVar(value=f"{algo}\nWaiting...")
            tk.Label(col_frame, textvariable=self.label_vars[algo], font=("Arial", 11, "bold"), height=3).pack(pady=5)

            c = tk.Canvas(col_frame, width=self.canvas_w, height=self.canvas_h, bg="white")
            c.pack(padx=10, pady=10)
            self.canvases[algo] = c

        # Draw initial state on all
        self.reset_stacks([3, 1, 4, 2])

    def reset_stacks(self, start_state):
        for algo in self.algos:
            self.current_stacks[algo] = list(start_state)
            self.draw_stack(algo)

    def update_labels(self):
        for algo in self.algos:
            if algo not in self.paths: continue

            step = self.anim_steps[algo]
            total_flips = len(self.paths[algo])
            nodes = self.nodes_expanded[algo]

            if step >= total_flips:
                status_text = "✅ Done"
            else:
                status_text = "🔄 Animating..."

            self.label_vars[algo].set(
                f"{algo} Algorithm\n"
                f"Flips: {step} / {total_flips} | Nodes: {nodes}\n"
                f"{status_text}"
            )

    def draw_stack(self, algo, spatula_index=None):
        canvas = self.canvases[algo]
        canvas.delete("all")

        stack = self.current_stacks[algo]
        if not stack: return

        n = len(stack)
        max_val = max(stack)
        pancake_height = 25
        max_width = self.canvas_w - 60

        # Draw plate
        plate_y = self.canvas_h - 30
        canvas.create_line(10, plate_y, self.canvas_w - 10, plate_y, width=4, fill="gray")

        # Draw pancakes
        for i, val in enumerate(stack):
            width = (val / max_val) * max_width
            x0 = (self.canvas_w - width) / 2
            x1 = x0 + width
            y1 = plate_y - ((n - i) * pancake_height)
            y0 = y1 - (pancake_height - 4)

            # Green if in correct final sorted position for its value
            color = "#f4a460" if val != i + 1 else "#3cb371"
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="saddlebrown", width=2)
            canvas.create_text((x0 + x1) / 2, (y0 + y1) / 2, text=str(val), font=("Arial", 11, "bold"))

            # Draw Spatula
            if spatula_index is not None and i == spatula_index - 1:
                sy = y1 + 2
                canvas.create_line(5, sy, self.canvas_w - 5, sy, width=3, fill="red", dash=(4, 4))
                canvas.create_text(30, sy - 10, text="Spatula", fill="red", font=("Arial", 9, "bold"))

    def start_solving(self):
        try:
            start_state = tuple(int(x.strip()) for x in self.stack_entry.get().split(","))
        except ValueError:
            messagebox.showerror("Error", "Please enter valid comma-separated integers.")
            return

        self.solve_btn.config(state=tk.DISABLED)
        self.status_var.set("Solving paths (this is fast)...")
        self.root.update()

        self.reset_stacks(start_state)

        # 1. Solve all paths
        self.paths["BFS"], self.nodes_expanded["BFS"] = solve_bfs(start_state)
        self.paths["DFS"], self.nodes_expanded["DFS"] = solve_dfs(start_state)
        self.paths["A*"], self.nodes_expanded["A*"] = solve_astar(start_state)

        for algo in self.algos:
            if self.paths[algo] is None:
                messagebox.showerror("Error", f"No solution found for {algo}")
                self.solve_btn.config(state=tk.NORMAL)
                return
            self.anim_steps[algo] = 0

        self.status_var.set("Animating...")
        self.update_labels()

        # 2. Start global animation loop
        self.animate_spatulas()

    def animate_spatulas(self):
        animating_any = False

        for algo in self.algos:
            step = self.anim_steps[algo]
            path = self.paths[algo]

            if step < len(path):
                animating_any = True
                flip_index = path[step]
                self.draw_stack(algo, spatula_index=flip_index)

        if animating_any:
            self.root.after(self.anim_speed, self.animate_flips)
        else:
            self.status_var.set("All animations complete!")
            self.solve_btn.config(state=tk.NORMAL)

    def animate_flips(self):
        for algo in self.algos:
            step = self.anim_steps[algo]
            path = self.paths[algo]

            if step < len(path):
                flip_index = path[step]
                # Apply the flip
                self.current_stacks[algo][:flip_index] = reversed(self.current_stacks[algo][:flip_index])
                self.draw_stack(algo)

                self.anim_steps[algo] += 1

        self.update_labels()
        self.root.after(self.anim_speed, self.animate_spatulas)


if __name__ == "__main__":
    root = tk.Tk()
    app = MultiPancakeVisualizer(root)
    root.mainloop()