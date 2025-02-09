import os
import subprocess
from mutagen.id3 import ID3, TIT2, TPE1, TALB
import time

def youtube_download(track, 
                     download_dir="C:\\Users\\afish\\Music\\iTunes\\iTunes Media\\Automatically Add to iTunes"):
    
    # Unpack track object from Track model
    artistName = track.artist
    trackName = track.name
    url = track.url

    # Define filepath
    filename = f'{artistName} - {trackName}.mp3'
    filepath = os.path.join(download_dir, filename)
    print(f'{filename}...')

    # Download with yl-dlp (update to most recent version with "yt-dlp -U")
    print('\tStarting download')
    sys_command = f'yt-dlp -x --audio-format mp3 "{url}" --output="{filepath}"'
    cmd = subprocess.run(sys_command, capture_output=True, encoding='UTF-8', shell=True, timeout=15)
    if cmd.returncode!=0:
        print(cmd.stderr)
    print('\tFinished download')


    print('\tUpdating tags')
    mp3file = ID3(filepath)
    mp3file['TIT2'] = TIT2(encoding=3, text=trackName)
    mp3file['TPE1'] = TPE1(encoding=3, text=artistName)
    mp3file['TALB'] = TALB(encoding=3, text='Main')
    mp3file.save()
    print('\tFinished changing tags\n')

    return
        

