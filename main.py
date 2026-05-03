import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os


class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Личный трекер расходов")
        self.root.geometry("950x650")
        self.root.resizable(True, True)

        # Установка иконки (опционально, если есть файл)
        try:
            self.root.iconbitmap('icon.ico')
        except:
            pass

        # Файл для хранения данных
        self.data_file = "expenses.json"
        self.expenses = self.load_expenses()

        # Создание интерфейса
        self.create_widgets()
        self.refresh_table()

    def load_expenses(self):
        """Загрузка расходов из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # Проверка, что данные - список
                    if isinstance(data, list):
                        return data
                    else:
                        return []
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка загрузки: {e}")
                return []
        return []

    def save_expenses(self):
        """Сохранение расходов в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as file:
                json.dump(self.expenses, file, ensure_ascii=False, indent=4)
            return True
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
            return False

    def create_widgets(self):
        """Создание всех элементов интерфейса"""
        # Стили
        style = ttk.Style()
        style.theme_use('clam')

        # ========== РАМКА ДЛЯ ВВОДА ==========
        input_frame = tk.LabelFrame(self.root, text="➕ Добавление расхода", font=("Arial", 10, "bold"), padx=10,
                                    pady=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        # Сумма
        tk.Label(input_frame, text="Сумма (₽):", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = tk.Entry(input_frame, width=20, font=("Arial", 10))
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        self.amount_entry.bind('<Return>', lambda e: self.add_expense())  # Enter для быстрого добавления

        # Категория
        tk.Label(input_frame, text="Категория:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.category_var = tk.StringVar(value="Еда")
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, width=15, font=("Arial", 10))
        self.category_combo['values'] = ('Еда', 'Транспорт', 'Развлечения', 'Здоровье', 'Коммунальные', 'Покупки',
                                         'Другое')
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)

        # Дата
        tk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):", font=("Arial", 10)).grid(row=0, column=4, padx=5, pady=5,
                                                                                  sticky="e")
        self.date_entry = tk.Entry(input_frame, width=15, font=("Arial", 10))
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        # Кнопка добавления
        self.add_btn = tk.Button(input_frame, text="Добавить расход", command=self.add_expense,
                                 bg="#4CAF50", fg="white", font=("Arial", 10, "bold"), padx=10)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)

        # ========== РАМКА ДЛЯ ФИЛЬТРАЦИИ ==========
        filter_frame = tk.LabelFrame(self.root, text="🔍 Фильтрация", font=("Arial", 10, "bold"), padx=10, pady=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        # Фильтр по категории
        tk.Label(filter_frame, text="Категория:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.filter_category_var = tk.StringVar(value="Все")
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var, width=15,
                                                  font=("Arial", 10))
        self.filter_category_combo['values'] = ('Все', 'Еда', 'Транспорт', 'Развлечения', 'Здоровье', 'Коммунальные',
                                                'Покупки', 'Другое')
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=5)

        # Фильтр по дате (от)
        tk.Label(filter_frame, text="Дата от:", font=("Arial", 10)).grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.date_from_entry = tk.Entry(filter_frame, width=12, font=("Arial", 10))
        self.date_from_entry.grid(row=0, column=3, padx=5, pady=5)

        # Фильтр по дате (до)
        tk.Label(filter_frame, text="до:", font=("Arial", 10)).grid(row=0, column=4, padx=5, pady=5, sticky="e")
        self.date_to_entry = tk.Entry(filter_frame, width=12, font=("Arial", 10))
        self.date_to_entry.grid(row=0, column=5, padx=5, pady=5)

        # Кнопки фильтрации
        self.filter_btn = tk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter,
                                    bg="#2196F3", fg="white", font=("Arial", 10), padx=10)
        self.filter_btn.grid(row=0, column=6, padx=5, pady=5)

        self.reset_btn = tk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter,
                                   bg="#FF9800", fg="white", font=("Arial", 10), padx=10)
        self.reset_btn.grid(row=0, column=7, padx=5, pady=5)

        # ========== ТАБЛИЦА ==========
        table_frame = tk.LabelFrame(self.root, text="📋 Список расходов", font=("Arial", 10, "bold"), padx=10, pady=10)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Создание таблицы
        columns = ("id", "amount", "category", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

        # Настройка заголовков
        self.tree.heading("id", text="ID")
        self.tree.heading("amount", text="Сумма (₽)")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")

        # Настройка ширины колонок
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("amount", width=120, anchor="e")
        self.tree.column("category", width=150, anchor="w")
        self.tree.column("date", width=120, anchor="center")

        # Скроллбар
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ========== ИТОГОВАЯ СУММА ==========
        total_frame = tk.Frame(self.root)
        total_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(total_frame, text="💰 Сумма за период:", font=("Arial", 12, "bold")).pack(side="left", padx=5)
        self.total_label = tk.Label(total_frame, text="0.00 ₽", font=("Arial", 14, "bold"), fg="#2E7D32")
        self.total_label.pack(side="left", padx=5)

        # ========== КНОПКИ УПРАВЛЕНИЯ ==========
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)

        self.delete_btn = tk.Button(button_frame, text="Удалить выбранную запись", command=self.delete_expense,
                                    bg="#f44336", fg="white", font=("Arial", 10), padx=10)
        self.delete_btn.pack(side="left", padx=5)

        self.clear_all_btn = tk.Button(button_frame, text="Очистить все данные", command=self.clear_all_data,
                                       bg="#9E9E9E", fg="white", font=("Arial", 10), padx=10)
        self.clear_all_btn.pack(side="left", padx=5)

    def validate_amount(self, amount_str):
        """Проверка корректности суммы"""
        if not amount_str:
            return False, "Сумма не может быть пустой"

        try:
            amount = float(amount_str)
            if amount <= 0:
                return False, "Сумма должна быть положительным числом"
            if amount > 999999999.99:
                return False, "Сумма слишком большая"
            # Округление до 2 знаков
            amount = round(amount, 2)
            return True, amount
        except ValueError:
            return False, "Введите корректное число (например: 100.50)"

    def validate_date(self, date_str):
        """Проверка корректности даты"""
        if not date_str:
            return False, "Дата не может быть пустой"

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            # Проверка на реальную дату (февраль, 31 число и т.д.)
            if date_obj.year < 2000 or date_obj.year > 2100:
                return False, "Год должен быть между 2000 и 2100"
            return True, date_str
        except ValueError:
            return False, "Дата должна быть в формате ГГГГ-ММ-ДД (например: 2026-05-03)"

    def add_expense(self):
        """Добавление нового расхода"""
        # Получение данных
        amount_str = self.amount_entry.get().strip()
        category = self.category_var.get()
        date_str = self.date_entry.get().strip()

        # Валидация суммы
        is_valid_amount, amount_result = self.validate_amount(amount_str)
        if not is_valid_amount:
            messagebox.showerror("Ошибка ввода", amount_result)
            self.amount_entry.focus()
            return

        # Валидация даты
        is_valid_date, date_result = self.validate_date(date_str)
        if not is_valid_date:
            messagebox.showerror("Ошибка ввода", date_result)
            self.date_entry.focus()
            return

        # Создание новой записи
        new_id = max([e["id"] for e in self.expenses], default=0) + 1
        new_expense = {
            "id": new_id,
            "amount": amount_result,
            "category": category,
            "date": date_result
        }

        # Добавление и сохранение
        self.expenses.append(new_expense)
        if self.save_expenses():
            self.refresh_table()
            # Очистка поля суммы, дата остаётся текущей
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.focus()
            messagebox.showinfo("Успех", f"Расход {amount_result:.2f} ₽ добавлен!")

    def delete_expense(self):
        """Удаление выбранного расхода"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Пожалуйста, выберите запись для удаления")
            return

        # Получение ID записи
        item = self.tree.item(selected[0])
        expense_id = item['values'][0]
        expense_amount = item['values'][1]
        expense_category = item['values'][2]

        # Подтверждение удаления
        if messagebox.askyesno("Подтверждение",
                               f"Удалить расход:\n"
                               f"Сумма: {expense_amount}\n"
                               f"Категория: {expense_category}\n"
                               f"ID: {expense_id}"):
            self.expenses = [e for e in self.expenses if e["id"] != expense_id]
            if self.save_expenses():
                self.refresh_table()
                messagebox.showinfo("Успех", "Запись успешно удалена")

    def clear_all_data(self):
        """Очистка всех данных"""
        if not self.expenses:
            messagebox.showinfo("Информация", "Нет данных для очистки")
            return

        if messagebox.askyesno("Подтверждение",
                               "ВНИМАНИЕ! Это действие удалит ВСЕ расходы.\n"
                               "Вы уверены, что хотите продолжить?"):
            self.expenses = []
            if self.save_expenses():
                self.refresh_table()
                self.reset_filter()
                messagebox.showinfo("Успех", "Все данные успешно очищены")

    def get_filtered_expenses(self):
        """Возвращает отфильтрованный список расходов"""
        filtered = self.expenses.copy()

        # Фильтр по категории
        category_filter = self.filter_category_var.get()
        if category_filter != "Все":
            filtered = [e for e in filtered if e["category"] == category_filter]

        # Фильтр по дате (от)
        date_from = self.date_from_entry.get().strip()
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") >= from_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты 'от'\nИспользуйте ГГГГ-ММ-ДД")
                return self.expenses

        # Фильтр по дате (до)
        date_to = self.date_to_entry.get().strip()
        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") <= to_date]
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты 'до'\nИспользуйте ГГГГ-ММ-ДД")
                return self.expenses

        return filtered

    def apply_filter(self):
        """Применение фильтрации"""
        self.refresh_table()
        messagebox.showinfo("Фильтр применен", "Таблица обновлена")

    def reset_filter(self):
        """Сброс фильтров"""
        self.filter_category_var.set("Все")
        self.date_from_entry.delete(0, tk.END)
        self.date_to_entry.delete(0, tk.END)
        self.refresh_table()
        messagebox.showinfo("Фильтр сброшен", "Показаны все расходы")

    def refresh_table(self):
        """Обновление таблицы и подсчёт суммы"""
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Получение отфильтрованных данных
        filtered = self.get_filtered_expenses()

        # Заполнение таблицы
        for expense in filtered:
            self.tree.insert("", "end", values=(
                expense["id"],
                f"{expense['amount']:.2f}",
                expense["category"],
                expense["date"]
            ))

        # Подсчёт суммы за период
        total = sum(e["amount"] for e in filtered)
        self.total_label.config(text=f"{total:.2f} ₽")

        # Обновление статуса
        count = len(filtered)
        if count == 0:
            self.total_label.config(fg="#9E9E9E")
        else:
            self.total_label.config(fg="#2E7D32")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
