
import os
import pafy

from pytube import Playlist
from pydub import AudioSegment
from unidecode import unidecode
from multiprocessing.pool import ThreadPool
import concurrent.futures


class Downloader():
    def __init__(self):
        self.counter = Counter()
        self.output_dir = ''
        self.allowParallelism = False

    def convert_file(self, input_file, desired_format, extra_audio=0, delete_old=True):
        name = input_file.split(os.sep)[-1]  # Get filename from filepath
        name = name.split('.')[0]  # Remove extension of filename
        output_file = os.path.join(self.output_dir, name+'.'+desired_format)
        print("Converting '", input_file, "' to ", desired_format)
        if os.path.exists(output_file):
            print("...already converted")
            return
        song = AudioSegment.from_file(input_file)
        song = song+extra_audio
        song.export(output_file, format=desired_format, bitrate="320k")
        if delete_old:
            os.remove(input_file)

    def download_song(self, url):
        self.counter.count()
        print(
            "____________________________________________ [",
            self.counter.prc,
            "%]\n",
            url
        )
        video = pafy.new(url)
        audio = video.getbestaudio()
        title = audio.title
        # # Replace also spaces for avoiding OS problems
        # for c in ['.', '\"', '|', "'", '/', ' ', '"', '+', '?']:
        #     title = title.replace(c, '_')
        title = unidecode(title)
        output_file = os.path.join(self.output_dir, title+'.'+audio.extension)
        desired_format = 'mp3'
        print("Going for... '", title, "'")
        if not os.path.exists(output_file) and not os.path.exists('.'.join(output_file.split('.')[:-1])+'.'+desired_format):
            print("Downloading...")
            audio.download(filepath=output_file, quiet=False, remux_audio=True)
        else:
            print("...is in local")

        self.convert_file(
            input_file=output_file,
            desired_format=desired_format
        )

    def download_songs(self, to_mp3, urls):
        to_mp3 = to_mp3
        n_urls = len(urls)
        print("____________________________________________")
        print(n_urls, " songs will be downloaded to ", self.output_dir)
        self.counter.getReady(until=len(urls))
        with concurrent.futures.ThreadPoolExecutor() as exector:
            exector.map(self.download_song, urls)
            print(n_urls, " downloaded songs are in ", self.output_dir)

    def download_playlist(self, playlist_url, output_dir='', to_mp3=True):
        self.output_dir = output_dir
        urls = Playlist(playlist_url)
        self.download_songs(urls=urls, to_mp3=to_mp3)


class Counter():
    def __init__(self):
        self.n = None
        self.until = None
        self.prc = None

    def getReady(self, until):
        self.n = 0
        self.until = until

    def count(self):
        self.n += 1
        self.prc = "{0:.2f}".format(100*self.n/self.until)
