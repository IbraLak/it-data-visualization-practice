from datetime import datetime
import io
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
# Импортируем модуль из Задания 1. Наш файл называется datatest.py
import datatest
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Переключаем matplotlib в режим работы с GUI Tkinter
matplotlib.use("TkAgg")

# -----------------------------------------------------------------------
# Настройка индивидуального цвета в соответствии с заданием (Требование по индивидуализации)
DEFAULT_CMAP = "Reds"  # Палитра для первой буквы фамилии начинающейся на "К"
STUDENT_ID = "70225625"  # Мой студенческий ID


# --------------------------------------------------------------------

def get_marker_by_id(student_id):
    """Возвращает маркер '>' (треугольник вправо) для моего ID со сверткой 2."""
    return ">"


class VisualApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Улучшенная визуализация данных")

        # Загружаем датасет через модуль из первого задания
        self.df = datatest.df
        if self.df.empty:
            messagebox.showerror("Ошибка", "Датасет пуст или файл 'dataset.csv' не найден.")
            self.root.destroy()
            return

        # Разделяем колонки нашего игрового датасета на числовые и категориальные
        self.numeric_cols = ["NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales", "Global_Sales"]
        self.categorical_cols = ["Platform", "Genre", "Year"]

        # Фильтруем только те столбцы, которые реально присутствуют в файле
        self.numeric_cols = [c for c in self.numeric_cols if c in self.df.columns]
        self.categorical_cols = [c for c in self.categorical_cols if c in self.df.columns]

        # Объединяем в общий список для вывода кнопок на панели управления
        self.all_cols = self.numeric_cols + self.categorical_cols

        # Начальный выбор колонок при старте приложения
        self.selected_x = self.numeric_cols[0] if self.numeric_cols else self.all_cols[0]
        self.selected_y = self.numeric_cols[1] if len(self.numeric_cols) > 1 else self.all_cols[0]
        self.marker_style = get_marker_by_id(STUDENT_ID)

        # Список из 29 цветовых схем в соответствии с таблицей из методички
        self.cmap_list = [
            "viridis", "plasma", "inferno", "magma", "cividis", "Greys", "Purples",
            "Blues", "Greens", "Oranges", "Reds", "YlOrBr", "YlOrRd", "OrRd", "winter",
            "PurD", "RdPu", "BuPu", "GnBu", "InBu", "PuBu", "YlGnBu", "PuBuGn", "BuGn",
            "YlGn", "binary", "gist_yarg", "spring", "summer", "autumn"
        ]
        # Проверяем корректность палитры по умолчанию
        self.current_cmap = DEFAULT_CMAP if DEFAULT_CMAP in self.cmap_list else "Reds"

        # Списковые структуры для хранения объектов кнопок
        self.y_buttons = {}
        self.x_buttons = {}

        self.create_widgets()
        self.update_plot()

    def create_widgets(self):
        # 1. Верхняя панель для выпадающего списка выбора цветовой схемы (cmap)
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        tk.Label(self.top_frame, text="cmap:").pack(side=tk.LEFT, padx=5)

        self.cmap_combo = ttk.Combobox(self.top_frame, values=self.cmap_list, state="readonly", width=15)
        self.cmap_combo.set(self.current_cmap)
        self.cmap_combo.pack(side=tk.LEFT, padx=5)
        self.cmap_combo.bind("<<ComboboxSelected>>", self.on_cmap_change)

        # 2. Левая панель для кнопок выбора оси Y и кнопки "Сохранить"
        self.left_frame = tk.Frame(self.root, width=150)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        self.save_btn = tk.Button(self.left_frame, text="Сохранить", command=self.save_graph, bg="#d3d3d3")
        self.save_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        for col in self.all_cols:
            btn = tk.Button(self.left_frame, text=col, command=lambda c=col: self.select_y_column(c))
            btn.pack(side=tk.TOP, fill=tk.X, pady=2)
            self.y_buttons[col] = btn

        # 3. Нижняя панель для кнопок выбора оси X
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        for col in self.all_cols:
            btn = tk.Button(self.bottom_frame, text=col, command=lambda c=col: self.select_x_column(c))
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
            self.x_buttons[col] = btn

        # 4. Центральная область под холст Matplotlib
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.fig, self.ax = plt.subplots(figsize=(6, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def update_plot(self):
        """Интеллектуально переключает тип визуализации по правилам методички."""
        # Очищаем всю фигуру целиком, чтобы сбросить настройки круговых диаграмм
        self.fig.clear()
        # Создаем чистые оси с нуля
        self.ax = self.fig.add_subplot(111)

        # Определяем типы текущих выбранных колонок
        x_is_num = self.selected_x in self.numeric_cols
        y_is_num = self.selected_y in self.numeric_cols
        cmap = plt.get_cmap(self.current_cmap)

        # ------ ЛОГИКА ПЕРЕКЛЮЧЕНИЯ ГРАФИКОВ -----

        # Правило 1: Одинаковые числовые колонки - ГИСТОГРАММА (на 10 отрезков)
        if self.selected_x == self.selected_y and x_is_num:
            data = self.df[self.selected_x].dropna()
            n, bins, patches = self.ax.hist(data, bins=10, edgecolor="black", alpha=0.8)
            # Распределяем градиент выбранной палитры по барам гистограммы
            for i, patch in enumerate(patches):
                patch.set_facecolor(cmap(i / max(1, len(patches) - 1)))
            self.ax.set_ylabel("Количество")

        # Правило 2: Одинаковые категориальные колонки - КРУГОВАЯ ДИАГРАММА
        elif self.selected_x == self.selected_y and not x_is_num:
            counts = self.df[self.selected_x].value_counts().head(10)  # топ-10 для наглядности
            colors = [cmap(i / max(1, len(counts) - 1)) for i in range(len(counts))]
            self.ax.pie(counts, labels=counts.index, colors=colors, startangle=90)
            self.ax.set_ylabel(self.selected_y)

        # Правило 3: На X числовая, на Y категориальная - КОРОБОЧНАЯ ДИАГРАММА (Boxplot )
        elif x_is_num and not y_is_num:
            categories = self.df[self.selected_y].dropna().unique()[:10]  # Срез топ-10 категорий
            data_groups = [self.df[self.df[self.selected_y] == cat][self.selected_x].dropna() for cat in categories]

            bp = self.ax.boxplot(data_groups, vert=False, tick_labels=categories, patch_artist=True)
            for i, box in enumerate(bp['boxes']):
                box.set_facecolor(cmap(i / max(1, len(bp['boxes']) - 1)))
            self.ax.set_xlabel(self.selected_x)
            self.ax.set_ylabel(self.selected_y)

        # Правило 4: На X категориальная - СТОЛБЧАТАЯ ДИАГРАММА (Распределение по N)
        elif not x_is_num:
            counts = self.df[self.selected_x].value_counts().head(15)
            colors = [cmap(i / max(1, len(counts) - 1)) for i in range(len(counts))]
            self.ax.bar(counts.index.astype(str), counts.values, color=colors, edgecolor="black", alpha=0.8)
            self.ax.set_xlabel(self.selected_x)
            self.ax.set_ylabel("N")
            self.ax.tick_params(axis='x', rotation=45)

        # В остальных случаях - ТОЧЕЧНАЯ ДИАГРАММА
        else:
            x_data = self.df[self.selected_x]
            y_data = self.df[self.selected_y]
            # Подкрашиваем точки палитрой по шкале X для наглядности градиента
            scatter = self.ax.scatter(x_data, y_data, marker=self.marker_style,
                                      c=x_data, cmap=self.current_cmap, alpha=0.7)
            self.ax.set_xlabel(self.selected_x)
            self.ax.set_ylabel(self.selected_y)

        # Стилизация и компоновка
        self.ax.set_title(f"{self.selected_y} vs {self.selected_x} ({self.current_cmap})")
        self.ax.grid(True, linestyle="--", alpha=0.3)
        self.fig.tight_layout()

        # Визуальное переключение состояния кнопок (активная - sunken, пассивные - raised)
        for col, btn in self.x_buttons.items():
            btn.config(relief=tk.SUNKEN if col == self.selected_x else tk.RAISED)
        for col, btn in self.y_buttons.items():
            btn.config(relief=tk.SUNKEN if col == self.selected_y else tk.RAISED)

        self.canvas.draw()

    def select_x_column(self, col_name):
        self.selected_x = col_name
        self.update_plot()

    def select_y_column(self, col_name):
        self.selected_y = col_name
        self.update_plot()

    def on_cmap_change(self, event):
        """Обрабатывает выбор новой палитры в выпадающем списке"""
        self.current_cmap = self.cmap_combo.get()
        self.update_plot()

    def save_graph(self):
        """Сохраняет текущий график в формате graphHH_MM_SS.png с ведущими нулями"""
        now = datetime.now()
        filename = now.strftime("graph%H_%M_%S.png")
        try:
            self.fig.savefig(filename, dpi=300, bbox_inches="tight")
            messagebox.showinfo("Успех", f"График успешно сохранен под именем:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = VisualApp(root)
    root.mainloop()