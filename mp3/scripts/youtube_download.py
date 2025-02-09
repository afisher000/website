# %% -*- coding: utf-8 -*-
"""
Created on Sat Jul 16 19:46:53 2022

@author: afisher
"""
import os
import subprocess
from mutagen.id3 import ID3, TIT2, TPE1, TALB
import os

def youtube_download(track, download_dir="C:\\Users\\afish\\Music\\Youtube Downloaded"):
    # track is entry of Track model
    artistName = track.artist
    trackName = track.name

    filename = f'{artistName} - {trackName}.mp3'
    filepath = os.path.join(download_dir, filename)
    print(f'{filename}...')

    print('\tStarting download')
    # Download with yl-dlp (update to most recent version with "yt-dlp -U")
    sys_command = f'yt-dlp -x --audio-format mp3 "{url}" --output="{filepath}"'
    cmd = subprocess.run(sys_command, capture_output=True, encoding='UTF-8', shell=True)
    if cmd.returncode!=0:
        print(cmd.stderr)
    print('\tFinished download')

    # Update song tags
    print('\tUpdating tags')
    mp3file = ID3(filepath)
    mp3file['TIT2'] = TIT2(encoding=3, text=trackName)
    mp3file['TPE1'] = TPE1(encoding=3, text=artistName)
    mp3file['TALB'] = TALB(encoding=3, text='Main')
    mp3file.save()
    print('Finished changing tags\n')

    return
        

# %%
