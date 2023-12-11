from pytube import YouTube
from pydub import AudioSegment
import os
import requests
from .get_md import MusicMetadata
from .metadata_editor import MP3MetadataEditor
import re
from tqdm import tqdm


class YTtoMP3Downloader:
    def __init__(self, url=""):
        self.url = url
        self.file_path = None
        self.path = None
        self.dwn_need = True

    def download(self, a):
        try:
            base_path = os.path.join(os.path.expanduser("~"), "Downloads")
            base_path = os.path.abspath(base_path)
            if os.path.isabs(a):
                folder = a
            else:
                folder = os.path.join(base_path, a)

            yt = YouTube(self.url)
            video = yt.streams.filter(only_audio=True).first()

            video_title = re.sub(r'''[<>:"'/\\|?*,.]''', '', video.title)
            mp3_file = os.path.join(folder, f"{video_title}.mp3")
            
            if os.path.exists(mp3_file):
                tqdm.write(f'{video_title}.mp3 already exists. Skipping download.')
                self.dwn_need = False
                return mp3_file

            tqdm.write(f'Descargando {video_title} from {self.url}')
            file = os.path.join(folder, f"{video_title}.mp4")

            video.download(folder)

            f_path = self.convert(file)

            self.cover_need = True
            return f_path

        except Exception as e:
            print(f"Error during download: {e}")

    def convert(self, file):
        try:
            name = os.path.splitext(os.path.basename(file))[0] + ".mp3"
            self.path = os.path.join(os.path.dirname(file), name)
            audio = AudioSegment.from_file(file)
            audio.export(self.path, format="mp3")

            os.remove(file)
            return self.path

        except Exception as e:
            print(f"Error during conversion: {e}")

    def download_cover(self, cover_url, dw_file, a):
        base_path = os.path.join(os.path.expanduser("~"), "Downloads")
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
        base_path = os.path.join(os.path.expanduser("~"), "Downloads")
        try:
            for url in tqdm(videos, desc=f'Descargando {playlist_title}'):
                self.url = url
                
                playlist_path = os.path.join(base_path, playlist_title)
                file_path = self.download(playlist_path)

                if self.dwn_need:
                    metadata = MusicMetadata().get_md(url)
                    cover_url = metadata.get('cover_url')

                    cover_path = self.download_cover(cover_url, file_path, f'{playlist_title}/covers')
                    
                    self.modify_md(file_path, metadata, cover_path)

        except Exception as e:
            print(f"Error during playlist download: {e}")

    def modify_md(self, file_path, metadata, cover):
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
            print(f"Error modifying metadata for {file_path}: {e}")