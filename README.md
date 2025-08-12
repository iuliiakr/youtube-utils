# youtube-utils
Python utils for analyzing available data on YouTube.

# Content

youtube_duration_calculator_api.py
- [YouTube Playlist Duration Calculator (uses YouTube Data API v3)](#youtube-playlist-duration-calculator) - for large projects
- [YouTube Playlist Duration Calculator (uses yt-dlp)](#youtube-playlist-duration-calculator) - for quick jobs


## YouTube Playlist Duration Calculator (uses YouTube Data API v3)
[scripts/youtube-duration-calculator-ytdlp.py](https://github.com/iuliiakr/youtube-utils/blob/main/scripts/youtube-duration-calculator-ytdlp.py)

Uses the YouTube Data API to calculate the total duration of videos from a YouTube channel, playlist, single video, or a list of URLs in a text file.
Options:
- <b>Duration filtering</b>: include only videos longer than [MINIMAL_DURATION_IN_MINUTES],
- <b>Batch processing</b>: input TXT file with links to YouTube videos, playlists or channels,
- <b>Export links</b>: save links to videos, included in calculation, to a TXT file (for download).

<br>

## YouTube Playlist Duration Calculator (uses yt-dlp)
[scripts/youtube-duration-calculator-ytdlp.py](https://github.com/iuliiakr/youtube-utils/blob/main/scripts/youtube-duration-calculator-ytdlp.py)

Calculates the total duration of all videos from a link to YouTube playlist or a channel.
Outputs duration in HH:MM:SS format and number of files.

Uses yt-dlp.
```bash
pip install --upgrade yt-dlp
```

### Usage:
```bash
python playlist_duration_ytdlp.py [OPTIONS] "YOUTUBE_URL"
```
<b>IMPORTANT:</b> Wrap the YouTube playlist URL in single (') or double (") quotes.

Arguments and Options:
- url (Required): The full URL of the YouTube playlist.
- -d, --min-duration MINUTES (Optional): Only include videos longer than this number of minutes.
- -s, --save-file FILENAME (Optional): Save the links of all included videos to the specified text file.
- -h, --help: Shows the help message with all available options.

### Examples

Basic
```bash
python scripts/youtube-playlist-duration.py "[URL]"
```

To calculate the duration of only the videos that are longer than 15 minutes:
```bash
python scripts/youtube-playlist-duration.py -d 15 "[URL]"
```

To save the links of videos in the playlist that are longer than 30 minutes to a file named my_playlist.txt:
```bash
python scripts/youtube-playlist-duration.py -d 30 -s [my_playlist.txt] "[URL]"
```
(This will create a my_playlist.txt file in the same directory.)

To use the saved file for bulk downloads:
```bash
yt-dlp -a [my_playlist.txt]
```

