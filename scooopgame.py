import tkinter as tk
import random
import os
import sys
import time
from collections import Counter

import pygame
from PIL import Image, ImageTk

# Marble definitions
marbles = [
    {"name": "Ring", "color": "#ff4d6d"},
    {"name": "Necklace", "color": "#8b4513"},
    {"name": "Bracelet", "color": "#ffb347"},
    {"name": "Hair clip", "color": "#ffd700"},
    {"name": "Hair Tie", "color": "#00ffcc"},
    {"name": "Squishy", "color": "#9370db"},
    {"name": "Shark Hair clip", "color": "#4682b4"},
    {"name": "Keychain", "color": "#dda0dd"},
    {"name": "Mouse pad", "color": "#40e0d0"},
    {"name": "Accessory", "color": "#add8e6"},
    {"name": "Sticker", "color": "#ffc0cb"},
    {"name": "Build Blocks", "color": "#ff69b4"},
    {"name": "Book mark", "color": "#f4a460"},
    {"name": "Note clip", "color": "#fdfd96"},
    {"name": "Eraser", "color": "#e0ffff"},
    {"name": "Mini notebook", "color": "#9370db"},
    {"name": "Note book", "color": "#ffff66"},
    {"name": "Post-it note", "color": "#ffb6c1"},
    {"name": "DIY-Diamond painting", "color": "#8b0000"},
    {"name": "Pencil case", "color": "#00bfff"},
    {"name": "Funny Pen", "color": "#90ee90"},
    {"name": "Multi-color Pen", "color": "#fffacd"},
    {"name": "Pen / Pencil", "color": "#ffe4e1"},
    {"name": "Mechanical pencil set", "color": "#0000cd"},
    {"name": "Highlighter", "color": "#87cefa"},
    {"name": "Planner", "color": "#ff69b4"},
    {"name": "Mini hardcover", "color": "#228b22"},
]

