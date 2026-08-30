import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import reporter

DEFAULT_NAME = "picture.pdf"
HEADING = "Общество с ограниченной ответственностью «ПоморКом»" 
SUBHEADING = "163016, г. Архангельск, ул. Октябрьская, д.3, стр. 7, каб.1"

class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Генератор отчёта")
        self.dir = tk.StringVar()
        self.name = tk.StringVar(value=DEFAULT_NAME)

        frame = tk.Frame(root, border=10)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Директория:").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.dir).grid(row=0, column=1, sticky="ew")
        tk.Button(frame, text="Обзор...", command=self.choose_dir).grid(row=0, column=2, padx=(5, 0))

        tk.Label(frame, text="Имя файла:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        tk.Entry(frame, textvariable=self.name).grid(row=1, column=1, sticky="ew", pady=(10, 0))

        tk.Button(frame, text="Сгенерировать", command=self.generate).grid(row=2, column=1, pady=(10, 0))

        frame.columnconfigure(1, weight=1)

    def choose_dir(self):
        chosen = filedialog.askdirectory(parent=self.root)
        if chosen:
            self.dir.set(chosen)

    def generate(self):
        dir = self.dir.get().strip()
        name = self.name.get().strip()
        if not dir:
            messagebox.showerror("Ошибка", "Выберите директорию")
            return
        if not name:
            messagebox.showerror("Ошибка", "Укажите имя файла")
            return
        threading.Thread(target=self._run, args=(dir, name), daemon=True).start()

    def _run(self, dir, name):
        try:
            reporter.main(dir, name, HEADING, SUBHEADING)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", str(e)))
        else:
            self.root.after(0, lambda: messagebox.showinfo("Готово", "Отчёт сохранён"))


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
