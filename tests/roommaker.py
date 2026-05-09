import tkinter as tk
from tkinter import messagebox, filedialog
import json

class DraggableResizable:
    HANDLE_SIZE = 8

    def __init__(self, canvas, x1, y1, x2, y2, fill="lightgrey", label="", on_update=None):
        self.canvas = canvas
        self.label = label
        self.on_update = on_update
        self.rect = canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="black", width=2)
        self.text = canvas.create_text((x1+x2)/2, (y1+y2)/2, text=f"{label}\n{int(x2-x1)}x{int(y2-y1)}")
        self.fill = fill
        self.handles = {}
        self._drag_data = {"x":0, "y":0, "action": None, "handle": None}
        self.create_handles()
        self.bind_events()

    def create_handles(self):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        self.handles['tl'] = self.canvas.create_rectangle(x1-4, y1-4, x1+4, y1+4, fill="red")
        self.handles['tr'] = self.canvas.create_rectangle(x2-4, y1-4, x2+4, y1+4, fill="red")
        self.handles['bl'] = self.canvas.create_rectangle(x1-4, y2-4, x1+4, y2+4, fill="red")
        self.handles['br'] = self.canvas.create_rectangle(x2-4, y2-4, x2+4, y2+4, fill="red")

    def bind_events(self):
        for tag in [self.rect, self.text]:
            self.canvas.tag_bind(tag, "<ButtonPress-1>", self.on_press)
            self.canvas.tag_bind(tag, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(tag, "<ButtonRelease-1>", self.on_release)
            self.canvas.tag_bind(tag, "<Button-3>", self.edit_popup)
        for handle in self.handles.values():
            self.canvas.tag_bind(handle, "<ButtonPress-1>", self.on_handle_press)
            self.canvas.tag_bind(handle, "<B1-Motion>", self.on_handle_drag)
            self.canvas.tag_bind(handle, "<ButtonRelease-1>", self.on_release)

    def update_handles(self):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        self.canvas.coords(self.handles['tl'], x1-4, y1-4, x1+4, y1+4)
        self.canvas.coords(self.handles['tr'], x2-4, y1-4, x2+4, y1+4)
        self.canvas.coords(self.handles['bl'], x1-4, y2-4, x1+4, y2+4)
        self.canvas.coords(self.handles['br'], x2-4, y2-4, x2+4, y2+4)
        self.canvas.coords(self.text, (x1+x2)/2, (y1+y2)/2)
        width = int(x2 - x1)
        height = int(y2 - y1)
        self.canvas.itemconfig(self.text, text=f"{self.label}\n{width}x{height}")

    # Dragging
    def on_press(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._drag_data["action"] = "move"

    def on_drag(self, event):
        if self._drag_data["action"] != "move":
            return
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.text, dx, dy)
        for handle in self.handles.values():
            self.canvas.move(handle, dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_release(self, event):
        self._drag_data["action"] = None
        self._drag_data["handle"] = None
        if self.on_update:
            x1, y1, x2, y2 = self.canvas.coords(self.rect)
            self.on_update(x1, y1, x2, y2)

    # Resize
    def on_handle_press(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        self._drag_data["action"] = "resize"
        self._drag_data["handle"] = event.widget.find_withtag("current")[0]

    def on_handle_drag(self, event):
        coords = self.canvas.coords(self.rect)
        x1, y1, x2, y2 = coords
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        handle = self._drag_data.get("handle")

        if handle == self.handles['tl']:
            x1 += dx; y1 += dy
        elif handle == self.handles['tr']:
            x2 += dx; y1 += dy
        elif handle == self.handles['bl']:
            x1 += dx; y2 += dy
        elif handle == self.handles['br']:
            x2 += dx; y2 += dy

        self.canvas.coords(self.rect, x1, y1, x2, y2)
        self.update_handles()
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        if self.on_update:
            self.on_update(x1, y1, x2, y2)

    # Edit popup
    def edit_popup(self, event):
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        popup = tk.Toplevel()
        popup.title("Edit Object")
        tk.Label(popup, text="Width:").grid(row=0, column=0)
        tk.Label(popup, text="Height:").grid(row=1, column=0)
        tk.Label(popup, text="Name:").grid(row=2, column=0)

        width_entry = tk.Entry(popup); width_entry.insert(0, int(x2-x1)); width_entry.grid(row=0, column=1)
        height_entry = tk.Entry(popup); height_entry.insert(0, int(y2-y1)); height_entry.grid(row=1, column=1)
        name_entry = tk.Entry(popup); name_entry.insert(0, self.label); name_entry.grid(row=2, column=1)

        def submit():
            try:
                w = int(width_entry.get())
                h = int(height_entry.get())
                name = name_entry.get()
                self.label = name
                self.canvas.coords(self.rect, x1, y1, x1+w, y1+h)
                self.update_handles()
                if self.on_update:
                    self.on_update(x1, y1, x1+w, y1+h)
                popup.destroy()
            except:
                messagebox.showerror("Error", "Enter valid numbers")
        tk.Button(popup, text="Apply", command=submit).grid(row=3, columnspan=2)


class MapEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("JRPG Multi-Floor Editor")
        self.canvas = tk.Canvas(root, width=800, height=600, bg="white")
        self.canvas.pack(fill="both", expand=True)

        self.floors = []
        self.current_floor = 0

        frame = tk.Frame(root); frame.pack()
        tk.Button(frame, text="Add Room", command=self.add_room).pack(side="left")
        tk.Button(frame, text="Add Element", command=self.add_element).pack(side="left")
        tk.Button(frame, text="Add Floor", command=self.add_floor).pack(side="left")
        tk.Button(frame, text="Prev Floor", command=self.prev_floor).pack(side="left")
        tk.Button(frame, text="Next Floor", command=self.next_floor).pack(side="left")
        tk.Button(frame, text="Save Map", command=self.save_map).pack(side="left")
        tk.Button(frame, text="Load Map", command=self.load_map).pack(side="left")
        self.floor_label = tk.Label(frame, text=f"Floor: 1"); self.floor_label.pack(side="left")

        self.add_floor()

    def add_floor(self):
        self.floors.append({"rooms": [], "elements":[]})
        self.current_floor = len(self.floors)-1
        self.redraw_current_floor()

    def redraw_current_floor(self):
        self.canvas.delete("all")
        floor = self.floors[self.current_floor]

        # Draw rooms first (room plane)
        for room in floor["rooms"]:
            self.redraw_room(room)

        # Draw elements on top (element plane)
        for elem in floor.get("elements", []):
            ex1, ey1, ex2, ey2 = elem["coords"]
            elem_obj = DraggableResizable(
                self.canvas, ex1, ey1, ex2, ey2,
                fill="lightblue",
                label=elem["label"],
                on_update=lambda x1, y1, x2, y2, ed=elem: ed.update({"coords":[x1, y1, x2, y2]})
            )
            elem["obj"] = elem_obj

        self.floor_label.config(text=f"Floor: {self.current_floor+1}")

    def redraw_room(self, room_data):
        x1, y1, x2, y2 = room_data["coords"]
        room_obj = DraggableResizable(
            self.canvas, x1, y1, x2, y2,
            fill="lightgrey",
            label=room_data["label"],
            on_update=lambda x1, y1, x2, y2, rd=room_data: rd.update({"coords":[x1, y1, x2, y2]})
        )
        room_data["obj"] = room_obj

    def add_room(self):
        floor = self.floors[self.current_floor]
        room_data = {"coords": [50, 50, 150, 150], "label": "Room"}
        floor["rooms"].append(room_data)
        self.redraw_room(room_data)

    def add_element(self):
        floor = self.floors[self.current_floor]
        elem_data = {"coords":[60,60,100,100], "label":"Element"}
        floor["elements"].append(elem_data)
        # Only redraw the new element to preserve positions
        ex1, ey1, ex2, ey2 = elem_data["coords"]
        elem_obj = DraggableResizable(
            self.canvas, ex1, ey1, ex2, ey2,
            fill="lightblue",
            label=elem_data["label"],
            on_update=lambda x1, y1, x2, y2, ed=elem_data: ed.update({"coords":[x1, y1, x2, y2]})
        )
        elem_data["obj"] = elem_obj

    def next_floor(self):
        if self.current_floor < len(self.floors)-1:
            self.current_floor += 1
            self.redraw_current_floor()

    def prev_floor(self):
        if self.current_floor > 0:
            self.current_floor -= 1
            self.redraw_current_floor()

    # --- Save / Load ---
    def save_map(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files","*.json")])
        if not filename: return
        data_to_save = []
        for floor in self.floors:
            floor_data = {
                "rooms": [{"label": r["label"], "coords": r["coords"]} for r in floor["rooms"]],
                "elements": [{"label": e["label"], "coords": e["coords"]} for e in floor["elements"]]
            }
            data_to_save.append(floor_data)
        with open(filename, "w") as f:
            json.dump({"floors": data_to_save}, f, indent=4)
        messagebox.showinfo("Saved", f"Map saved to {filename}")

    def load_map(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON Files","*.json")])
        if not filename: return
        with open(filename, "r") as f:
            loaded = json.load(f)
        self.floors = []
        for floor in loaded["floors"]:
            self.floors.append({
                "rooms": [{"label": r["label"], "coords": r["coords"]} for r in floor["rooms"]],
                "elements": [{"label": e["label"], "coords": e["coords"]} for e in floor["elements"]]
            })
        self.current_floor = 0
        self.redraw_current_floor()
        messagebox.showinfo("Loaded", f"Map loaded from {filename}")


if __name__ == "__main__":
    root = tk.Tk()
    editor = MapEditor(root)
    root.mainloop()