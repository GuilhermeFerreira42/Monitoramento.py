import os
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import time
from datetime import datetime
import pystray
from pystray import Icon as icon, Menu as menu, MenuItem as item
from PIL import Image, ImageDraw

class Watcher:
    def __init__(self, directory_to_watch, directory_to_copy, include_folders, copy_only_files, log_text):
        self.DIRECTORY_TO_WATCH = directory_to_watch
        self.DIRECTORY_TO_COPY = directory_to_copy
        self.include_folders = include_folders
        self.copy_only_files = copy_only_files
        self.log_text = log_text
        self.event_handler = Handler(self.DIRECTORY_TO_WATCH, self.DIRECTORY_TO_COPY, self.include_folders, self.copy_only_files, self.log_text)
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
    def __init__(self, directory_to_watch, directory_to_copy, include_folders, copy_only_files, log_text):
        self.DIRECTORY_TO_WATCH = directory_to_watch
        self.DIRECTORY_TO_COPY = directory_to_copy
        self.include_folders = include_folders
        self.copy_only_files = copy_only_files
        self.log_text = log_text

    def on_created(self, event):
        if event.is_directory and not self.include_folders:
            return None
        else:
            src_path = event.src_path
            if self.copy_only_files:
                dest_path = os.path.join(self.DIRECTORY_TO_COPY, os.path.basename(src_path))
            else:
                dest_path = os.path.join(self.DIRECTORY_TO_COPY, src_path[len(self.DIRECTORY_TO_WATCH):])

            if os.path.abspath(src_path) != os.path.abspath(dest_path):
                try:
                    self.log_message(f"Tentando copiar de {src_path} para {dest_path}")
                    self.retry_copy(src_path, dest_path)
                except Exception as e:
                    self.log_message(f"Erro ao copiar {src_path} para {dest_path}: {str(e)}")

    def retry_copy(self, src_path, dest_path, retries=5, delay=5):
        for i in range(retries):
            try:
                if os.path.isdir(src_path):
                    subprocess.run(["xcopy", src_path, dest_path, "/E", "/H", "/C", "/I", "/Y"], check=True)
                else:
                    subprocess.run(["copy", src_path, dest_path], shell=True, check=True)
                self.log_message(f"Arquivo copiado: {src_path}")
                return
            except subprocess.CalledProcessError as e:
                self.log_message(f"Erro ao tentar copiar {src_path} para {dest_path} (tentativa {i+1}): {str(e)}")
                time.sleep(delay)
        self.log_message(f"Falha ao copiar {src_path} para {dest_path} após {retries} tentativas")

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
        self.create_tray_icon()

        self.select_watch_button = tk.Button(root, text="Selecionar Pasta para Observar", command=self.select_watch_directory)
        self.select_watch_button.pack()

        self.watch_dir_label = tk.Label(root, text="")
        self.watch_dir_label.pack()

        self.select_copy_button = tk.Button(root, text="Selecionar Pasta de Destino", command=self.select_copy_directory)
        self.select_copy_button.pack()

        self.copy_dir_label = tk.Label(root, text="")
        self.copy_dir_label.pack()

        self.include_folders_var = tk.IntVar()
        self.include_folders_checkbox = tk.Checkbutton(root, text="Incluir Pastas", variable=self.include_folders_var)
        self.include_folders_checkbox.pack()

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

        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

    def create_image(self, width, height, color1, color2):
        # Generate an image and draw a pattern
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (width // 10, height // 10, width - width // 10, height - height // 10),
            fill=color2
        )
        return image

    def create_tray_icon(self):
        self.icon_image = self.create_image(64, 64, 'black', 'white')
        self.tray_icon = icon("Tray Icon",
                              self.icon_image,
                              menu=menu(
                                  item('Show', self.show_window),
                                  item('Quit', self.quit_app)
                              ))
        threading.Thread(target=self.tray_icon.run).start()

    def minimize_to_tray(self):
        self.root.withdraw()
        self.tray_icon.notify("Minimizado para a bandeja!")

    def show_window(self, icon, item):
        self.root.deiconify()

    def quit_app(self, icon, item):
        self.tray_icon.stop()
        self.root.quit()

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
            self.watcher = Watcher(self.watch_dir, self.copy_dir, bool(self.include_folders_var.get()), bool(self.copy_only_files_var.get()), self.log_text)
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
    