import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import eyed3
from scripts.get_md import MusicMetadata
from scripts.downloader import YTtoMP3Downloader
from scripts.metadata_editor import MP3MetadataEditor
from urllib.parse import urlparse, parse_qs, urlunparse

class YTtoMP3App:
    def __init__(self, master):
        self.master = master
        self.master.resizable(False, False)
        self.master.title("Convertidor de YT a MP3")
        self.cover_path = None

        self.create_widgets()

    def create_widgets(self):
        self.create_download_section()
        self.create_edit_section()

    def create_download_section(self):
        download_frame = ttk.LabelFrame(self.master, text="Descargar y Convertir a MP3")
        download_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        ttk.Label(download_frame, text="URL del video:").grid(row=0, column=0, padx=10, pady=10)

        self.url_entry = ttk.Entry(download_frame, width=40)
        self.url_entry.grid(row=0, column=1, padx=10, pady=10)

        ttk.Button(download_frame, text="Descargar y Convertir", command=self.download_and_convert).grid(row=0, column=2, padx=10, pady=10)

    def create_edit_section(self):
        edit_frame = ttk.LabelFrame(self.master, text="Editar MP3")
        edit_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        labels_and_entries = [
            ("Archivo de audio", 'file_path', "readonly", self.browse_file),
            ("Título", 'title', None, None),
            ("Artista", 'author', None, None),
            ("Álbum", 'album', None, None),
            ("Año de lanzamiento", 'year', None, None),
            ("Carátula", 'cover_path', "readonly", self.browse_cover),
            ("Metadatos desde URL", 'url_meta', None, self.url_md),
            ("Cover desde URL", 'url_cover', None, self.url_cover)
        ]

        for row, (label_text, entry, state, command) in enumerate(labels_and_entries):
            ttk.Label(edit_frame, text=label_text).grid(row=row, column=0, padx=10, pady=10)
            entry_widget = ttk.Entry(edit_frame, width=40, state=state)
            entry_widget.grid(row=row, column=1, padx=10, pady=10)
            setattr(self, f"{entry}_entry", entry_widget)

            if command:
                button = ttk.Button(edit_frame, text=f"Seleccionar {label_text}", command=command)
                button.grid(row=row, column=2, padx=10, pady=10)
                setattr(self, f"{entry}_button", button)

        ttk.Button(edit_frame, text="Guardar", command=self.save_metadata).grid(row=row+2, column=0, columnspan=3, pady=10)

    def url_cover(self):
        url = self.url_cover_entry.get()
        metadata = MusicMetadata().get_md(url)
        cover_url = metadata.get('cover_url')

        self.cover_path = YTtoMP3Downloader().download_cover(cover_url, 'cover', 'Music Downloader')

        if self.cover_path:
            self.cover_path_entry.config(state="normal")
            self.cover_path_entry.delete(0, tk.END)
            self.cover_path_entry.insert(0, self.cover_path)
            self.cover_path_entry.config(state="readonly")

    def url_md(self):
        url = self.url_meta_entry.get()
        metadata = MusicMetadata().get_md(url)
        
        self.title_entry.delete(0, tk.END)
        title_value = metadata["title"]
        if title_value:
            self.title_entry.insert(tk.END, title_value)

        self.author_entry.delete(0, tk.END)
        author_value = metadata["artist"]
        if author_value:
            self.author_entry.insert(tk.END, author_value)

        self.album_entry.delete(0, tk.END)
        album_value = metadata["album"]
        if album_value:
            self.album_entry.insert(tk.END, album_value)

        self.year_entry.delete(0, tk.END)
        year_value = metadata["release_date"]
        if year_value:
            self.year_entry.insert(tk.END, year_value)

    def download_and_convert(self):
        url = self.del_params(self.url_entry.get())
        title = MusicMetadata().get_md(url).get('title')
        if url:
            downloader = YTtoMP3Downloader(url, 'file')
            downloader.download('Music Downloader')

            if title == 'Unknown Title':
                messagebox.showwarning('Completado', 'El archivo se ha descargado y convertido con exito. Pero los metadatos de esta canción y su portada no estan disponibles en su url.')
                self.url_cover_button.config(state='disabled')
                self.url_meta_button.config(state='disabled')
            else:
                messagebox.showinfo('Completado', f'{title} se ha descargado con exito')
                self.url_cover_button.config(state="normal")
                self.url_meta_button.config(state="normal")

            self.file_path_entry.config(state="normal")
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, downloader.path)
            self.file_path_entry.config(state="readonly")

            self.url_meta_entry.delete(0, tk.END)
            self.url_cover_entry.delete(0, tk.END)
        
            self.url_meta_entry.insert(tk.END, self.del_params(url))
            self.url_cover_entry.insert(tk.END, self.del_params(url))

    def del_params(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        new_query_params = {'v': query_params.get('v', [''])[0]}
        new_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.params, '&'.join(f"{k}={v}" for k, v in new_query_params.items()), parsed_url.fragment))
        return new_url
        
    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos de audio", "*.mp3;*.wav")])
        if file_path:
            metadata = self.load_metadata(file_path)

            self.file_path_entry.config(state="normal")
            self.file_path_entry.delete(0, tk.END)
            self.file_path_entry.insert(0, file_path)
            self.file_path_entry.config(state="readonly")

            self.title_entry.delete(0, tk.END)
            title_value = metadata.get("title", "")
            if title_value:
                self.title_entry.insert(tk.END, title_value)
            else:
                self.title_entry.insert(tk.END, os.path.splitext(os.path.basename(file_path))[0])

            self.author_entry.delete(0, tk.END)
            author_value = metadata.get("artist", "")
            if author_value:
                self.author_entry.insert(tk.END, author_value)

            self.album_entry.delete(0, tk.END)
            album_value = metadata.get("album", "")
            if album_value:
                self.album_entry.insert(tk.END, album_value)

            self.year_entry.delete(0, tk.END)
            year_value = metadata.get("release_date", "")
            if year_value:
                self.year_entry.insert(tk.END, year_value)

    def browse_cover(self):
        cover_path = filedialog.askopenfilename(filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg")])
        self.cover_path_entry.config(state="normal")
        self.cover_path_entry.delete(0, tk.END)
        self.cover_path_entry.insert(0, cover_path)
        self.cover_path_entry.config(state="readonly")

    def save_metadata(self):
        file_path = self.file_path_entry.get()
        title = self.title_entry.get()
        author = self.author_entry.get()
        album = self.album_entry.get()
        year = self.year_entry.get()
        cover_path = self.cover_path_entry.get()

        if file_path:
            MP3MetadataEditor.modify_metadata(file_path, title, author, album, year, cover_path)
        
        if self.cover_path:
            os.remove(self.cover_path)

        messagebox.showinfo('Completado', 'Los datos fueron aplicados correctamente')

    def load_metadata(self, file_path):
        try:
            audiofile = eyed3.load(file_path)
            metadata = {
                "title": audiofile.tag.title,
                "artist": audiofile.tag.artist,
                "album": audiofile.tag.album,
                "release_date": audiofile.tag.release_date,
            }
            return metadata
        except Exception as e:
            return {}

if __name__ == "__main__":
    root = tk.Tk()
    app = YTtoMP3App(root)
    root.mainloop()
