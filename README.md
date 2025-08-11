# youtube-utils
Python utils for analyzing available data on YouTube.

# Content

- [YouTube Playlist Duration Calculator](#get-total-duration-of-audio-in-an-input-directory-uses-ffprobe)

## YouTube Playlist Duration Calculator
[scripts/youtube-playlist-duration.py](https://github.com/iuliiakr/youtube-utils/blob/main/scripts/youtube-playlist-duration.py)

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
python scripts/youtube-playlist-duration.py "https://www.youtube.com/playlist?list=PL-osiE80TeTucQ08e_hIs7B2tOltWf1Dd"
```

To calculate the duration of only the videos that are longer than 15 minutes:
```bash
python scripts/youtube-playlist-duration.py -d 15 "https://www.youtube.com/playlist?list=PL-osiE80TeTucQ08e_hIs7B2tOltWf1Dd"
```

To save the links of videos in the playlist that are longer than 30 minutes to a file named my_playlist.txt:
```bash
python scripts/youtube-playlist-duration.py -d 30 -s my_playlist.txt "https://www.youtube.com/playlist?list=PL-osiE80TeTucQ08e_hIs7B2tOltWf1Dd"
```
(This will create a my_playlist.txt file in the same directory.)

To use the saved file for bulk downloads:
```bash
yt-dlp -a long_videos.txt
```

