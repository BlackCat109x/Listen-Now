import youtube_dl

class MusicMetadata:
    def get_md(self, video_url):
        options = {
            'format': 'bestaudio/best',
            'extract_metadata': True,
            'quiet': True,
        }
        try:
            with youtube_dl.YoutubeDL(options) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                title = info.get('title', 'Unknown Title')
                artist = info.get('artist', 'Unknown Artist')
                album = info.get('album', 'Unknown Album')
                year = info.get('release_year', 'Unknown Year')
                cover_url = info.get('thumbnail', None)  # Assuming 'thumbnail' contains the cover URL

                return {"title": title, "artist": artist, "album": album, "release_date": year, "cover_url": cover_url}
        except Exception as e:
            return {"title": 'Unknown Title', "artist": 'Unknown Artist', "album": 'Unknown Album', "release_date": 'Unknown Year', "cover_url": None}

