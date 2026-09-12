import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
        self.status = tk.StringVar(value="Готов к запуску")
        self.running = False

        frame = tk.Frame(root, border=10)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Директория:").grid(row=0, column=0, sticky="w")
        tk.Entry(frame, textvariable=self.dir).grid(row=0, column=1, sticky="ew")
        tk.Button(frame, text="Обзор...", command=self.choose_dir).grid(row=0, column=2, padx=(5, 0))

        tk.Label(frame, text="Имя файла:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        tk.Entry(frame, textvariable=self.name).grid(row=1, column=1, sticky="ew", pady=(10, 0))

        self.generate_btn = tk.Button(frame, text="Сгенерировать", command=self.generate)
        self.generate_btn.grid(row=2, column=1, pady=(10, 0))

        tk.Label(frame, text="Прогресс:").grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.progress = ttk.Progressbar(frame, mode="determinate")
        self.progress.grid(row=3, column=1, columnspan=2, sticky="ew", pady=(10, 0))

        tk.Label(frame, textvariable=self.status).grid(row=4, column=1, columnspan=2, sticky="w")

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
        if self.running:
            return
        self.running = True
        self.generate_btn.config(state="disabled")
        self.status.set("Обработка...")
        threading.Thread(target=self._run, args=(dir, name), daemon=True).start()

    def _progress(self, done: int, total: int):
        self.root.after(0, self._update_progress, done, total)

    def _update_progress(self, done: int, total: int):
        if total and int(self.progress["maximum"]) != total:
            self.progress.configure(maximum=total)
        self.progress["value"] = done
        if total:
            self.status.set(f"Обработка: {done} из {total}")

    def _done(self):
        value = float(self.progress["value"])
        self.running = False
        self.progress.configure(maximum=value or 1, value=value or 1)
        self.generate_btn.config(state="normal")
        self.status.set("Готово")
        messagebox.showinfo("Готово", "Отчёт сохранён")

    def _failed(self, exc: Exception):
        self.running = False
        self.generate_btn.config(state="normal")
        self.status.set("Ошибка")
        messagebox.showerror("Ошибка", str(exc))

    def _run(self, dir, name):
        try:
            reporter.main(dir, name, HEADING, SUBHEADING, self._progress)
        except Exception as e:
            self.root.after(0, self._failed, e)
        else:
            self.root.after(0, self._done)


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()