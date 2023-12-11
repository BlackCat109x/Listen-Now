import eyed3

class MP3MetadataEditor:
    @staticmethod
    def modify_metadata(path, title, artist, album, year, cover_path):
        try:
            audiofile = eyed3.load(path)
            audiofile.tag.title = title
            audiofile.tag.artist = artist
            audiofile.tag.album = album
            audiofile.tag.release_date = year

            if cover_path:
                cover_data = open(cover_path, "rb").read()
                audiofile.tag.images.set(3, cover_data, "image/jpeg", u"Cover")
            
            audiofile.tag.save()

        except Exception as e:
            print(f"Error during metadata modification: {e}")