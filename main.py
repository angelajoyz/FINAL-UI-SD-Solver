"""
Symbolic Derivative Generator  —  SD Solver
UI: CustomTkinter — playful-formal light theme, Nunito + Space Mono vibes
Functions: Symbolic + Numerical engines, Export (TXT/HTML), Toggle switch for Numerical,
           TrailLogger animation, Stop/Clear toggle, Notify popup, Stop popup
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext, font as tkfont, filedialog
import os
import threading
from datetime import datetime

from engine import DerivativeEngine
from numerical_engine import NumericalEngine
from trail_logger import TrailLogger

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ── Palette (light, airy, blue-lavender) ─────────────────────────────────────
BG          = "#f0f4ff"
BG2         = "#e4eaff"
SURFACE     = "#ffffff"
SURFACE2    = "#f7f9ff"
BORDER      = "#d0d8f5"
BORDER2     = "#c2ccf0"
ACCENT      = "#5c6ef8"
ACCENT2     = "#8b5cf6"
ACCENT3     = "#3b82f6"
GOLD        = "#f59e0b"
GREEN       = "#10b981"
RED         = "#ef4444"
BLUE_V      = "#3b82f6"
TXT         = "#1e2150"
TXT2        = "#5a608a"
TXT3        = "#9ba3cc"
TAG_BG      = "#eef0ff"
WARN_YEL    = "#f59e0b"

# ── Font placeholders (overridden in _load_fonts) ────────────────────────────
F_TOPBAR  = ("Nunito ExtraBold", 19)
F_SECTION = ("Nunito ExtraBold", 15)
F_LABEL   = ("Nunito ExtraBold", 15)
F_MONO    = ("Consolas",    13)
F_TAG     = ("Consolas",    12, "bold")
F_BTN     = ("Nunito ExtraBold", 17)
F_SMALL   = ("Nunito ExtraBold", 12)
F_ERR     = ("Nunito",      12)
F_ANSWER  = ("Consolas",    26, "bold")
F_STATUS  = ("Nunito ExtraBold", 17)
F_CHIP    = ("Nunito ExtraBold", 15)


class DerivativeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self._load_fonts()
        self.title("∂ SD Solver — Symbolic Derivative Generator")
        self.geometry("920x680")
        self.minsize(720, 520)
        self.configure(fg_color=BG)
        self.resizable(True, True)

        # ── Engines ──────────────────────────────────────────────────────────
        self.sym_engine  = DerivativeEngine()
        self.num_engine  = NumericalEngine()

        # ── State ─────────────────────────────────────────────────────────────
        self._generating       = False
        self._last_result      = None
        self._last_log         = []
        self._export_menu_open = False

        # Trail status: "idle" | "solved" | "error"
        self._trail_status     = "idle"

        self._build_ui()

    # ── Font loader ───────────────────────────────────────────────────────────
    def _load_fonts(self):
        global F_TOPBAR, F_SECTION, F_LABEL, F_MONO, F_TAG
        global F_BTN, F_SMALL, F_ERR, F_ANSWER, F_STATUS, F_CHIP

        F_TOPBAR  = ctk.CTkFont(family="Nunito ExtraBold", size=18)
        F_SECTION = ctk.CTkFont(family="Nunito ExtraBold", size=13)
        F_LABEL   = ctk.CTkFont(family="Nunito SemiBold",  size=13)
        F_MONO    = ctk.CTkFont(family="Consolas",         size=13)
        F_TAG     = ctk.CTkFont(family="Consolas",         size=12, weight="bold")
        F_BTN     = ctk.CTkFont(family="Nunito ExtraBold", size=14)
        F_SMALL   = ctk.CTkFont(family="Nunito SemiBold",  size=11)
        F_ERR     = ctk.CTkFont(family="Nunito",           size=11)
        F_ANSWER  = ctk.CTkFont(family="Consolas",         size=26, weight="bold")
        F_STATUS  = ctk.CTkFont(family="Nunito ExtraBold", size=16)
        F_CHIP    = ctk.CTkFont(family="Nunito SemiBold",  size=13)

    # ── Main UI ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_topbar()
        self.main_scroll = ctk.CTkScrollableFrame(
            self, fg_color=BG, corner_radius=0,
            scrollbar_button_color=BORDER2,
            scrollbar_button_hover_color=ACCENT)
        self.main_scroll.pack(fill="both", expand=True)

        self.col = ctk.CTkFrame(self.main_scroll, fg_color="transparent")
        self.col.pack(fill="x", padx=56, pady=(32, 48))

        self._build_input_panel()
        self._build_rules_section()
        self._build_trail_section()

        # TrailLogger hooks into the tk.Text trail widget
        self.logger = TrailLogger(self.trail_text)

    # ── Topbar ────────────────────────────────────────────────────────────────
    def _build_topbar(self):
        bar = ctk.CTkFrame(self, fg_color=SURFACE, corner_radius=0,
                           height=58, border_width=2, border_color=BORDER)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        ctk.CTkLabel(bar, text="∂", font=ctk.CTkFont(family="Nunito ExtraBold", size=22),
                     fg_color=ACCENT, text_color="white",
                     corner_radius=12, width=40, height=40
                     ).pack(side="left", padx=(18, 0), pady=9)

        ctk.CTkLabel(bar, text=" SD ", font=F_TOPBAR,
                     fg_color="transparent", text_color=ACCENT
                     ).pack(side="left")
        ctk.CTkLabel(bar, text="Solver — Symbolic Derivative Generator",
                     font=F_TOPBAR, fg_color="transparent", text_color=TXT
                     ).pack(side="left")

        ctk.CTkFrame(bar, fg_color=BORDER2, width=1, height=22,
                     corner_radius=0).pack(side="left", padx=14, pady=18)

        ctk.CTkLabel(bar, text="  Basic Rules Engine  ",
                     font=F_SMALL, fg_color=TAG_BG,
                     text_color=TXT2, corner_radius=20
                     ).pack(side="left")

        # About / Help button
        ctk.CTkButton(bar, text="?  About / Help", font=F_SMALL,
                      fg_color=ACCENT2, hover_color="#7340d4",
                      text_color="white", corner_radius=10,
                      height=32, width=120,
                      command=self._show_about
                      ).pack(side="right", padx=(0, 12), pady=13)

        self.st_dot = ctk.CTkLabel(bar, text="●", font=F_SMALL,
                                   text_color=GREEN, fg_color="transparent")
        self.st_dot.pack(side="right", padx=(4, 8))
        self.status_lbl = ctk.CTkLabel(bar, text="Ready",
                                       font=F_SMALL, text_color=TXT3,
                                       fg_color="transparent")
        self.status_lbl.pack(side="right")

    # ── Section label with trailing line ──────────────────────────────────────
    def _section_label(self, parent, text, pady_top=0):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(pady_top, 10))
        ctk.CTkLabel(row, text=text.upper(), font=F_SECTION,
                     fg_color="transparent", text_color=ACCENT,
                     anchor="w").pack(side="left")
        ctk.CTkFrame(row, fg_color=BORDER, height=2,
                     corner_radius=2).pack(side="left", fill="x",
                                           expand=True, padx=(10, 0), pady=6)

    # ── Input panel ───────────────────────────────────────────────────────────
    def _build_input_panel(self):
        self._section_label(self.col, "Input Panel")

        panel = ctk.CTkFrame(self.col, fg_color=SURFACE, corner_radius=20,
                             border_width=2, border_color=BORDER)
        panel.pack(fill="x")

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="x", padx=24, pady=20)

        # Row 1 — f(x)
        fx_block = self._field(inner, "f(x) =", "f(x)", "x**3 + 2*x**2 - 5*x + 1")
        fx_block.pack(fill="x", pady=(0, 10))
        self.entry_fx   = fx_block._entry
        self.wrap_fx    = fx_block._wrap
        self.err_fx     = fx_block._err

        # Row 2 — var, order, eval point
        fields_row = ctk.CTkFrame(inner, fg_color="transparent")
        fields_row.pack(fill="x")
        fields_row.columnconfigure(0, weight=1)
        fields_row.columnconfigure(1, weight=1)
        fields_row.columnconfigure(2, weight=2)

        var_block = self._field(fields_row, "Variable", "var", "x")
        var_block.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_var  = var_block._entry
        self.wrap_var   = var_block._wrap
        self.err_var    = var_block._err

        order_block = self._field(fields_row, "Order (n)", "n =", "1")
        order_block.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        self.entry_order = order_block._entry
        self.wrap_order  = order_block._wrap
        self.err_order   = order_block._err

        self.point_block = self._field(fields_row, "Eval at x =", "x =", "e.g. 2.5", optional=True)
        self.point_block.grid(row=0, column=2, sticky="ew")
        self.entry_point = self.point_block._entry
        self.wrap_point  = self.point_block._wrap
        self.err_point   = self.point_block._err

        # ── Buttons row ───────────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x", pady=(14, 0))

        # Stop / Clear toggle button (same position as Clear)
        self.btn_clear = ctk.CTkButton(
            btn_row, text="✕  Clear", font=F_BTN,
            fg_color=SURFACE, hover_color=BG2,
            text_color=TXT2, corner_radius=12, height=42,
            width=120, border_width=2, border_color=BORDER2,
            command=self._on_clear_or_stop)
        self.btn_clear.pack(side="right")

        ctk.CTkButton(btn_row, text="▶   COMPUTE", font=F_BTN,
                      fg_color=ACCENT, hover_color=ACCENT2,
                      text_color="white", corner_radius=12, height=42,
                      width=154, command=self._on_compute
                      ).pack(side="right", padx=(0, 8))

        # ── Numerical toggle switch ───────────────────────────────────────────
        # Sits on the left side of the button row, subtle and unobtrusive
        self._numerical_var = ctk.BooleanVar(value=False)

        switch_frame = ctk.CTkFrame(btn_row, fg_color="transparent")
        switch_frame.pack(side="left")

        self.numerical_switch = ctk.CTkSwitch(
            switch_frame,
            text="",
            variable=self._numerical_var,
            onvalue=True,
            offvalue=False,
            width=36,
            height=18,
            button_color=SURFACE,
            button_hover_color=BG2,
            fg_color=BORDER2,
            progress_color=ACCENT3,
            command=self._on_numerical_toggle,
        )
        self.numerical_switch.pack(side="left")

        self.numerical_label = ctk.CTkLabel(
            switch_frame,
            text="Numerical",
            font=F_SMALL,
            text_color=TXT3,
            fg_color="transparent",
        )
        self.numerical_label.pack(side="left", padx=(6, 0))

    # ── Numerical toggle callback ─────────────────────────────────────────────
    def _on_numerical_toggle(self):
        """Updates label color to reflect active/inactive state."""
        if self._numerical_var.get():
            self.numerical_label.configure(text_color=ACCENT3)
        else:
            self.numerical_label.configure(text_color=TXT3)

    # ── Field widget ──────────────────────────────────────────────────────────
    def _field(self, parent, label_text, tag_text, placeholder, optional=False):
        outer = ctk.CTkFrame(parent, fg_color="transparent")

        lbl_row = ctk.CTkFrame(outer, fg_color="transparent")
        lbl_row.pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(lbl_row, text=label_text, font=F_LABEL,
                     fg_color="transparent", text_color=TXT2).pack(side="left")
        if optional:
            ctk.CTkLabel(lbl_row, text=" opt ", font=ctk.CTkFont(family="Nunito ExtraBold", size=13),
                         fg_color=BG2, text_color=TXT3,
                         corner_radius=6).pack(side="left", padx=(5, 0))

        wrap = ctk.CTkFrame(outer, fg_color=SURFACE2, corner_radius=12,
                            border_width=2, border_color=BORDER)
        wrap.pack(fill="x")

        ctk.CTkLabel(wrap, text=f" {tag_text} ", font=F_TAG,
                     fg_color=TAG_BG, text_color=ACCENT,
                     corner_radius=8, height=36
                     ).pack(side="left", padx=(3, 0), pady=3)

        entry = ctk.CTkEntry(wrap, font=F_MONO,
                             fg_color="transparent", bg_color="transparent",
                             text_color=TXT,
                             placeholder_text=placeholder,
                             placeholder_text_color=TXT3,
                             border_width=0, corner_radius=0, height=36)
        entry.pack(side="left", fill="x", expand=True, padx=(8, 6), pady=3)

        err = ctk.CTkLabel(outer, text="", font=F_ERR,
                           text_color=RED, fg_color="transparent", anchor="w")
        err._outer = outer

        outer._entry = entry
        outer._wrap  = wrap
        outer._err   = err
        return outer

    # ── Error helpers ─────────────────────────────────────────────────────────
    def _set_err(self, wrap, err, msg):
        wrap.configure(border_color=RED)
        err.configure(text=f"⚠  {msg}")
        err.pack(anchor="w", pady=(3, 0), in_=err._outer)

    def _clr_err(self, wrap, err):
        wrap.configure(border_color=BORDER)
        err.configure(text="")
        err.pack_forget()

    def _clear_all_errors(self):
        for w, e in [(self.wrap_fx, self.err_fx), (self.wrap_var, self.err_var),
                     (self.wrap_order, self.err_order), (self.wrap_point, self.err_point)]:
            self._clr_err(w, e)

    # ── Supported rules ───────────────────────────────────────────────────────
    def _build_rules_section(self):
        self._section_label(self.col, "Supported Rules", pady_top=22)

        panel = ctk.CTkFrame(self.col, fg_color=SURFACE, corner_radius=20,
                             border_width=2, border_color=BORDER)
        panel.pack(fill="x")

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=16)

        grid = ctk.CTkFrame(inner, fg_color="transparent")
        grid.pack(fill="x")
        for i in range(3):
            grid.columnconfigure(i, weight=1)

        rules = ["Power Rule", "Constant Rule", "Sum / Difference",
                 "Chain Rule (basic)", "Product Rule", "Quotient Rule"]

        for i, rule in enumerate(rules):
            c, r = i % 3, i // 3
            ctk.CTkLabel(grid, text=f"✦  {rule}",
                         font=F_CHIP, text_color=TXT2,
                         fg_color="transparent", anchor="w"
                         ).grid(row=r, column=c,
                                padx=(0, 8) if c < 2 else 0,
                                pady=5, sticky="w")

    # ── Trail section (hidden until compute) ──────────────────────────────────
    def _build_trail_section(self):
        self.trail_outer = ctk.CTkFrame(self.col, fg_color="transparent")

        self._section_label(self.trail_outer, "Solution Trail", pady_top=22)

        # ── Trail card — border color changes on solved/error ─────────────────
        self.trail_card = ctk.CTkFrame(self.trail_outer, fg_color=SURFACE,
                                       corner_radius=20, border_width=2,
                                       border_color=BORDER)
        self.trail_card.pack(fill="x")

        # ── Answer bar — border turns green (solved) / red (error) ──────────
        self.ans_bar = ctk.CTkFrame(self.trail_card, fg_color=SURFACE2,
                                    corner_radius=0, border_width=3,
                                    border_color=BORDER)
        self.ans_bar.pack(fill="x")
        ans_inner = ctk.CTkFrame(self.ans_bar, fg_color="transparent")
        ans_inner.pack(fill="x", padx=20, pady=16)

        # Left: answer label
        ans_left = ctk.CTkFrame(ans_inner, fg_color="transparent")
        ans_left.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(ans_left, text="FINAL ANSWER", font=F_SMALL,
                     text_color=TXT3, fg_color="transparent").pack(anchor="w")
        self.lbl_answer = ctk.CTkLabel(ans_left, text="—", font=F_ANSWER,
                                       text_color=GOLD, fg_color="transparent")
        self.lbl_answer.pack(anchor="w")

        # Right: method badge only
        ans_right = ctk.CTkFrame(ans_inner, fg_color="transparent")
        ans_right.pack(side="right", fill="y")

        self.lbl_method_badge = ctk.CTkLabel(
            ans_right, text="—",
            font=F_SMALL,
            fg_color=TAG_BG, text_color=TXT3,
            corner_radius=10)
        self.lbl_method_badge.pack(anchor="e")

        ctk.CTkFrame(self.trail_card, fg_color=BORDER, height=2,
                     corner_radius=0).pack(fill="x")

        # ── Trail header row ──────────────────────────────────────────────────
        trail_hdr = ctk.CTkFrame(self.trail_card, fg_color=BG2,
                                 corner_radius=0, height=44)
        trail_hdr.pack(fill="x")
        trail_hdr.pack_propagate(False)

        # Left side: label + sub-label
        hdr_left = ctk.CTkFrame(trail_hdr, fg_color="transparent")
        hdr_left.pack(side="left", padx=18, pady=8)
        ctk.CTkLabel(hdr_left, text="SOLUTION TRAIL", font=F_SECTION,
                     text_color=TXT, fg_color="transparent").pack(side="left")
        ctk.CTkLabel(hdr_left, text="  step-by-step audit log",
                     font=ctk.CTkFont(family="Nunito", size=12), text_color=TXT3,
                     fg_color="transparent").pack(side="left")

        # Right side: Export icon button only
        export_anchor = ctk.CTkFrame(trail_hdr, fg_color="transparent")
        export_anchor.pack(side="right", padx=14, pady=6)

        def _toggle_export_menu(event=None):
            if self._export_menu_open:
                return
            self._export_menu_open = True

            menu = tk.Toplevel(self)
            menu.overrideredirect(True)
            menu.configure(bg=BORDER2)
            menu.attributes("-topmost", True)

            inner_m = tk.Frame(menu, bg=SURFACE, padx=1, pady=1)
            inner_m.pack(fill="both", expand=True)

            def _pick_txt():
                menu.destroy()
                self._export_menu_open = False
                self._export_txt()

            def _pick_html():
                menu.destroy()
                self._export_menu_open = False
                self._export_html()

            def _close_menu(e=None):
                try:
                    menu.destroy()
                except Exception:
                    pass
                self._export_menu_open = False

            for label, cmd, color in [
                ("📄  Export as .TXT",  _pick_txt,  ACCENT3),
                ("🌐  Export as .HTML", _pick_html, GOLD),
            ]:
                b = tk.Button(inner_m, text=label,
                              font=("Nunito SemiBold", 11),
                              fg=color, bg=SURFACE,
                              activebackground=BG2, activeforeground=color,
                              relief="flat", bd=0,
                              padx=14, pady=8,
                              cursor="hand2", anchor="w",
                              command=cmd)
                b.pack(fill="x")

            menu.update_idletasks()
            export_anchor.update_idletasks()
            bx = export_anchor.winfo_rootx()
            by = export_anchor.winfo_rooty() + export_anchor.winfo_height()
            mw = menu.winfo_reqwidth()
            mx = bx + export_anchor.winfo_width() - mw
            menu.geometry(f"+{mx}+{by}")
            menu.bind("<FocusOut>", _close_menu)
            menu.focus_set()

        export_btn = ctk.CTkButton(
            export_anchor,
            text="⬇",
            font=ctk.CTkFont(family="Nunito ExtraBold", size=15),
            fg_color="#e8ecf4",
            hover_color="#d4d9e8",
            text_color="#8a93b8",
            corner_radius=8,
            height=30,
            width=36,
            command=_toggle_export_menu,
        )
        export_btn.pack()

        ctk.CTkFrame(self.trail_card, fg_color=BORDER, height=2,
                     corner_radius=0).pack(fill="x")

        # ── Trail text box ────────────────────────────────────────────────────
        self.trail_text = tk.Text(
            self.trail_card, font=("Nunito SemiBold", 13),
            bg=SURFACE, fg=TXT,
            insertbackground=ACCENT,
            relief="flat", bd=0,
            wrap="word", state="disabled",
            padx=20, pady=16,
            height=1, cursor="arrow",
            selectbackground=BG2,
            selectforeground=TXT)
        self.trail_text.pack(fill="x", expand=False)

        for tag, fg_, fnt in [
            ("header",  ACCENT,   ("Consolas",         12)),
            ("section", ACCENT2,  ("Nunito ExtraBold", 13)),
            ("step",    TXT,      ("Nunito SemiBold",  13)),
            ("answer",  GOLD,     ("Nunito ExtraBold", 20)),
            ("verify",  BLUE_V,   ("Nunito",           13)),
            ("summary", TXT2,     ("Nunito",           13)),
            ("dim",     TXT3,     ("Consolas",         12)),
            ("rule",    GOLD,     ("Consolas",         13)),
            ("pass",    GREEN,    ("Nunito SemiBold",  13)),
            ("fail",    RED,      ("Nunito SemiBold",  13)),
            ("warn",    WARN_YEL, ("Nunito SemiBold",  13)),
        ]:
            self.trail_text.tag_config(tag, foreground=fg_, font=fnt)

        # ── Footer ────────────────────────────────────────────────────────────
        ctk.CTkFrame(self.trail_card, fg_color=BORDER, height=2,
                     corner_radius=0).pack(fill="x")
        solve_foot = ctk.CTkFrame(self.trail_card, fg_color=SURFACE2, corner_radius=0)
        solve_foot.pack(fill="x")

        self.solve_another_btn = ctk.CTkButton(
            solve_foot, text="↺   Solve Another", font=F_BTN,
            fg_color=SURFACE, hover_color=ACCENT,
            text_color=ACCENT, corner_radius=12, height=44,
            border_width=2, border_color=ACCENT,
            command=self._solve_another)

    # ── Trail card + answer bar border state ─────────────────────────────────
    def _set_trail_state(self, state: str):
        """state: 'idle' | 'computing' | 'solved' | 'error'"""
        self._trail_status = state
        color_map = {
            "idle":      BORDER,
            "computing": ACCENT,
            "solved":    GREEN,
            "error":     RED,
        }
        col = color_map.get(state, BORDER)
        self.trail_card.configure(border_color=col)
        self.ans_bar.configure(border_color=col)

    # ── Status helpers ────────────────────────────────────────────────────────
    def _set_status(self, msg, dot_color=None):
        self.status_lbl.configure(text=msg)
        if dot_color:
            self.st_dot.configure(text_color=dot_color)

    def _set_generating(self, state: bool):
        self._generating = state
        if state:
            self.btn_clear.configure(text="⏹  STOP",
                                     fg_color=RED, hover_color="#cc2222",
                                     text_color="white", border_color=RED)
        else:
            self.btn_clear.configure(text="✕  Clear",
                                     fg_color=SURFACE, hover_color=BG2,
                                     text_color=TXT2, border_color=BORDER2)

    # ── Trail helpers ─────────────────────────────────────────────────────────
    def _tc(self):
        self.trail_text.configure(state="normal")
        self.trail_text.delete("1.0", "end")
        self.trail_text.configure(state="disabled", height=1)

    def _show_trail(self):
        self.trail_outer.pack(fill="x")

    def _hide_trail(self):
        self.trail_outer.pack_forget()
        self.solve_another_btn.pack_forget()

    def _real_value(self, entry):
        return entry.get().strip()

    # ── Export helpers ────────────────────────────────────────────────────────
    def _get_trail_text(self) -> str:
        self.trail_text.configure(state="normal")
        content = self.trail_text.get("1.0", "end")
        self.trail_text.configure(state="disabled")
        return content

    def _get_trail_log(self) -> list:
        return self.logger.get_log()

    def _export_txt(self):
        content = self._get_trail_text().strip()
        if not content or content == "—":
            self._show_notify("warning", "Nothing to Export",
                              "The solution trail is empty.\nPlease compute a derivative first.")
            return

        filepath = filedialog.asksaveasfilename(
            parent=self, title="Export Trail as TXT",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=f"sd_solver_trail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        )
        if not filepath:
            return

        header_line = (
            "SD SOLVER — Solution Trail Export\n"
            f"Exported : {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}\n"
            + "=" * 64 + "\n\n"
        )
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(header_line + content)
            self._show_notify("success", "Export Successful", f"Trail saved to:\n{filepath}")
        except Exception as exc:
            self._show_notify("error", "Export Failed", str(exc))

    def _export_html(self):
        content_check = self._get_trail_text().strip()
        if not content_check:
            self._show_notify("warning", "Nothing to Export",
                              "The solution trail is empty.\nPlease compute a derivative first.")
            return

        log = self._last_log if self._last_log else [(content_check, "step")]

        filepath = filedialog.asksaveasfilename(
            parent=self, title="Export Trail as HTML",
            defaultextension=".html",
            filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")],
            initialfile=f"sd_solver_trail_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
        )
        if not filepath:
            return

        TAG_COLORS = {
            "header":  ACCENT,
            "section": ACCENT2,
            "step":    TXT,
            "answer":  GOLD,
            "verify":  BLUE_V,
            "summary": TXT2,
            "dim":     TXT3,
            "rule":    GOLD,
            "pass":    GREEN,
            "fail":    RED,
            "warn":    WARN_YEL,
        }
        TAG_WEIGHTS = {"header": "bold", "section": "bold", "answer": "bold"}

        def escape_html(text: str) -> str:
            return (text.replace("&", "&amp;")
                        .replace("<", "&lt;")
                        .replace(">", "&gt;")
                        .replace(" ", "&nbsp;")
                        .replace("\n", "<br>\n"))

        body_html = ""
        for text, tag in log:
            color  = TAG_COLORS.get(tag, TXT)
            weight = TAG_WEIGHTS.get(tag, "normal")
            body_html += (f'<span style="color:{color};font-weight:{weight};">'
                          f'{escape_html(text)}</span>')

        timestamp = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>SD Solver — Solution Trail</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;800&family=Consolas&display=swap');
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ background: {BG}; color: {TXT}; font-family: 'Nunito', sans-serif;
           font-size: 13px; line-height: 1.65; padding: 32px 16px; }}
    .wrapper {{ max-width: 860px; margin: 0 auto; }}
    .banner {{ background: {SURFACE}; border-left: 4px solid {ACCENT};
               padding: 18px 28px; margin-bottom: 24px;
               display: flex; justify-content: space-between; align-items: center;
               flex-wrap: wrap; gap: 8px; border-radius: 12px; }}
    .banner-title {{ color: {ACCENT}; font-size: 18px; font-weight: 800; letter-spacing: 2px; }}
    .banner-meta  {{ color: {TXT3}; font-size: 11px; }}
    .trail-box {{ background: {SURFACE}; border: 1px solid {BORDER}; border-radius: 12px;
                  padding: 24px 28px; white-space: pre-wrap; word-break: break-word;
                  line-height: 1.7; font-family: 'Consolas', monospace; }}
    .footer {{ margin-top: 20px; color: {TXT3}; font-size: 10px;
               text-align: right; letter-spacing: 1px; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="banner">
      <div class="banner-title">∂&nbsp;&nbsp;SD SOLVER — SOLUTION TRAIL</div>
      <div class="banner-meta">Exported: {timestamp}</div>
    </div>
    <div class="trail-box">{body_html}</div>
    <div class="footer">Generated by SD Solver &nbsp;|&nbsp; {timestamp}</div>
  </div>
</body>
</html>"""

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
            self._show_notify("success", "Export Successful", f"Trail saved to:\n{filepath}")
        except Exception as exc:
            self._show_notify("error", "Export Failed", str(exc))

    # ── Custom notify popup ───────────────────────────────────────────────────
    def _show_notify(self, kind: str, title: str, message: str):
        KIND_MAP = {
            "success": (GREEN,    "✔", "EXPORT SUCCESSFUL"),
            "error":   (RED,      "✘", "EXPORT FAILED"),
            "warning": (WARN_YEL, "⚠", "NOTHING TO EXPORT"),
        }
        accent_col, icon, badge = KIND_MAP.get(kind, (ACCENT, "ℹ", title.upper()))

        popup = tk.Toplevel(self)
        popup.title(title)
        popup.configure(bg=SURFACE)
        popup.resizable(False, False)
        popup.grab_set()
        popup.attributes("-topmost", True)

        tk.Frame(popup, bg=accent_col, height=4).pack(fill="x")

        hdr = tk.Frame(popup, bg=SURFACE, padx=24, pady=16)
        hdr.pack(fill="x")
        tk.Label(hdr, text=icon,
                 font=tkfont.Font(family="Nunito ExtraBold", size=20, weight="bold"),
                 fg=accent_col, bg=SURFACE, width=2).pack(side="left", padx=(0, 14))
        title_col = tk.Frame(hdr, bg=SURFACE)
        title_col.pack(side="left", fill="x", expand=True)
        tk.Label(title_col, text=badge,
                 font=tkfont.Font(family="Nunito ExtraBold", size=11, weight="bold"),
                 fg=accent_col, bg=SURFACE, anchor="w").pack(anchor="w")
        tk.Label(title_col, text=title,
                 font=tkfont.Font(family="Nunito", size=9),
                 fg=TXT2, bg=SURFACE, anchor="w").pack(anchor="w", pady=(2, 0))

        tk.Frame(popup, bg=BORDER, height=1).pack(fill="x", padx=20)

        msg_frame = tk.Frame(popup, bg=BG2, padx=20, pady=14)
        msg_frame.pack(fill="x", padx=20, pady=14)
        tk.Label(msg_frame, text=message,
                 font=tkfont.Font(family="Nunito", size=9),
                 fg=TXT, bg=BG2,
                 justify="left", wraplength=360, anchor="w").pack(anchor="w")

        tk.Frame(popup, bg=BORDER, height=1).pack(fill="x", padx=20)

        btn_row = tk.Frame(popup, bg=SURFACE, padx=20, pady=12)
        btn_row.pack(fill="x")
        tk.Button(btn_row, text="  OK  ",
                  font=tkfont.Font(family="Nunito ExtraBold", size=10, weight="bold"),
                  fg="white", bg=accent_col,
                  activebackground=BG2, activeforeground=accent_col,
                  relief="flat", bd=0, padx=20, pady=6, cursor="hand2",
                  command=popup.destroy).pack(side="right")

        self.update_idletasks()
        popup.update_idletasks()
        mx = self.winfo_x() + (self.winfo_width()  // 2) - (popup.winfo_reqwidth()  // 2)
        my = self.winfo_y() + (self.winfo_height() // 2) - (popup.winfo_reqheight() // 2)
        popup.geometry(f"+{mx}+{my}")

    # ── Stop popup ────────────────────────────────────────────────────────────
    def _show_stop_popup(self, reason: str, outcome: str):
        popup = tk.Toplevel(self)
        popup.title("Completion / Stopping Condition")
        popup.configure(bg=SURFACE)
        popup.resizable(False, False)

        if outcome == "manual":
            accent_col = RED
            icon_text  = "⏹  MANUALLY STOPPED"
        elif outcome == "validation":
            accent_col = WARN_YEL
            icon_text  = "⚠  COMPUTATION STOPPED"
        else:
            accent_col = GREEN
            icon_text  = "✔  COMPUTATION COMPLETE"

        tk.Frame(popup, bg=accent_col, height=6).pack(fill="x")

        title_frame = tk.Frame(popup, bg=SURFACE, padx=24, pady=14)
        title_frame.pack(fill="x")
        tk.Label(title_frame,
                 text="🛑  COMPLETION / STOPPING CONDITION",
                 font=tkfont.Font(family="Nunito ExtraBold", size=11, weight="bold"),
                 fg=accent_col, bg=SURFACE).pack(anchor="w")
        tk.Label(title_frame, text=icon_text,
                 font=tkfont.Font(family="Nunito", size=9),
                 fg=TXT2, bg=SURFACE).pack(anchor="w", pady=(2, 0))

        tk.Frame(popup, bg=BORDER, height=1).pack(fill="x", padx=24)

        msg_frame = tk.Frame(popup, bg=SURFACE, padx=24, pady=16)
        msg_frame.pack(fill="x")
        tk.Label(msg_frame, text=reason,
                 font=tkfont.Font(family="Nunito", size=10),
                 fg=TXT, bg=SURFACE,
                 wraplength=380, justify="left").pack(anchor="w")

        tk.Frame(popup, bg=BORDER, height=1).pack(fill="x", padx=24)

        btn_frame2 = tk.Frame(popup, bg=SURFACE, padx=24, pady=12)
        btn_frame2.pack(fill="x")
        tk.Button(btn_frame2, text="  OK  ",
                  font=tkfont.Font(family="Nunito ExtraBold", size=10, weight="bold"),
                  fg="white", bg=accent_col,
                  activebackground=BG2, activeforeground=accent_col,
                  relief="flat", bd=0, padx=16, pady=6, cursor="hand2",
                  command=popup.destroy).pack(side="right")

        self.update_idletasks()
        popup.update_idletasks()
        mx = self.winfo_x() + (self.winfo_width()  // 2) - (popup.winfo_width()  // 2)
        my = self.winfo_y() + (self.winfo_height() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{mx}+{my}")

    # ── About / Help dialog ───────────────────────────────────────────────────
    def _show_about(self):
        popup = tk.Toplevel(self)
        popup.title("About / Help — SD Solver")
        popup.configure(bg=SURFACE)
        popup.geometry("520x600")
        popup.minsize(500, 550)
        popup.grab_set()

        container = tk.Frame(popup, bg=SURFACE)
        container.pack(fill="both", expand=True)

        canvas   = tk.Canvas(container, bg=SURFACE, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=SURFACE)
        scroll_frame.bind("<Configure>",
                          lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Frame(scroll_frame, bg=ACCENT2, height=5).pack(fill="x")

        hdr = tk.Frame(scroll_frame, bg=SURFACE, padx=28, pady=18)
        hdr.pack(fill="x")
        tk.Label(hdr, text="∂  SD SOLVER",
                 font=tkfont.Font(family="Nunito ExtraBold", size=16, weight="bold"),
                 fg=ACCENT, bg=SURFACE).pack(anchor="w")
        tk.Label(hdr, text="Symbolic Derivative Generator — Basic Rules Engine",
                 font=tkfont.Font(family="Nunito", size=9),
                 fg=TXT2, bg=SURFACE).pack(anchor="w")

        tk.Frame(scroll_frame, bg=BORDER, height=1).pack(fill="x", padx=24)

        info = tk.Frame(scroll_frame, bg=SURFACE, padx=28, pady=14)
        info.pack(fill="x")

        def row(label, value, val_color=TXT):
            f = tk.Frame(info, bg=SURFACE)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=f"{label:<18}",
                     font=tkfont.Font(family="Nunito ExtraBold", size=9, weight="bold"),
                     fg=TXT2, bg=SURFACE).pack(side="left")
            tk.Label(f, text=value,
                     font=tkfont.Font(family="Nunito", size=9),
                     fg=val_color, bg=SURFACE).pack(side="left")

        row("Version",      "1.0.0",      GOLD)
        row("Release Date", "2025")
        row("Language",     "Python 3.9+")
        row("GUI Toolkit",  "CustomTkinter")
        row("Math Engine",  "SymPy (symbolic exact)")

        tk.Frame(scroll_frame, bg=BORDER, height=1).pack(fill="x", padx=24, pady=(4, 0))

        mem = tk.Frame(scroll_frame, bg=SURFACE, padx=28, pady=14)
        mem.pack(fill="x")
        tk.Label(mem, text="PROJECT MEMBERS",
                 font=tkfont.Font(family="Nunito ExtraBold", size=9, weight="bold"),
                 fg=ACCENT2, bg=SURFACE).pack(anchor="w", pady=(0, 6))

        for m in ["Abella, Jonah Mark F.", "Janopol, Angela Joyce E.", "Pablo, Francis John C."]:
            f = tk.Frame(mem, bg=BG2, padx=10, pady=5)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=m,
                     font=tkfont.Font(family="Nunito ExtraBold", size=9, weight="bold"),
                     fg=TXT, bg=BG2).pack(anchor="w")

        tk.Frame(scroll_frame, bg=BORDER, height=1).pack(fill="x", padx=24, pady=(4, 0))

        hlp = tk.Frame(scroll_frame, bg=SURFACE, padx=28, pady=14)
        hlp.pack(fill="x")
        tk.Label(hlp, text="HOW TO USE",
                 font=tkfont.Font(family="Nunito ExtraBold", size=9, weight="bold"),
                 fg=ACCENT2, bg=SURFACE).pack(anchor="w", pady=(0, 6))

        help_lines = [
            ("f(x)",         "Enter function in Python syntax. e.g. x**3 + 2*x"),
            ("Variable",     "Single letter (x, y, t)"),
            ("Order",        "1–10"),
            ("Evaluate",     "Optional value (required for Numerical mode)"),
            ("Numerical",    "Toggle switch — enables finite difference approximation"),
            ("COMPUTE",      "Runs the solver immediately, no popup"),
            ("⏹ STOP",      "Stops the animation mid-way"),
            ("✕ Clear",     "Resets all fields"),
            ("⬇ Export",    "Icon button beside SOLUTION TRAIL header"),
            ("  → .TXT",    "Save trail as plain text file"),
            ("  → .HTML",   "Save trail as styled HTML file"),
        ]

        for field, desc in help_lines:
            f = tk.Frame(hlp, bg=SURFACE)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=f"{field:<16}",
                     font=tkfont.Font(family="Nunito ExtraBold", size=9, weight="bold"),
                     fg=GOLD, bg=SURFACE).pack(side="left")
            tk.Label(f, text=desc,
                     font=tkfont.Font(family="Nunito", size=9),
                     fg=TXT, bg=SURFACE,
                     wraplength=350, justify="left").pack(side="left")

        tk.Frame(scroll_frame, bg=BORDER, height=1).pack(fill="x", padx=24, pady=(4, 0))

        btn_f = tk.Frame(scroll_frame, bg=SURFACE, padx=28, pady=12)
        btn_f.pack(fill="x")
        tk.Button(btn_f, text="CLOSE",
                  font=tkfont.Font(family="Nunito ExtraBold", size=10, weight="bold"),
                  bg=ACCENT2, fg="white",
                  relief="flat", bd=0, padx=16, pady=6,
                  cursor="hand2", command=popup.destroy).pack(side="right")

    # ── Build trail segments (UI fallback trail builder) ──────────────────────
    def _build_segments(self, r):
        DIV = "─" * 58 + "\n"
        segs = []

        def s(text, tag="step"):
            segs.append((text, tag))

        s("⓪ GIVEN\n", "section");      s(DIV, "dim")
        s(f"   f({r['var']})           =  {r['raw_fx']}\n")
        s(f"   Variable        =  {r['raw_var']}\n")
        s(f"   Order (n)       =  {r['raw_order']}\n")
        s(f"   Evaluate at     =  {r['raw_point'] or 'Not specified'}\n\n")

        s("① VALIDATION\n", "section"); s(DIV, "dim")
        for chk in r.get("validation_steps", []):
            status = chk["status"]
            tag  = {"PASS":"pass","FAIL":"fail","WARN":"warn","SKIP":"dim"}.get(status,"step")
            icon = {"PASS":"✔","FAIL":"✘","WARN":"⚠","SKIP":"○"}.get(status," ")
            s(f"   Step {chk['num']}  {chk['label']}\n")
            s(f"           {icon}  {status}", tag)
            if chk.get("detail"):
                s(f"  —  {chk['detail']}", tag)
            s("\n\n")

        if not r["ok"]:
            s("   ✘  Computation aborted — correct the errors above and retry.\n", "fail")
            s("\n" + "═" * 58 + "\n", "dim")
            return segs

        s("   ✔  All checks passed — proceeding to computation.\n\n", "pass")

        s("③ METHOD\n", "section");     s(DIV, "dim")
        s(f"   Name            :  Symbolic Differentiation (Basic Rules)\n")
        s(f"   Rules applied   :  Power, Constant, Sum/Difference,\n")
        s(f"                      Constant Multiple, Chain, Product, Quotient\n")
        s(f"   Library         :  SymPy {r.get('sympy_version','')}\n\n")

        s("④ STEPS\n", "section");      s(DIV, "dim")
        var, fx, n = r["var"], r["raw_fx"], r["order"]
        s(f"   Step 1  Parse f({var}) into symbolic expression tree\n")
        s(f"           → Expression  :  {fx}\n\n", "rule")
        s(f"   Step 2  Identify each term and applicable rule\n")
        s(f"           \n\n", "rule")
        s(f"   Step 3  Apply derivative rule term-by-term  (n={n} pass(es))\n")
        s(f"           → d/d{var} [terms] = ...\n\n", "rule")
        s(f"   Step 4  Simplify / collect like terms\n")
        s(f"           → {r['answer']}\n\n", "rule")

        if r.get("point_value") is not None:
            s(f"   Step 5  Evaluate  f'({r['raw_point']})\n")
            s(f"           → f'({r['raw_point']})  =  {r['point_value']}\n\n", "rule")

        s("⑤ FINAL ANSWER\n", "section"); s(DIV, "dim")
        s(f"   d^{n}/d{var}^{n} [{fx}]  =  {r['answer']}\n\n", "answer")

        s("⑥ VERIFICATION\n", "section"); s(DIV, "dim")
        s("   Method          :  Symbolic back-substitution check\n", "verify")
        s("   Check           :  Integrate result → compare to f(x) + C\n", "verify")
        s("   Status          :  ⏳ Pending full verification engine\n\n", "verify")

        s("⑦ SUMMARY\n", "section");    s(DIV, "dim")
        s(f"   Timestamp       :  {r.get('timestamp','')}\n", "summary")
        s(f"   Python          :  {r.get('python_version','')}\n", "summary")
        s(f"   SymPy           :  {r.get('sympy_version','')}\n", "summary")
        s(f"   Status          :  ✅ Validation complete\n", "summary")
        s("\n" + "═" * 58 + "\n", "dim")

        return segs

    # ── Scroll to trail ───────────────────────────────────────────────────────
    def _scroll_to_trail(self):
        self.update_idletasks()
        self.trail_outer.update_idletasks()
        canvas = self.main_scroll._parent_canvas
        canvas.update_idletasks()
        try:
            col_y   = self.col.winfo_y()
            trail_y = self.trail_outer.winfo_y()
            total_height = self.col.winfo_height()
            scroll_frac = (col_y + trail_y) / max(total_height, 1)
            canvas.yview_moveto(max(0.0, scroll_frac - 0.02))
        except Exception:
            canvas.yview_moveto(0.6)

    # ── Self-contained human-paced animation ─────────────────────────────────
    def _run_animation(self, segments: list, on_done=None):
        CHAR_NORMAL  = 12
        CHAR_FAST    = 2
        CHAR_ANSWER  = 18
        PAUSE_SEG    = 30
        PAUSE_SEC    = 160
        PAUSE_RESULT = 65

        seg_idx = [0]

        def next_segment():
            if not self._generating:
                if on_done:
                    on_done("stopped")
                return

            idx = seg_idx[0]
            if idx >= len(segments):
                if on_done:
                    on_done("done")
                return

            text, tag = segments[idx]
            seg_idx[0] += 1

            if tag == "dim":
                cdelay, post, pre = CHAR_FAST,   20,          0
            elif tag == "section":
                cdelay, post, pre = CHAR_NORMAL, PAUSE_SEC,   PAUSE_SEC
            elif tag == "answer":
                cdelay, post, pre = CHAR_ANSWER, PAUSE_RESULT, 0
            elif tag in ("rule", "pass", "fail", "warn"):
                cdelay, post, pre = CHAR_NORMAL, PAUSE_RESULT, 0
            else:
                cdelay, post, pre = CHAR_NORMAL, PAUSE_SEG,   0

            def type_chars(ci=0):
                if not self._generating:
                    if on_done:
                        on_done("stopped")
                    return
                if ci >= len(text):
                    self.after(post, next_segment)
                    return
                ch = text[ci]
                self.trail_text.configure(state="normal")
                self.trail_text.insert("end", ch, tag)
                lc = int(self.trail_text.index("end-1c").split(".")[0])
                self.trail_text.configure(state="disabled", height=max(1, lc))
                try:
                    self.main_scroll._parent_canvas.yview_moveto(1.0)
                except Exception:
                    pass
                self.after(cdelay, type_chars, ci + 1)

            if pre > 0:
                self.after(pre, type_chars)
            else:
                type_chars()

        next_segment()

    # ── Stop / Clear toggle ───────────────────────────────────────────────────
    def _on_clear_or_stop(self):
        if self._generating:
            self._generating = False
        else:
            self._do_clear()

    def _do_clear(self):
        self._clear_all_errors()
        self.logger.clear()
        self._last_log = []
        self.lbl_answer.configure(text="—", text_color=GOLD)
        self.lbl_method_badge.configure(text="—", fg_color=TAG_BG, text_color=TXT3)
        self._set_trail_state("idle")
        self._set_status("Cleared", GREEN)
        self._hide_trail()
        self._tc()
        # Reset numerical toggle
        self._numerical_var.set(False)
        self.numerical_label.configure(text_color=TXT3)
        for entry, ph in [
            (self.entry_fx,    "x**3 + 2*x**2 - 5*x + 1"),
            (self.entry_var,   "x"),
            (self.entry_order, "1"),
            (self.entry_point, "e.g. 2.5"),
        ]:
            entry.delete(0, "end")
            entry.configure(placeholder_text=ph, text_color=TXT)

    def _on_clear(self):
        if not self._generating:
            self._do_clear()

    # ── Solve another ─────────────────────────────────────────────────────────
    def _solve_another(self):
        self._generating = False
        self._hide_trail()
        self._do_clear()
        self.main_scroll._parent_canvas.yview_moveto(0.0)

    # ── Compute — no popup, reads toggle directly ─────────────────────────────
    def _on_compute(self):
        if self._generating:
            return
        # Read method directly from the toggle switch
        method = "numerical" if self._numerical_var.get() else "symbolic"
        self._do_compute(method, scheme="central")

    def _do_compute(self, method: str, scheme: str):
        self._clear_all_errors()
        raw_fx    = self._real_value(self.entry_fx)
        raw_var   = self._real_value(self.entry_var)
        raw_order = self._real_value(self.entry_order)
        raw_point = self._real_value(self.entry_point)

        self._tc()
        self._show_trail()
        self._set_trail_state("computing")
        self.lbl_answer.configure(text="…", text_color=TXT2)
        self._set_status("Computing…", ACCENT)
        self.update_idletasks()
        self.after(50, self._scroll_to_trail)

        # Method badge
        if method == "numerical":
            self.lbl_method_badge.configure(text="  NUMERICAL  ",
                                            fg_color=ACCENT3, text_color="white")
        else:
            self.lbl_method_badge.configure(text="  SYMBOLIC  ",
                                            fg_color=ACCENT, text_color="white")

        # Run engine
        if method == "numerical":
            result = self.num_engine.validate_and_compute(
                raw_fx, raw_var, raw_order, raw_point, scheme=scheme)
        else:
            result = self.sym_engine.validate_and_compute(
                raw_fx, raw_var, raw_order, raw_point)

        full_log = result.get("log", [])
        if not full_log:
            full_log = self._build_segments(result)
        self._last_log = full_log

        if not result["ok"]:
            self.lbl_answer.configure(text="Error — see trail", text_color=RED)
            self._set_trail_state("error")
            self._set_status("Validation failed", RED)

            for field, msg in result["field_errors"].items():
                pairs = {"fx":    (self.wrap_fx,    self.err_fx),
                         "var":   (self.wrap_var,   self.err_var),
                         "order": (self.wrap_order, self.err_order),
                         "point": (self.wrap_point, self.err_point)}
                if field in pairs:
                    self._set_err(*pairs[field], msg)

            reason = "  \n".join(result["field_errors"].values())
            self._set_generating(True)
            self._run_animation(
                full_log,
                on_done=lambda _: (
                    self._set_generating(False),
                    self._show_stop_popup(reason, "validation")
                ))
            return

        self._set_generating(True)

        def on_animation_done(outcome):
            self._set_generating(False)
            if outcome == "stopped":
                self.lbl_answer.configure(text="—", text_color=GOLD)
                self._set_trail_state("idle")
                self._set_status("Stopped — no result", RED)
                self._show_stop_popup("User pressed Stop.", "manual")
            else:
                self.lbl_answer.configure(text=result["answer"], text_color=GOLD)
                self._set_trail_state("solved")
                self._set_status(f"Done  [{method.capitalize()}]  —  {result['timestamp']}", GREEN)
                self.solve_another_btn.pack(fill="x", padx=16, pady=12)
                self._show_stop_popup("Computation Complete", "done")

        self._run_animation(full_log, on_done=on_animation_done)


if __name__ == "__main__":
    app = DerivativeApp()
    app.mainloop()
