from datetime import datetime
import tkinter as tk
from tkinter import messagebox
# Импортируем модуль из Задания 1.
# Наш файл называется datatest.py, а внутри него лежит таблица df
import datatest
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Переключаем matplotlib в режим работы с GUI Tkinter
matplotlib.use("TkAgg")

# -----------------------------------------------------------------------------
# Впишем сюда наш номер студенческого билета (ID)
STUDENT_ID = "70225625"
# -----------------------------------------------------------------------------


def get_marker_by_id(student_id):
    """ Функция вычисляет рекурсивную сумму цифр студенческого ID и возвращает маркер"""

    # Словарь соответствия цифр (1-9) и маркеров Matplotlib согласно таблице
    markers_map = {
        1: "^",  # Треугольник вверх
        2: ">",  # Треугольник вправо
        3: "o",  # Круг
        4: "s",  # Квадрат
        5: "P",  # Плюс
        6: "h",  # Шестиугольная фигура
        7: "*",  # Звезда
        8: "H",  # Шестиугольная фигура, иной вариант
        9: "<",  # Треугольник влево
    }

    # Оставляем только цифры из строки
    digits = [int(char) for char in str(student_id) if char.isdigit()]
    if not digits:
        return "^"  # По умолчанию, если ID пустой

    current_sum = sum(digits)
    # Рекурсивно складываем цифры, пока не останется одна цифра (меньше 10)
    while current_sum >= 10:
        current_sum = sum(int(d) for d in str(current_sum))

    return markers_map.get(current_sum, "^")


class ScatterApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Визуализация данных: Точечная диаграмма")

        # Получаем данные из модуля первого задания
        self.df = datatest.df
        if self.df.empty:
            messagebox.showerror(
                "Ошибка",
                "Датасет пуст или файл 'dataset.csv' не найден модулем datatest.py",
            )
            self.root.destroy()
            return

        # Наш список числовых колонок (из игрового датасета)
        self.numeric_cols = [
            "NA_Sales",
            "EU_Sales",
            "JP_Sales",
            "Other_Sales",
            "Global_Sales",
        ]
        # Фильтруем только те колонки, которые реально присутствуют в файле
        self.numeric_cols = [col for col in self.numeric_cols if col in self.df.columns]

        # Переменные для хранения выбранных колонок
        # По умолчанию: X - первая числовая колонка, Y - вторая
        self.selected_x = self.numeric_cols[0]
        self.selected_y = self.numeric_cols[1]

        # Определяем маркер на основе студенческого ID
        self.marker_style = get_marker_by_id(STUDENT_ID)

        # Списки для хранения объектов кнопок (чтобы менять их внешний вид при активации)
        self.y_buttons = {}
        self.x_buttons = {}

        self.create_widgets()
        self.update_plot()

    def create_widgets(self):
        # 1. Левая панель для кнопок выбора оси Y
        self.left_frame = tk.Frame(self.root, width=150)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Кнопка "Сохранить" в левом нижнем углу
        self.save_btn = tk.Button(
            self.left_frame,
            text="Сохранить",
            command=self.save_graph,
            bg="#d3d3d3",
        )
        self.save_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        # Создаем вертикальный ряд кнопок для оси Y
        for col in self.numeric_cols:
            btn = tk.Button(
                self.left_frame,
                text=col,
                command=lambda c=col: self.select_y_column(c),
                relief=tk.RAISED,
            )
            btn.pack(side=tk.TOP, fill=tk.X, pady=2)
            self.y_buttons[col] = btn

        # 2. Нижняя панель для кнопок выбора оси X
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        # Создаем горизонтальный ряд кнопок для оси X
        for col in self.numeric_cols:
            btn = tk.Button(
                self.bottom_frame,
                text=col,
                command=lambda c=col: self.select_x_column(c),
                relief=tk.RAISED,
            )
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
            self.x_buttons[col] = btn

        # 3. Центральная область для холста графика Matplotlib
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        # Создаем фигуру Matplotlib
        self.fig, self.ax = plt.subplots(figsize=(6, 5))

        # Интегрируем график в окно Tkinter через Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def update_plot(self):
        """ Функция перерисовывает график при изменении колонок"""
        self.ax.clear()

        x_data = self.df[self.selected_x]
        y_data = self.df[self.selected_y]

        # Строим точечную диаграмму с индивидуальным маркером
        self.ax.scatter(x_data, y_data, marker=self.marker_style, alpha=0.7)

        # Настраиваем подписи осей и заголовок
        self.ax.set_xlabel(self.selected_x)
        self.ax.set_ylabel(self.selected_y)
        self.ax.set_title(f"Диаграмма рассеяния: {self.selected_y} vs {self.selected_x}")
        self.ax.grid(True, linestyle="--", alpha=0.5)

        # Обновляем внешний вид кнопок - выбранные утапливаем, а остальные поднимаем
        for col, btn in self.x_buttons.items():
            btn.config(relief=tk.SUNKEN if col == self.selected_x else tk.RAISED)

        for col, btn in self.y_buttons.items():
            btn.config(relief=tk.SUNKEN if col == self.selected_y else tk.RAISED)

        # Обновляем холст в окне
        self.canvas.draw()

    def select_x_column(self, col_name):
        self.selected_x = col_name
        self.update_plot()

    def select_y_column(self, col_name):
        self.selected_y = col_name
        self.update_plot()

    def save_graph(self):
        """ Функция сохраняет текущий график в формате graphHH_MM_SS.png"""
        now = datetime.now()
        # Форматируем имя файла: часы, минуты, секунды с ведущими нулями
        filename = now.strftime("graph%H_%M_%S.png")

        try:
            # Сохраняем фигуру matplotlib в файл
            self.fig.savefig(filename, dpi=300, bbox_inches="tight")
            messagebox.showinfo("Успех", f"График успешно сохранен как:\n{filename}")
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить файл:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ScatterApp(root)
    root.mainloop()