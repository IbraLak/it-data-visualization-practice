from datetime import datetime
import tkinter as tk
from tkinter import messagebox, colorchooser, ttk
# Импортируем модуль из Задания 1
import datatest
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Включаем интеграцию Matplotlib в графические окна Tkinter
matplotlib.use("TkAgg")

# =====================================================================
# НАСТРОЙКИ ИНДИВИДУАЛИЗАЦИИ В СООТВЕТСТВИИ С ВАРИАНТОМ (ID: 70225625)
DEFAULT_CMAP = "Reds"  # Палитра для первой буквы фамилии "К"
STUDENT_ID = "70225625"  # Свертка 2 -> маркер '>'


# =====================================================================

def get_marker_by_id(student_id):
    """Возвращает индивидуальный маркер на основе вашего ID."""
    return ">"


class DrawApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Модификация визуализаций данных: Рисование")

        # Загружаем датасет
        self.df = datatest.df
        if self.df.empty:
            messagebox.showerror("Ошибка", "Датасет пуст или файл 'dataset.csv' не найден.")
            self.root.destroy()
            return

        # Настраиваем списки колонок под наш игровой датасет
        self.numeric_cols = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"]
        self.categorical_cols = ["Platform", "Genre", "Year"]
        self.numeric_cols = [c for c in self.numeric_cols if c in self.df.columns]
        self.categorical_cols = [c for c in self.categorical_cols if c in self.df.columns]
        self.all_cols = self.numeric_cols + self.categorical_cols

        # Настройки отображения по умолчанию
        # НАСТРОЙКА: Выбираем строго одну первую и одну вторую колонку из списка числовых продаж
        self.selected_x = self.numeric_cols[0] if self.numeric_cols else self.all_cols[0]
        # Если в списке есть вторая колонка, берем её для оси Y, иначе берем первую
        self.selected_y = self.numeric_cols[1] if len(self.numeric_cols) > 1 else self.selected_x
        self.marker_style = get_marker_by_id(STUDENT_ID)
        self.current_cmap = DEFAULT_CMAP

        # ИНДИВИДУАЛЬНЫЕ НАСТРОЙКИ РИСОВАНИЯ ПО ВАРИАНТУ (ID: 70225625)
        self.is_drawing_mode = False
        self.pen_color = "#163819"  # Стабильный HEX-код для чисел RGB(22, 56, 25)
        self.pen_thickness = 6  # Рассчитанная толщина по умолчанию (6 пикселей)

        # Переменные для трекинга рисования и жесткого условия отмены по заданию
        self.last_drawn_line = None  #  Храним строго одну последнюю линию для отмены
        self.current_line_x = []
        self.current_line_y = []
        self.active_drawing_artist = None

        self.y_buttons = {}
        self.x_buttons = {}

        self.create_widgets()
        self.update_plot()

        # Универсальный перехват Ctrl+Z для любых раскладок  и CapsLock
        self.root.bind("<Control-KeyPress>", self.check_ctrl_z)

    def create_widgets(self):
        # 1. Верхняя панель: выбор cmap + Инструменты рисования
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        tk.Label(self.top_frame, text="cmap:").pack(side=tk.LEFT, padx=5)
        self.cmap_list = ["viridis", "plasma", "inferno", "magma", "cividis", "Greys", "Purples", "Blues", "Greens",
                          "Reds", "winter", "autumn", "spring", "summer"]
        self.cmap_combo = ttk.Combobox(self.top_frame, values=self.cmap_list, state="readonly", width=10)
        self.cmap_combo.set(self.current_cmap)
        self.cmap_combo.pack(side=tk.LEFT, padx=5)
        self.cmap_combo.bind("<<ComboboxSelected>>", self.on_cmap_change)

        # Разделительная линия
        ttk.Separator(self.top_frame, orient="vertical").pack(side=tk.LEFT, fill="y", padx=10)

        # Кнопка-триггер "Рисование"
        self.draw_toggle_btn = tk.Button(self.top_frame, text="Рисование", command=self.toggle_drawing_mode,
                                         relief=tk.RAISED)
        self.draw_toggle_btn.pack(side=tk.LEFT, padx=5)

        # Текстовое поле ввода толщины
        tk.Label(self.top_frame, text="Толщина:").pack(side=tk.LEFT, padx=2)
        self.thickness_var = tk.StringVar(value=str(self.pen_thickness))
        self.thickness_entry = tk.Entry(self.top_frame, textvariable=self.thickness_var, width=4)
        self.thickness_entry.pack(side=tk.LEFT, padx=5)
        self.thickness_var.trace_add("write", self.on_thickness_change)

        # Кнопка-квадратик выбора цвета
        tk.Label(self.top_frame, text="Цвет:").pack(side=tk.LEFT, padx=2)
        self.color_preview = tk.Button(self.top_frame, bg=self.pen_color, width=3, height=1, relief=tk.SOLID, bd=1,
                                       command=self.choose_color)
        self.color_preview.pack(side=tk.LEFT, padx=5)

        # 2. Левая панель: выбор оси Y + кнопка "Сохранить"
        self.left_frame = tk.Frame(self.root, width=150)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.save_btn = tk.Button(self.left_frame, text="Сохранить", command=self.save_graph, bg="#d3d3d3")
        self.save_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        for col in self.all_cols:
            btn = tk.Button(self.left_frame, text=col, command=lambda c=col: self.select_y_column(c))
            btn.pack(side=tk.TOP, fill=tk.X, pady=2)
            self.y_buttons[col] = btn

        # 3. Нижняя панель: выбор оси X
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        for col in self.all_cols:
            btn = tk.Button(self.bottom_frame, text=col, command=lambda c=col: self.select_x_column(c))
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
            self.x_buttons[col] = btn

        # 4. Центральная зона под график
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(expand=True, fill=tk.BOTH)

        # Регистрация событий мыши для рисования в Matplotlib
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_move)
        self.canvas.mpl_connect("button_release_event", self.on_release)

    def update_plot(self):
        """Интеллектуальная перерисовка 5 типов графиков из Задания 3"""
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)

        x_is_num = self.selected_x in self.numeric_cols
        y_is_num = self.selected_y in self.numeric_cols
        cmap = plt.get_cmap(self.current_cmap)

        if self.selected_x == self.selected_y and x_is_num:
            data = self.df[self.selected_x].dropna()
            n, bins, patches = self.ax.hist(data, bins=10, edgecolor="black", alpha=0.8)
            for i, patch in enumerate(patches):
                patch.set_facecolor(cmap(i / max(1, len(patches) - 1)))
            self.ax.set_ylabel("Количество")
        elif self.selected_x == self.selected_y and not x_is_num:
            counts = self.df[self.selected_x].value_counts().head(10)
            colors = [cmap(i / max(1, len(counts) - 1)) for i in range(len(counts))]
            self.ax.pie(counts, labels=counts.index, colors=colors, startangle=90)
            self.ax.set_ylabel(self.selected_y)
        elif x_is_num and not y_is_num:
            categories = self.df[self.selected_y].dropna().unique()[:10]
            data_groups = [self.df[self.df[self.selected_y] == cat][self.selected_x].dropna() for cat in categories]
            bp = self.ax.boxplot(data_groups, vert=False, tick_labels=categories, patch_artist=True)
            for i, box in enumerate(bp['boxes']):
                box.set_facecolor(cmap(i / max(1, len(bp['boxes']) - 1)))
            self.ax.set_xlabel(self.selected_x)
            self.ax.set_ylabel(self.selected_y)
        elif not x_is_num:
            counts = self.df[self.selected_x].value_counts().head(15)
            colors = [cmap(i / max(1, len(counts) - 1)) for i in range(len(counts))]
            self.ax.bar(counts.index.astype(str), counts.values, color=colors, edgecolor="black", alpha=0.8)
            self.ax.set_xlabel(self.selected_x)
            self.ax.set_ylabel("N")
            self.ax.tick_params(axis='x', rotation=45)
        else:
            x_data = self.df[self.selected_x]
            y_data = self.df[self.selected_y]
            self.ax.scatter(x_data, y_data, marker=self.marker_style, c=x_data, cmap=self.current_cmap, alpha=0.7)
            self.ax.set_xlabel(self.selected_x)
            self.ax.set_ylabel(self.selected_y)

        self.ax.set_title(f"{self.selected_y} vs {self.selected_x} ({self.current_cmap})")
        self.ax.grid(True, linestyle="--", alpha=0.3)
        self.fig.tight_layout()

        # ТЗ Требование: Восстанавливаем последнюю линию на новых осях при смене графиков
        if hasattr(self, 'last_drawn_line') and self.last_drawn_line is not None:
            new_artist, = self.ax.plot(self.last_drawn_line.get_xdata(), self.last_drawn_line.get_ydata(),
                                       color=self.last_drawn_line.get_color(),
                                       linewidth=self.last_drawn_line.get_linewidth())
            self.last_drawn_line = new_artist

        for col, btn in self.x_buttons.items():
            btn.config(relief=tk.SUNKEN if col == self.selected_x else tk.RAISED)
        for col, btn in self.y_buttons.items():
            btn.config(relief=tk.SUNKEN if col == self.selected_y else tk.RAISED)

        self.canvas.draw()

    def toggle_drawing_mode(self):
        """Переключает режим рисования и меняет курсор над холстом"""
        self.is_drawing_mode = not self.is_drawing_mode
        if self.is_drawing_mode:
            self.draw_toggle_btn.config(relief=tk.SUNKEN)
            self.canvas_widget.config(cursor="pencil")  # Карандаш по ТЗ
        else:
            self.draw_toggle_btn.config(relief=tk.RAISED)
            self.canvas_widget.config(cursor="arrow")  # Стрелка по ТЗ

    def select_x_column(self, col_name):
        """Смена оси X. Выключает режим рисования по заданию"""
        if self.is_drawing_mode:
            self.toggle_drawing_mode()
        self.selected_x = col_name
        self.update_plot()

    def select_y_column(self, col_name):
        """Смена оси Y. Выключает режим рисования по заданию."""
        if self.is_drawing_mode:
            self.toggle_drawing_mode()
        self.selected_y = col_name
        self.update_plot()

    def choose_color(self):
        """Открывает окно выбора цвета и передает туда ваши точные числа из ID"""
        color_code = colorchooser.askcolor(title="Выберите цвет карандаша", initialcolor=(22, 56, 25))
        if color_code and color_code[1]:
            self.pen_color = color_code[1]  # Сохраняем HEX для стабильного рисования
            self.color_preview.config(bg=self.pen_color)

    def on_thickness_change(self, *args):
        """Отслеживает ввод толщины в текстовое поле"""
        try:
            val = int(self.thickness_var.get())
            if val > 0:
                self.pen_thickness = val
        except ValueError:
            pass

    def on_cmap_change(self, event):
        """Перестраивает график при выборе новой цветовой схемы."""
        self.current_cmap = self.cmap_combo.get()
        self.update_plot()

    # ---
    def on_press(self, event):
        """Срабатывает при клике мышкой по графику."""
        if not self.is_drawing_mode:
            return

        # Нажатие правой кнопки мыши (кнопка 3) отключает режим рисования по заданию
        if event.button == 3:
            self.toggle_drawing_mode()
            return

        # Рисуем только левой кнопкой мыши  и строго внутри области осей графика
        if event.inaxes != self.ax or event.button != 1:
            return

        # Фиксируем начальные координаты клика
        self.current_line_x = [event.xdata]
        self.current_line_y = [event.ydata]

        # На месте одиночного клика рисуем квадратик (marker='s') нужного размера по заданию
        self.active_drawing_artist, = self.ax.plot(
            self.current_line_x, self.current_line_y,
            color=self.pen_color, linewidth=self.pen_thickness,
            marker='s', markersize=self.pen_thickness / 2
        )
        self.canvas.draw()

    def on_move(self, event):
        """Срабатывает при движении зажатой мыши внутри графика."""
        if not self.is_drawing_mode or self.active_drawing_artist is None or event.inaxes != self.ax:
            return

        # Добавляем новые точки в список координат линии
        self.current_line_x.append(event.xdata)
        self.current_line_y.append(event.ydata)

        # Обновляем координаты непрерывной линии на экране
        self.active_drawing_artist.set_data(self.current_line_x, self.current_line_y)
        self.canvas.draw()

    def on_release(self, event):
        """Срабатывает при отпускании левой кнопки мыши (завершение рисования)."""
        if self.active_drawing_artist is not None:
            # Убираем временный маркер-квадратик у линии для сохранения плавности
            self.active_drawing_artist.set_marker('none')

            # сохраняем в переменную только одну последнюю линию
            self.last_drawn_line = self.active_drawing_artist

            self.active_drawing_artist = None
            self.canvas.draw()

    def check_ctrl_z(self, event):
        """Проверяет нажатие Ctrl+Z/Я в любой раскладке клавиатуры."""
        if event.keysym.lower() == 'z' or event.keysym == 'Cyrillic_ya' or event.keycode == 90:
            self.undo_last_line()

    def undo_last_line(self, event=None):
        """Отмена ТОЛЬКО ОДНОЙ последней линии по Ctrl+Z (ТЗ Часть 3)."""
        # Пока мышка зажата (идет процесс рисования) - отмена заблокирована по ТЗ
        if self.active_drawing_artist is not None:
            return

        # Если есть линия для удаления - удаляем её
        if hasattr(self, 'last_drawn_line') and self.last_drawn_line is not None:
            self.last_drawn_line.remove()  # Стираем графический объект с холста
            self.last_drawn_line = None  # Очищаем переменную, повторный Ctrl+Z больше ничего не удалит!
            self.canvas.draw()

    def save_graph(self):
        """Сохраняет график со всеми нарисованными изменениями."""
        now = datetime.now()
        filename = now.strftime("graph%H_%M_%S.png")
        try:
            self.fig.savefig(filename, dpi=300, bbox_inches="tight")
            messagebox.showinfo("Успех", f"График с рисунками сохранен:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")


# --- ТОЧКА ВХОДА В ПРОГРАММУ ---
if __name__ == "__main__":
    root = tk.Tk()
    app = DrawApp(root)
    root.mainloop()
