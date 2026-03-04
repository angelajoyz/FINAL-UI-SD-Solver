import tkinter as tk

root = tk.Tk()
root.withdraw()

from tkinter import font
all_fonts = sorted(font.families())

print("=== Fonts containing 'nunito' (case-insensitive) ===")
matches = [f for f in all_fonts if "nunito" in f.lower()]
if matches:
    for m in matches:
        print(f"  '{m}'")
else:
    print("  NONE FOUND — Nunito is not visible to tkinter")

print("\n=== All available fonts ===")
for f in all_fonts:
    print(f"  {f}")

root.destroy()