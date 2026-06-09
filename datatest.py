import io
import pandas as pd

# 1. Загрузка данных при импорте или запуске модуля
try:
    df = pd.read_csv("dataset.csv")
except FileNotFoundError:
    # Создаем пустой DataFrame, если файла еще нет в папке
    df = pd.DataFrame()


def generate_report():
    """Функция для генерации отчета.
    Использует StringIO для одновременной записи в консоль и файл.
    """
    if df.empty:
        print("Ошибка: Файл 'dataset.csv' не найден или пуст.")
        return

    output = io.StringIO()

    # --- 1. Количество строк и колонок ---
    output.write(f"{df.shape}\n\n")

    # --- 2. Информация о типах данных (df.info()) ---
    df.info(buf=output)
    output.write("\n")

    # --- 3. Количество незаполненных ячеек ---
    output.write(f"{df.isna().sum().to_string()}\n\n")

    # --- 4. Базовая статистика для числовых (счётных) колонок ---
    # Колонки продаж для разных регионов
    numeric_cols = [
        "NA_Sales",
        "EU_Sales",
        "JP_Sales",
        "Other_Sales",
        "Global_Sales",
    ]

    output.write("Колонка>\tсреднее\tмедиана\tотклонение\n")
    for col in numeric_cols:
        if col in df.columns:
            mean_val = df[col].mean()
            median_val = df[col].median()
            std_val = df[col].std()
            output.write(
                f"{col}>\t{mean_val:.2f};\t{median_val:.2f};\t{std_val:.2f}\n"
            )
    output.write("\n")

    # --- 5. Распределение для категориальных колонок ---
    # Текстовые категории (Игровые платформы, Жанры) и Год выпуска
    categorical_cols = ["Platform", "Genre", "Year"]
    for col in categorical_cols:
        if col in df.columns:
            # Превращаем в строку
            output.write(str(df[col].value_counts()) + "\n\n")

    # Получаем финальный текст отчета
    report_text = output.getvalue()
    output.close()

    # Печатаем собранный отчет в консоль PyCharm
    print(report_text, end="")

    # Записываем отчет в файл report.txt в кодировке utf-8
    with open("report.txt", "w", encoding="utf-8") as f:
        f.write(report_text)


# Разграничение запуска: отчет сработает только при прямом старте файла
if __name__ == "__main__":
    generate_report()