class MarbleScooperApp:
    def __init__(self, master):
        self.master = master
        self.master.title("✨ Animated Marble Scooper")
        self.canvas = tk.Canvas(master, width=500, height=350, bg="#dfe6e9", highlightthickness=0)
        self.canvas.pack()

        self.title_label = tk.Label(master, text="Marble Scoop Machine", font=("Helvetica", 18, "bold"))
        self.title_label.pack(pady=(10, 5))

        self.start_button = tk.Button(master, text="🎮 Start Scooping", font=("Helvetica", 12), command=self.start_scoop)
        self.start_button.pack(pady=5)

        self.text_area = tk.Text(master, height=10, width=60, state='disabled', font=("Courier", 10))
        self.text_area.pack(pady=10)

        self.spoon = None
        self.spoon_img = None
        self.scoop_sound_length = 0
        self.marble_delay_ms = 20  # speed up marble drip
        self.started_at = None
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        self.sound_path = os.path.join(base_path, "freesound_community-roll-marbles-55488.mp3")
        self.spoon_image_path = os.path.join(base_path, "spoon.png")
        self.setup_assets()

        self.marble_items = []
        self.draw_marble_pit()

    def setup_assets(self):
        try:
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.scoop_sound_length = pygame.mixer.Sound(self.sound_path).get_length()
        except Exception:
            self.scoop_sound_length = 0

        try:
            img = Image.open(self.spoon_image_path)
            new_size = (int(img.width * 0.6), int(img.height * 0.6))
            img = img.resize(new_size, Image.LANCZOS)
            self.spoon_img = ImageTk.PhotoImage(img)
        except Exception:
            self.spoon_img = None

    def draw_marble_pit(self):
        self.marble_items.clear()
        self.canvas.delete("marble")
        for _ in range(800):  # fewer marbles to render faster
            marble = random.choice(marbles)
            x = random.randint(40, 460)
            y = random.randint(200, 320)
            r = 12
            circle = self.canvas.create_oval(x - r, y - r, x + r, y + r,
                                             fill=marble["color"], outline="#555", width=1.5, tags="marble")
            self.marble_items.append((circle, marble["name"], marble["color"]))

    def start_scoop(self):
        self.started_at = time.time()
        self.clear_output()
        self.canvas.delete("spoon")
        self.canvas.delete("scooped")
        self.draw_marble_pit()
        if self.spoon_img:
            self.spoon = self.canvas.create_image(250, -20, image=self.spoon_img, anchor=tk.CENTER, tags="spoon")
        else:
            self.spoon = None

        self.play_scoop_sound()
        print(f"[scoop] start at {self.started_at:.3f}")
        self.animate_scoop_down(0)

    def animate_scoop_down(self, step):
        if step < 60:
            if self.spoon:
                self.canvas.move(self.spoon, 0, 5)
            self.master.after(5, lambda: self.animate_scoop_down(step + 1))
        else:
            print(f"[scoop] reached pit at {time.time() - self.started_at:.3f}s")
            self.master.after(200, self.do_scoop)

    def do_scoop(self):
        self.scooped = [random.choice(marbles) for _ in range(random.randint(6, 10))]
        self.count = Counter([m["name"] for m in self.scooped])
        self.animate_index = 0
        print(f"[scoop] scooping {len(self.scooped)} marbles")
        self.animate_scooped_marble()

    def animate_scooped_marble(self):
        if self.animate_index < len(self.scooped):
            m = self.scooped[self.animate_index]
            self.animate_marble_into_spoon(m["color"], self.animate_index)
            self.animate_index += 1
            self.master.after(self.marble_delay_ms, self.animate_scooped_marble)
        else:
            self.master.after(200, self.animate_scoop_up)

    def animate_scoop_up(self, step=0):
        if step < 60:
            if self.spoon:
                self.canvas.move(self.spoon, 0, -5)
            self.master.after(5, lambda: self.animate_scoop_up(step + 1))
        else:
            if self.spoon:
                self.canvas.delete("spoon")
                self.spoon = None
            print(f"[scoop] done at {time.time() - self.started_at:.3f}s")
            self.display_results()

    def animate_marble_into_spoon(self, color, index):
        r = 10
        max_per_row = 4
        spacing = 22
        row = index // max_per_row
        col = index % max_per_row
        spoon_x = 220
        spoon_y = 100
        x_target = spoon_x + col * spacing
        y_target = spoon_y + row * spacing
        marble = self.canvas.create_oval(x_target - r, -20, x_target + r, 0,
                    fill=color, outline="#333", width=1.5, tags="scooped")

        dy = (y_target + 5) / 12
        for _ in range(12):
            self.canvas.move(marble, 0, dy)
            self.canvas.update()

    def display_results(self):
        self.display_output("\n📦 Scooped Marbles:\n\n")
        for name, qty in self.count.items():
            self.display_output(f"• {name:<24}: {qty}x\n")

        # 🎲 2% chance of bonus scoop
        if random.randint(1, 50) == 1:
            self.display_output("\n🎁 BONUS SCOOP ACTIVATED!\n")
            self.master.after(1000, self.do_bonus_scoop)

    def do_bonus_scoop(self):
        bonus = [random.choice(marbles) for _ in range(random.randint(6, 10))]
        for m in bonus:
            self.scooped.append(m)
        bonus_count = Counter([m["name"] for m in bonus])
        self.count.update(bonus_count)
        self.animate_index = len(self.scooped) - len(bonus)
        self.animate_bonus_fall(bonus)

    def animate_bonus_fall(self, bonus):
        if self.animate_index < len(self.scooped):
            m = self.scooped[self.animate_index]
            self.animate_marble_into_spoon(m["color"], self.animate_index)
            self.animate_index += 1
            self.master.after(self.marble_delay_ms, lambda: self.animate_bonus_fall(bonus))
        else:
            self.display_output("\n🎉 Bonus Marbles:\n\n")
            bonus_count = Counter([m["name"] for m in self.scooped])
            for name, qty in bonus_count.items():
                self.display_output(f"• {name:<24}: {qty}x\n")

    def display_output(self, text):
        self.text_area.configure(state='normal')
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.configure(state='disabled')

    def clear_output(self):
        self.text_area.configure(state='normal')
        self.text_area.delete(1.0, tk.END)
        self.text_area.configure(state='disabled')

    def play_scoop_sound(self):
        if not pygame.mixer.get_init():
            return

        try:
            pygame.mixer.music.stop()
            start_at = 0
            duration = 5
            if self.scoop_sound_length > duration:
                start_at = random.uniform(0, self.scoop_sound_length - duration)

            pygame.mixer.music.load(self.sound_path)
            pygame.mixer.music.play(start=start_at)
            self.master.after(int(duration * 1000), pygame.mixer.music.stop)
        except Exception:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#f5f6fa")
    app = MarbleScooperApp(root)
    root.mainloop()
