import os
import youtube_dl
from scripts.downloader import YTtoMP3Downloader
from scripts.get_md import MusicMetadata
from datetime import datetime



class PlaylistDownloader:
    def __init__(self, playlist_url=""):
        self.playlist_url = playlist_url
        self.metadata_fetcher = MusicMetadata()
        self.ls = []
        self.startTime = datetime.now()

    def download_playlist(self):

        video_urls = self.get_video_urls()
        playlist_title = self.get_title(self.playlist_url)
        print()
        self.startTime = datetime.now()
        YTtoMP3Downloader(resource='playlist').download_playlist(video_urls, playlist_title)
        # os.system('cls')
        # print(f'La playlist fue descargada en: {datetime.now() - self.startTime}')
        # print('Presione enter para salir...')
        # input()

    def get_title(self, playlist_url):
        options = {
            'quiet': True,
            'noplaylist': True,
            'skip_download': True,  
            'extract_flat': True, 
            'max_downloads': 1, 
        }

        with youtube_dl.YoutubeDL(options) as ydl:
            info = ydl.extract_info(playlist_url)
            if info.get('title'):
                playlist_title = info.get('title')
            else:
                playlist_title = info.get('title', 'Unknown Playlist Title')

            return playlist_title

    def get_video_urls(self):
        print('Iniciando la busqueda de URLs...')
        try:
            ydl_opts = {
                'quiet': True,
                'noplaylist': True,
                'skip_download': True,
                'max_workers': 8,
                'extract_flat': True,
            }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(self.playlist_url, download=False)
                data = playlist_info.get('entries', [])
                print(f'La busqueda de URLs tardó: {datetime.now() - self.startTime}')
                print(f'La lista contiene {len(data)} elementos')
                for i in data:
                    url = f"https://youtube.com/watch?v={i.get('id')}"
                    self.ls.append(url)
                return self.ls
        except Exception as e:
            print(f"Error getting playlist video URLs: {e}")
            return []

if __name__ == "__main__":
    os.system('cls')
    playlist_url = input('Playlist URL: ')
    print()
    PlaylistDownloader(playlist_url).download_playlist()
