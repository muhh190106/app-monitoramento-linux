"""A visitor dashboard using synthetic activity only; no collectors are started."""

from datetime import date
import logging
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .charts import ACCENT, MUTED, PANEL, TEXT, draw_timeline
from .i18n import translate
from .reporting import build_report, demo_intervals, format_duration

BACKGROUND = "#0b1420"
SIDEBAR = "#0d1927"
BORDER = "#25364b"


class Dashboard:
    def __init__(self, root: tk.Tk, language="en", anchor=None, intervals=None):
        self.root = root
        self.language = language
        self.anchor = anchor or date.today()
        self.reference = self.anchor
        self.intervals = tuple(demo_intervals(self.anchor) if intervals is None else intervals)
        self.days = 1
        self.application = None
        self.report = None
        self.root.title("STime NOW")
        self.root.geometry("1220x800")
        self.root.minsize(980, 700)
        self.root.configure(bg=BACKGROUND)
        self.root.bind("<Control-q>", lambda event: self.root.destroy())
        self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)
        self._style()
        self._build()

    def t(self, key, **values):
        return translate(self.language, key, **values)

    def _style(self):
        self.font = "Segoe UI" if self.root.tk.call("tk", "windowingsystem") == "win32" else "DejaVu Sans"
        self.root.option_add("*Font", (self.font, 10))
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground="#1b2d42", background="#1b2d42", foreground=TEXT, arrowcolor=TEXT, bordercolor=BORDER, padding=8)
        style.map("TCombobox", fieldbackground=[("readonly", "#1b2d42")], foreground=[("readonly", TEXT)], selectbackground=[("readonly", "#1b2d42")], selectforeground=[("readonly", TEXT)])
        self.root.option_add("*TCombobox*Listbox.background", PANEL)
        self.root.option_add("*TCombobox*Listbox.foreground", TEXT)
        style.configure("Usage.Treeview", background=PANEL, fieldbackground=PANEL, foreground=TEXT, borderwidth=0, rowheight=32, font=(self.font, 10))
        style.configure("Usage.Treeview.Heading", background=PANEL, foreground=MUTED, relief="flat", font=(self.font, 9))
        style.map("Usage.Treeview", background=[("selected", "#244559")], foreground=[("selected", TEXT)])
        style.map("Usage.Treeview.Heading", background=[("active", PANEL)])

    def label(self, parent, text, *, size=10, color=TEXT, bold=False, bg=None, **kwargs):
        return tk.Label(parent, text=text, font=(self.font, size, "bold" if bold else "normal"), fg=color, bg=bg or parent.cget("bg"), anchor="w", **kwargs)

    def button(self, parent, text, command, selected=False):
        return tk.Button(parent, text=text, command=command, bg=ACCENT if selected else "#1b2d42", fg=BACKGROUND if selected else TEXT, activebackground="#79e4cf", activeforeground=BACKGROUND, relief="flat", bd=0, padx=15, pady=8, cursor="hand2", highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT, takefocus=True)

    def _build(self):
        for child in self.root.winfo_children():
            child.destroy()
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        sidebar = tk.Frame(self.root, bg=SIDEBAR, width=190)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        sidebar.columnconfigure(0, weight=1)
        sidebar.rowconfigure(6, weight=1)
        self.label(sidebar, "STime NOW", size=18, bold=True).grid(row=0, padx=22, pady=(32, 4), sticky="w")
        self.label(sidebar, self.t("tagline"), size=8, color=MUTED).grid(row=1, padx=22, sticky="w")
        self.label(sidebar, self.t("workspace"), size=8, color=MUTED).grid(row=2, padx=22, pady=(56, 12), sticky="w")
        self.label(sidebar, "  " + self.t("overview"), size=11, color=ACCENT, bg="#15352f", padx=12, pady=12).grid(row=3, padx=16, sticky="ew")
        profile = tk.Frame(sidebar, bg=SIDEBAR)
        profile.grid(row=4, column=0, padx=22, pady=28, sticky="w")
        self.label(profile, self.t("visitor"), bold=True).pack(anchor="w")
        self.label(profile, self.t("local_profile"), size=9, color=MUTED).pack(anchor="w", pady=(6, 0))
        demo = tk.Frame(sidebar, bg=SIDEBAR)
        demo.grid(row=7, padx=20, pady=28, sticky="sw")
        self.label(demo, self.t("demo"), size=10, color=ACCENT, bold=True).pack(anchor="w")
        self.label(demo, self.t("demo_note"), size=9, color=MUTED, justify="left", wraplength=140).pack(anchor="w", pady=(10, 0))

        main = tk.Frame(self.root, bg=BACKGROUND, padx=28, pady=26)
        main.grid(row=0, column=1, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(4, weight=1)
        header = tk.Frame(main, bg=BACKGROUND)
        header.grid(row=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        self.title_label = self.label(header, self.t("overview"), size=26, bold=True)
        self.title_label.grid(row=0, column=0, sticky="w")
        self.label(header, self.t("subtitle"), color=MUTED).grid(row=1, column=0, sticky="w", pady=(7, 0))
        lang = tk.Frame(header, bg=BACKGROUND)
        lang.grid(row=0, column=1, rowspan=2, sticky="e")
        self.label(lang, self.t("language"), size=9, color=MUTED).pack(anchor="w", pady=(0, 6))
        self.language_box = ttk.Combobox(lang, values=("English", "Português"), state="readonly", width=12, takefocus=True)
        self.language_box.set("English" if self.language == "en" else "Português")
        self.language_box.pack()
        self.language_box.bind("<<ComboboxSelected>>", lambda event: self.set_language("en" if self.language_box.get() == "English" else "pt-BR"))

        filters = tk.Frame(main, bg=BACKGROUND)
        filters.grid(row=1, sticky="ew", pady=(28, 4))
        self.period_buttons = {}
        for column, (days, key) in enumerate(((1, "today"), (7, "week"), (30, "month"))):
            button = self.button(filters, self.t(key), lambda value=days: self.set_period(value), self.days == days)
            button.grid(row=1, column=column, sticky="w", padx=(0, 7))
            self.period_buttons[days] = button
        filters.columnconfigure(3, weight=1)
        self.label(filters, self.t("date"), size=9, color=MUTED).grid(row=0, column=4, sticky="w", pady=(0, 6))
        self.date_entry = tk.Entry(filters, bg="#1b2d42", fg=TEXT, insertbackground=ACCENT, relief="flat", width=12, highlightthickness=1, highlightbackground=BORDER, highlightcolor=ACCENT)
        self.date_entry.grid(row=1, column=4, ipady=8, padx=(0, 8))
        self.date_entry.insert(0, self.reference.isoformat())
        self.date_entry.bind("<Return>", lambda event: self.apply_date())
        self.button(filters, self.t("apply"), self.apply_date).grid(row=1, column=5)
        self.message = tk.StringVar()
        self.label(main, "", size=9, color="#ffba90", textvariable=self.message).grid(row=2, sticky="w", pady=(2, 10))

        cards = tk.Frame(main, bg=BACKGROUND)
        cards.grid(row=3, sticky="ew", pady=(0, 22))
        self.metrics = {}
        for column, key in enumerate(("active", "idle", "apps", "top_app")):
            cards.columnconfigure(column, weight=1, uniform="metric")
            card = tk.Frame(cards, bg=PANEL, padx=17, pady=17, highlightbackground=BORDER, highlightthickness=1)
            card.grid(row=0, column=column, sticky="nsew", padx=(0, 10 if column < 3 else 0))
            self.label(card, self.t(key), size=9, color=MUTED).pack(anchor="w")
            value = tk.StringVar(value="—")
            self.label(card, "", size=22 if key != "top_app" else 17, bold=True, color=ACCENT if key == "active" else TEXT, textvariable=value).pack(anchor="w", pady=(13, 0))
            self.metrics[key] = value

        content = tk.Frame(main, bg=BACKGROUND)
        content.grid(row=4, sticky="nsew")
        content.columnconfigure(0, weight=3)
        content.columnconfigure(1, weight=2)
        content.rowconfigure(0, weight=1)
        chart = tk.Frame(content, bg=PANEL, highlightbackground=BORDER, highlightthickness=1)
        chart.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
        chart.rowconfigure(2, weight=1)
        chart.columnconfigure(0, weight=1)
        self.label(chart, self.t("timeline"), size=12, bold=True).grid(row=0, padx=20, pady=(20, 8), sticky="w")
        self.range_label = self.label(chart, "", size=9, color=MUTED)
        self.range_label.grid(row=1, padx=20, sticky="w")
        self.figure = Figure(figsize=(5.4, 3.1), dpi=100, facecolor=PANEL)
        self.canvas = FigureCanvasTkAgg(self.figure, master=chart)
        self.canvas.get_tk_widget().configure(bg=PANEL, highlightthickness=0, width=1, height=1)
        self.canvas.get_tk_widget().grid(row=2, column=0, sticky="nsew", pady=(4, 6))

        breakdown = tk.Frame(content, bg=PANEL, padx=17, pady=16, highlightbackground=BORDER, highlightthickness=1)
        breakdown.grid(row=0, column=1, sticky="nsew")
        breakdown.columnconfigure(0, weight=1)
        breakdown.rowconfigure(3, weight=1)
        self.label(breakdown, self.t("breakdown"), size=12, bold=True).grid(row=0, sticky="w")
        self.label(breakdown, self.t("filter_label"), size=9, color=MUTED).grid(row=1, sticky="w", pady=(12, 6))
        self.application_box = ttk.Combobox(breakdown, state="readonly", values=(self.t("all_apps"), *sorted({event.app for event in self.intervals})), width=18)
        self.application_box.set(self.application or self.t("all_apps"))
        self.application_box.grid(row=2, sticky="ew", pady=(0, 14))
        self.application_box.bind("<<ComboboxSelected>>", lambda event: self.set_application(None if self.application_box.get() == self.t("all_apps") else self.application_box.get()))
        table_frame = tk.Frame(breakdown, bg=PANEL)
        table_frame.grid(row=3, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.table = ttk.Treeview(table_frame, columns=("app", "time", "share"), show="headings", style="Usage.Treeview", height=5, selectmode="browse")
        for column, key, width, anchor in (("app", "application", 105, "w"), ("time", "time", 80, "e"), ("share", "share", 55, "e")):
            self.table.heading(column, text=self.t(key))
            self.table.column(column, width=width, minwidth=45, anchor=anchor, stretch=column == "app")
        self.table.grid(row=0, column=0, sticky="nsew")
        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        scroll.grid(row=0, column=1, sticky="ns")
        self.table.configure(yscrollcommand=scroll.set)
        self.empty_label = self.label(breakdown, "", size=9, color=MUTED, wraplength=230)
        self.empty_label.grid(row=4, sticky="w", pady=(8, 0))
        footer = tk.Frame(main, bg=BACKGROUND)
        footer.grid(row=5, sticky="ew", pady=(18, 0))
        self.label(footer, self.t("sample_label"), size=8, color=ACCENT, bold=True).pack(side="left")
        self.button(footer, self.t("reset"), self.reset_filters).pack(side="right")
        self.refresh()

    def refresh(self):
        self.message.set("")
        try:
            self.report = build_report(self.intervals, self.reference, self.days, self.application)
        except ValueError:
            logging.getLogger(__name__).exception("Unable to build the activity report")
            self.message.set(self.t("report_error"))
            return
        report = self.report
        self.metrics["active"].set(format_duration(report.active_seconds))
        self.metrics["idle"].set(format_duration(report.idle_seconds))
        self.metrics["apps"].set(str(len(report.applications)))
        self.metrics["top_app"].set(report.applications[0].app if report.applications else "—")
        self.range_label.configure(text=self.t("period", start=report.start.strftime("%d/%m/%Y"), end=report.end.strftime("%d/%m/%Y")))
        self.table.delete(*self.table.get_children())
        for app in report.applications:
            self.table.insert("", "end", values=(app.app, format_duration(app.seconds), f"{app.share:.0%}"))
        if report.applications:
            self.empty_label.grid_remove()
        else:
            self.empty_label.configure(text=self.t("empty"))
            self.empty_label.grid()
        draw_timeline(self.figure, report, self.language)
        self.canvas.draw()

    def set_period(self, days):
        self.days = days
        for value, button in self.period_buttons.items():
            button.configure(bg=ACCENT if value == days else "#1b2d42", fg=BACKGROUND if value == days else TEXT)
        self.refresh()

    def set_application(self, application):
        self.application = application
        self.application_box.set(application or self.t("all_apps"))
        self.refresh()

    def apply_date(self):
        try:
            reference = date.fromisoformat(self.date_entry.get())
            # Reporting needs room for the exclusive end boundary and lookback.
            if reference.year < 2 or reference == date.max:
                raise ValueError("Date outside supported report range")
        except ValueError:
            self.message.set(self.t("date_error"))
            return
        self.reference = reference
        self.refresh()

    def set_language(self, language):
        self.language = language
        self._build()

    def reset_filters(self):
        self.reference, self.days, self.application = self.anchor, 1, None
        self._build()


def launch(language="en"):
    root = tk.Tk()
    Dashboard(root, language)
    root.mainloop()
