import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import filedialog, scrolledtext
import threading
import time
from datetime import datetime

def set_permissions(file_path):
    os.chmod(file_path, 0o777)  # Tenta mudar as permissões do arquivo

class Watcher:
    def __init__(self, directory_to_watch, directory_to_copy, copy_entire_directory, copy_only_files, log_text):
        self.DIRECTORY_TO_WATCH = directory_to_watch
        self.DIRECTORY_TO_COPY = directory_to_copy
        self.copy_entire_directory = copy_entire_directory
        self.copy_only_files = copy_only_files
        self.log_text = log_text
        self.event_handler = Handler(self.DIRECTORY_TO_WATCH, self.DIRECTORY_TO_COPY, self.copy_entire_directory, self.copy_only_files, self.log_text)
        self.observer = Observer()

    def run(self):
        self.observer.schedule(self.event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        self.log_message(f"Iniciado monitoramento de: {self.DIRECTORY_TO_WATCH}")
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    def stop(self):
        self.observer.stop()
        self.observer.join()
        self.log_message("Monitoramento parado.")

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {message}\n"
        self.log_text.insert(tk.END, log_entry)
        with open("log.txt", "a") as log_file:
            log_file.write(log_entry)

class Handler(FileSystemEventHandler):
    def __init__(self, directory_to_watch, directory_to_copy, copy_entire_directory, copy_only_files, log_text):
        self.DIRECTORY_TO_WATCH = directory_to_watch
        self.DIRECTORY_TO_COPY = directory_to_copy
        self.copy_entire_directory = copy_entire_directory
        self.copy_only_files = copy_only_files
        self.log_text = log_text

    def on_created(self, event):
        if event.is_directory and not self.copy_entire_directory:
            return None
        else:
            src_path = event.src_path
            if self.copy_only_files:
                dest_path = os.path.join(self.DIRECTORY_TO_COPY, os.path.basename(src_path))
            else:
                dest_path = os.path.join(self.DIRECTORY_TO_COPY, src_path[len(self.DIRECTORY_TO_WATCH):])

            if os.path.abspath(src_path) != os.path.abspath(dest_path):
                try:
                    set_permissions(src_path)  # Tenta alterar permissões antes de copiar
                    os.system(f'copy "{src_path}" "{dest_path}"')
                    self.log_message(f"Arquivo copiado: {src_path}")
                except PermissionError:
                    self.log_message(f"Permissão negada: {src_path}")
                except Exception as e:
                    self.log_message(f"Erro ao copiar {src_path}: {e}")

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {message}\n"
        self.log_text.insert(tk.END, log_entry)
        with open("log.txt", "a") as log_file:
            log_file.write(log_entry)

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Observador de Pastas")
        self.root.geometry("600x400")
        self.watch_dir = ""
        self.copy_dir = ""
        self.watcher = None

        self.select_watch_button = tk.Button(root, text="Selecionar Pasta para Observar", command=self.select_watch_directory)
        self.select_watch_button.pack()

        self.watch_dir_label = tk.Label(root, text="")
        self.watch_dir_label.pack()

        self.select_copy_button = tk.Button(root, text="Selecionar Pasta de Destino", command=self.select_copy_directory)
        self.select_copy_button.pack()

        self.copy_dir_label = tk.Label(root, text="")
        self.copy_dir_label.pack()

        self.copy_entire_directory_var = tk.IntVar()
        self.copy_entire_directory_checkbox = tk.Checkbutton(root, text="Copiar Diretório Inteiro", variable=self.copy_entire_directory_var)
        self.copy_entire_directory_checkbox.pack()

        self.copy_only_files_var = tk.IntVar()
        self.copy_only_files_checkbox = tk.Checkbutton(root, text="Copiar Apenas Arquivos", variable=self.copy_only_files_var)
        self.copy_only_files_checkbox.pack()

        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        self.start_button = tk.Button(self.button_frame, text="Iniciar", command=self.start_watching, bg="white")
        self.start_button.grid(row=0, column=0)

        self.stop_button = tk.Button(self.button_frame, text="Parar", command=self.stop_watching, bg="white")
        self.stop_button.grid(row=0, column=1)

        self.log_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
        self.log_text.pack()

    def select_watch_directory(self):
        self.watch_dir = filedialog.askdirectory()
        self.watch_dir_label.config(text=f"Pasta para Observar: {self.watch_dir}")
        self.log_message(f"Selecionado para observar: {self.watch_dir}")

    def select_copy_directory(self):
        self.copy_dir = filedialog.askdirectory()
        self.copy_dir_label.config(text=f"Pasta de Destino: {self.copy_dir}")
        self.log_message(f"Selecionado para copiar: {self.copy_dir}")

    def start_watching(self):
        if self.watch_dir and self.copy_dir:
            self.start_button.config(bg="green")
            self.watcher = Watcher(self.watch_dir, self.copy_dir, bool(self.copy_entire_directory_var.get()), bool(self.copy_only_files_var.get()), self.log_text)
            threading.Thread(target=self.watcher.run).start()
        else:
            self.log_message("Por favor, selecione ambas as pastas.")

    def stop_watching(self):
        if self.watcher:
            self.watcher.stop()
            self.watcher = None
            self.start_button.config(bg="white")
            self.log_message("Monitoramento parado.")

    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {message}\n"
        self.log_text.insert(tk.END, log_entry)
        with open("log.txt", "a") as log_file:
            log_file.write(log_entry)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
