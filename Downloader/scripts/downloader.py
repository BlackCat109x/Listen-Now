from pytube import YouTube
from pydub import AudioSegment
import os
import requests
from .get_md import MusicMetadata
from .metadata_editor import MP3MetadataEditor
import re
from tqdm import tqdm
from tkinter import messagebox
import colorama

class YTtoMP3Downloader:
    def __init__(self, url='', resource=''):
        self.url = url
        self.file_path = None
        self.path = None
        self.dwn_need = True
        self.resource = resource

    def get_ansi(self, hex_color):
        ansi_color = f'\033[38;2;{int(hex_color[1:3], 16)};{int(hex_color[3:5], 16)};{int(hex_color[5:], 16)}m'
        return ansi_color

    def download(self, a):
        yell = self.get_ansi('#f7f792')
        red = self.get_ansi('#ff3636')
        blue = self.get_ansi('#92a1f7')
        reset_color = '\033[0m'
        self.downloaded = []
        try:
            base_path = os.path.join(os.path.expanduser("~"), "Music")
            base_path = os.path.abspath(base_path)
            if os.path.isabs(a):
                folder = a
            else:
               folder = os.path.join(base_path, a)

            yt = YouTube(self.url)
            video = yt.streams.filter(only_audio=True).first()

            video_author =  re.sub(r'''[<>:"'/\\|?*,.]''', '', yt.author)
            video_title = re.sub(r'''[<>:"'/\\|?*,.]''', '', video.title)
            mp3_file = os.path.join(folder, f"{video_title} - {video_author}.mp3")
            
            if os.path.exists(mp3_file):
                if self.resource == 'playlist':
                    tqdm.write(f'{blue}{video_title}.mp3 ya existe. Saltando la descarga.{reset_color}')
                self.dwn_need = False
                self.path = mp3_file
                return mp3_file
            
            if self.resource == 'playlist':
                tqdm.write(f'{yell}Descargando {video_title} desde {self.url}{reset_color}')

            file = os.path.join(folder, f"{video_title}.mp4")

            video.download(folder)

            f_path = self.convert(file, video_author)

            if self.resource == 'playlist':
                tqdm.write(f'Completado\n')

            self.cover_need = True
            return f_path

        except Exception as e:
            if self.resource == 'playlist':
                tqdm.write(f"{red}Error durante la descarga: {e}{reset_color}")
            elif self.resource == 'file':
                messagebox.showerror('Error', f"Error durante la descarga: {e}")

    def convert(self, file, author):
        try:
            name = os.path.splitext(os.path.basename(file))[0] + f" - {author}.mp3"
            self.path = os.path.join(os.path.dirname(file), name)
            audio = AudioSegment.from_file(file)
            audio.export(self.path, format="mp3")

            os.remove(file)
            return self.path

        except Exception as e:
            if self.resource == 'playlist':
                tqdm.write(f"Error durante la conversión: {e}")
            elif self.resource == 'file':
                messagebox.showerror('Error', f"Error durante la conversión: {e}")

    def download_cover(self, cover_url, dw_file, a):
        base_path = os.path.join(os.path.expanduser("~"), "Music")
        base_path = os.path.abspath(base_path)
        save_path = os.path.join(base_path, a)
        if cover_url:
            response = requests.get(cover_url)
            if response.status_code == 200:
                if not os.path.exists(save_path):
                    os.makedirs(save_path)

                file_name = os.path.join(save_path, f'{os.path.splitext(os.path.basename(dw_file))[0]}.jpg')

                with open(file_name, 'wb') as file:
                    file.write(response.content)
            return file_name
        else:
            return None

    def download_playlist(self, videos, playlist_title):
        base_path = os.path.join(os.path.expanduser("~"), "Music")

        colorama.init()
        green = self.get_ansi('#92f7b2')
        red = self.get_ansi('#ff3636')
        reset_color = '\033[0m'

        try:
            for url in tqdm(videos, desc=f'{green}Descargando {playlist_title}{reset_color}'):
                self.url = url
                
                playlist_path = os.path.join(base_path, playlist_title)
                file_path = self.download(playlist_path)

                if self.dwn_need:
                    metadata = MusicMetadata().get_md(url)
                    cover_url = metadata.get('cover_url')

                    cover_path = self.download_cover(cover_url, file_path, f'{playlist_title}/covers')
                    
                    self.modify_md(file_path, metadata, cover_path)

        except Exception as e:
            tqdm.write(f"{red}Error durante la descarga de la lista de reproducción: {e}{reset_color}")

    def modify_md(self, file_path, metadata, cover):
        red = self.get_ansi('#ff3636')
        reset_color = '\033[0m'
        try:
            editor = MP3MetadataEditor()
            editor.modify_metadata(
                path=file_path,
                title=metadata['title'],
                artist=metadata['artist'],
                album=metadata['album'],
                year=metadata['release_date'],
                cover_path=cover
            )
        except Exception as e:
            if self.resource == 'playlist':
                tqdm.write(f"{red}Error modificando los metadatos de {file_path}: {e}{reset_color}")
            elif self.resource == 'file':
                messagebox.showerror('Error', f"Error modificando los metadatos de {file_path}: {e}")