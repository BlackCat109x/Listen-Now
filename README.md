# Listen Now - Music Player and Complements

![Python](https://img.shields.io/badge/Python-3.11%2B-blue) ![Platform](https://img.shields.io/badge/Platform-Windows-green) ![Language](https://img.shields.io/badge/Language-Spanish-orange) ![License](https://img.shields.io/badge/License-GNU%20v3.0-blue)

## Overview

This repository contains a package of three Python applications designed for Windows, providing a comprehensive music experience. The applications included are licensed under GNU v3.0. The applications are:

1.  **MP3 Music Player:** A feature-rich MP3 music player with an intuitive user interface, allowing you to enjoy your favorite tunes seamlessly.
    
2.  **YouTube to MP3 Downloader:** An application that facilitates downloading music from YouTube in MP3 format, making it easy to build your music library.
    
3.  **Album/Playlist Downloader:** A script designed to simplify the process of downloading entire albums or playlists, streamlining your music collection management.
    


## Requirements

-   Python 3.8 or higher
-   Windows operating system
-   Codex FFMPEG v40 (Full)

## Installation

1.  Clone the repository to your local machine.
    
    `git clone https://github.com/yourusername/Music-Player-and-Complements.git` 
    
2.  Navigate to the project directory.
    
    `cd Music-Player-and-Complements` 
    
3.  Install the required dependencies.
    
    `pip install -r requirements.txt` 
    
4.  Install FFMPEG v40 Full using Chocolatey.
    
    `choco install ffmpeg-full`

    
## Usage

1.  Launch the MP3 Music Player application.
  
    `cd '.\Music Player\'`
    
    `python main.py` 
    
3.  Run the YouTube to MP3 Downloader.
    
    `cd .\Downloader\`
    
    `python main.py` 
    
4.  Execute the Album/Playlist Downloader script.
    
    `cd .\Downloader\`
    
    `python playlist.py` 
    
Follow the on-screen instructions for each application to maximize your experience.


## Build with PyInstaller

### YouTube to MP3 Downloader

`cd '.\Music Player\'`

`pyinstaller --onefile --noconsole --add-data "scripts;scripts" --name 'YT to MP3' main.py` 

### Playlist Downloader

`cd .\Downloader\`

`pyinstaller --onefile --console --add-data "scripts;scripts" --name 'Download a Playlist' playlist.py` 

### MP3 Music Player

`cd .\Downloader\`

`pyinstaller --onefile --add-data "assets;assets" --noconsole --icon="./assets/img/icon.ico" --name "Listen Now - Music Player" main.py` 

Follow these commands to build each application using PyInstaller. Adjust the paths and filenames as needed for your project.

## Contributing

We welcome contributions! If you have ideas for improvement, new features, or bug fixes, please feel free to open an issue or submit a pull request.

## License

This project is licensed under the [GNU General Public License v3.0](https://chat.openai.com/c/LICENSE). Feel free to use, modify, and distribute the code as needed.

----------

¡Gracias por usar Music Player and Complements! Si tienes alguna pregunta o sugerencia, no dudes en ponerte en contacto con nosotros. ¡Disfruta de tu experiencia musical!
