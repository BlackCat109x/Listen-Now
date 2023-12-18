import sys
import os
import tkinter as tk
from tkinter import filedialog
from pygame import mixer
from PIL import Image, ImageTk
import eyed3
import io
import random

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.initialize_gui()
        self.playlist = []
        self.og = False
        self.original_playlist = []
        self.current_index = 0
        self.playing = False
        
    def initialize_gui(self):
        self.base_path = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
        self.root.title("Music Player - Listen Now")
        self.root.geometry("400x700")
        self.root.resizable(False, False)
        self.root.iconbitmap(os.path.join(self.base_path, "assets", "img", "icon.ico"))
        self.root.config(bg="#474747")
        for i in range(4):
            self.root.columnconfigure(i, weight=1)

        mixer.init()
        self.font = (os.path.join(self.base_path, "assets", "fonts", "Quicksand-Regular.ttf"), 15)
        self.create_widgets()

    def create_widgets(self):
        self.sel_btn_img = self.btn_img('add', 50)
        select_button = tk.Button(self.root, image=self.sel_btn_img, command=self.select_song, bg="#474747", fg="white", border=0, font=self.font, cursor="hand2")
        select_button.grid(row=0, column=3, sticky="e", padx=5, pady=5)

        self.clear_btn_img = self.btn_img('exit', 50)
        clear_button = tk.Button(self.root, image=self.clear_btn_img, command=self.clear_player, bg="#474747", fg="white", border=0, font=self.font, cursor="hand2")
        clear_button.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.shuffle_btn_img = self.btn_img('shuffle_off', 50)
        self.shuffle_button = tk.Button(self.root, image=self.shuffle_btn_img, command=self.shuffle_playlist, bg="#474747", fg="white", border=0, font=self.font, cursor="hand2")
        self.shuffle_button.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        self.song_image = tk.PhotoImage()
        self.image_label = tk.Label(self.root, image=self.song_image, bg="#474747", font=self.font)
        self.image_label.grid(row=1, column=0, columnspan=4, pady=15)

        metadata_frame = tk.Frame(self.root, bg="#474747")
        metadata_frame.grid(row=2, column=0, columnspan=4, pady=15)

        self.create_label(metadata_frame)

        self.progress_bar = tk.Scale(self.root, from_=0, to=100, orient="horizontal", length=300, width=20, showvalue=0, sliderlength=5, bg="red", fg="white", troughcolor="white", border=0, font=self.font)
        self.progress_bar.grid(row=3, column=0, columnspan=4, pady=15)
        self.progress_bar.bind("<Button-1>", lambda event: "break")

        self.time_label = tk.Label(self.root, text='0:00 / 0:00', font=self.font, fg='white', bg="#474747")
        self.time_label.grid(row=4, column=0, columnspan=4)

        buttons_frame = tk.Frame(self.root, bg="#474747")
        buttons_frame.grid(row=5, column=0, columnspan=4, pady=20)

        self.create_button(buttons_frame, "prev", self.play_previous, btn='previous')
        self.create_button(buttons_frame, "play", self.play_pause, btn='play_pause')
        self.create_button(buttons_frame, "stop", self.restart_song, btn='restart')
        self.create_button(buttons_frame, "next", self.play_next, btn='next')

        self.root.after(1000, self.update_progress)

        volume_frame = tk.Frame(self.root, bg="#474747")
        volume_frame.grid(row=6, column=0, columnspan=4, pady=10)

        self.volume_control(volume_frame)
    
        self.queue_count_label = tk.Label(self.root, text='0', font=self.font, fg='white', bg="#474747")
        self.queue_count_label.grid(row=7, column=3, pady=15, padx=40)

        self.queue_btn_img = self.btn_img('queue', 40)
        queue_button = tk.Button(self.root, image=self.queue_btn_img, command=self.show_queue, bg="#474747", fg="white", border=0, font=self.font, cursor="hand2")
        queue_button.grid(row=7, column=3, padx=15,pady=15, sticky='se')

    def update_queue_count_label(self):
        count = len(self.playlist)
        self.queue_count_label.config(text=f'{count}')

    def shuffle_playlist(self):
        if not hasattr(self, 'shuffle_state') or self.shuffle_state == 'shuffle_off':
            self.shuffle_state = 'shuffle_on'
            self.shuffle_btn_img = self.btn_img('shuffle_on', 50)
            random.shuffle(self.playlist)
            self.current_index = 0
            self.play_selected_song()
        else:
            self.shuffle_state = 'shuffle_off'
            self.shuffle_btn_img = self.btn_img('shuffle_off', 50)
            self.playlist = self.original_playlist.copy()
            self.current_index = 0
            self.play_selected_song()
        self.shuffle_button.config(image=self.shuffle_btn_img)

    def show_queue(self, event=None):
        queue_window = tk.Toplevel(self.root)
        queue_window.title("Cola de Reproducción")
        queue_window.geometry("400x400")

        playlist_listbox = tk.Listbox(queue_window, selectmode=tk.SINGLE, font=self.font, bg="#474747", fg="white")
        for song_path in self.playlist:
            title, author, _, _ = self.extract_metadata(song_path)
            song_info = f"{title} - {author}"
            playlist_listbox.insert(tk.END, song_info)

        playlist_listbox.pack(expand=True, fill="both")

        def play_selected_song(event):
            selected_index = playlist_listbox.curselection()
            if selected_index:
                self.current_index = selected_index[0]
                self.play_selected_song()

        playlist_listbox.bind("<Double-Button-1>", play_selected_song)

    def format_time(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        return f"{int(minutes):02d}:{int(seconds):02d}"

    def create_label(self, frame):
        self.title_label = tk.Label(frame, text='', font=self.font, fg='white', bg="#474747")
        self.album_label = tk.Label(frame, text='', font=self.font, fg='white', bg="#474747")
        self.title_label.pack(padx=5, pady=5)
        self.album_label.pack(padx=5, pady=5)

    def extract_metadata(self, file_path):
        audiofile = eyed3.load(file_path)
        title = audiofile.tag.title if audiofile.tag and audiofile.tag.title else ""
        authors = audiofile.tag.artist.split(",") if audiofile.tag and audiofile.tag.artist else [""]
        author = authors[0].strip()
        album = audiofile.tag.album if audiofile.tag and audiofile.tag.album else ""
        year = str(audiofile.tag.getBestDate()) if audiofile.tag and audiofile.tag.getBestDate() else ""
    
        title = self.truncate_with_ellipsis(title, 22)
        author = self.truncate_with_ellipsis(author, 15)
        album = self.truncate_with_ellipsis(album, 34)

        return title, author, album, year

    def truncate_with_ellipsis(self, text, max_length):
        if len(text) > max_length:
            return text[:max_length-3] + "..."
        return text

    def volume_control(self, frame):
        self.sound_img = self.btn_img('sound', 30)
        self.sound_button = tk.Button(frame, image=self.sound_img, command=self.toggle_mute, bg="#474747", border=0, cursor="hand2")
        self.sound_button.grid(row=0, column=0, padx=10)

        self.volume_bar = tk.Scale(frame, from_=0, to=100, orient="horizontal", length=200, width=10, showvalue=0, bg="red", fg="white", troughcolor="white", border=0, font=self.font, command=self.update_volume)
        self.volume_bar.set(50)
        self.volume_bar.grid(row=0, column=1, padx=10)

        self.volume_label = tk.Label(frame, text="Volumen: 50", font=self.font, fg="white", bg="#474747")
        self.volume_label.grid(row=0, column=2, padx=10)

    def toggle_mute(self):
        if mixer.music.get_volume() == 0:
            self.new_sound = self.btn_img('sound', 30)
            self.sound_button.config(image=self.new_sound)
        else:
            self.new_sound = self.btn_img('mute', 30)
            self.sound_button.config(image=self.new_sound)
            mixer.music.set_volume(0)
            self.volume_bar.set(0)

    def update_volume(self, event=None):
        volume_value = self.volume_bar.get()
        if volume_value > 0:
            self.new_sound = self.btn_img('sound', 30)
            self.sound_button.config(image=self.new_sound)
        else:
            self.new_sound = self.btn_img('mute', 30)
            self.sound_button.config(image=self.new_sound)
        mixer.music.set_volume(volume_value / 100)
        self.volume_label.config(text=f"{volume_value}")

    def create_button(self, frame, image_name, command, btn=''):
        img_path = os.path.join(self.base_path, "assets", "img", "buttons", f"{image_name}.png")
        img = Image.open(img_path).resize((40, 40))
        img = ImageTk.PhotoImage(img)
        
        button = tk.Button(frame, image=img, command=command, bg="#474747", border=0, cursor="hand2")
        button.image = img
        button.pack(side="left", padx=20)
        setattr(self, btn + '_button', button)

    def select_song(self):
        self.og = False
        file_paths = filedialog.askopenfilenames(title="Seleccionar Canciones", filetypes=[("Archivos de audio", "*.mp3;*.wav")])
        
        if not self.playlist:
            self.playlist = list(file_paths)
            self.original_playlist = list(file_paths)
            self.og = True
            self.current_index = 0
            self.play_selected_song()  
        else:
            self.playlist.extend(file_paths)

            if not self.og:
                self.original_playlist.extend(file_paths)

        self.update_queue_count_label()

    def clear_player(self):
        mixer.music.stop()
        self.playlist = []
        self.current_index = 0
        self.playing = False
        self.title_label.config(text='')
        self.album_label.config(text='')
        self.image_label.config(image='')
        self.progress_bar.set(0)
        self.nw_img = self.btn_img('play', 40)
        self.play_pause_button.config(image=self.nw_img)
        self.update_queue_count_label()

    def play_previous(self):
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play_selected_song()

    def play_next(self):
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play_selected_song()

    def restart_song(self):
        if self.playlist:
            self.play_selected_song()
            self.playing = True
            self.play_pause()

    def play_selected_song(self):
        if self.playlist:
            file_path = self.playlist[self.current_index]
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            title, author, album, year = self.extract_metadata(file_path)
            
            if title and author and album and year:
                first_line = f"{title} • {author}"
                second_line = f"{album} • {year}"
                self.title_label.config(text=first_line)
                self.album_label.config(text=second_line)
            else:
                self.title_label.config(text=file_name)
                self.album_label.config(text="Sin datos")

            self.load_song_image(file_path)

            mixer.music.load(file_path)
            mixer.music.set_volume(0.5)
            mixer.music.play()
            self.new_btn = self.btn_img('pause', 40)
            self.play_pause_button.config(image=self.new_btn)
            self.playing = True

            song_length = mixer.Sound(file_path).get_length()
            self.progress_bar.config(to=song_length)

            self.root.after(1000, self.update_progress)

    def load_song_image(self, file_path):
        audiofile = eyed3.load(file_path)
        img = Image.open(io.BytesIO(audiofile.tag.images[0].image_data)) if audiofile.tag and audiofile.tag.images else Image.open(os.path.join(self.base_path, "assets", "img", "default.png"))
        img = img.resize((350, 198))
        self.song_image = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.song_image)

    def play_pause(self):
        if self.playing:
            mixer.music.pause()
            self.playing = False
            self.new_btn = self.btn_img('play', 40)
            self.play_pause_button.config(image=self.new_btn)
        else:
            mixer.music.unpause()
            self.playing = True
            self.new_btn = self.btn_img('pause', 40)
            self.play_pause_button.config(image=self.new_btn)

    def btn_img(self, img_name, s):
        img_path = os.path.join(self.base_path, "assets", "img", "buttons", f"{img_name}.png")
        img = Image.open(img_path).resize((s, s))
        
        return ImageTk.PhotoImage(img)

    def update_progress(self):
        current_time = mixer.music.get_pos() // 1000
        total_time = self.progress_bar['to']
        time_label_text = f"{self.format_time(current_time)} / {self.format_time(total_time)}"
        self.time_label.config(text=time_label_text)
        self.progress_bar.set(current_time)

        self.root.after(1000, self.update_progress)
        if not mixer.music.get_busy() and self.playing:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            self.play_selected_song()   

if __name__ == "__main__":
    root = tk.Tk()
    app = MusicPlayer(root)
    root.mainloop()
