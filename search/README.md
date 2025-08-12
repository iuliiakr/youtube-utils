# YouTube Advanced Search

A Python tool for searching YouTube videos using the **YouTube Data API v3** with advanced filters for language, country, and video duration.  
Supports both YouTube's built-in duration categories and a **custom minimum duration filter**.

<br>

## ✨ Features
- Search YouTube videos by **keyword**.
- Filter results by:
  - **Language** (`--language`)
  - **Country bias** (`--country`)
  - **Built-in duration filters** (`short`, `medium`, `long`)
  - **Custom minimum duration** in minutes
- Limit the number of results returned.
- Output results to **console**, **TXT**, or **JSON** file.
- Automatically formats video durations as `HH:MM:SS`.

<br>

### Install dependencies:

```bash
pip install google-api-python-client isodate
```

### Set your YouTube API key:

```bash
export YOUTUBE_API_KEY="YOUR_API_KEY_HERE"
```
You can obtain an API key from the Google Cloud Console.

<br>

## 🚀 Usage
Basic syntax:
```bash
python3 youtube_search.py "SEARCH_QUERY" LANGUAGE_CODE [OPTIONS]
```

### Examples:

Search for Python tutorials in English:
```bash
python3 youtube_search.py "Python tutorial" en
```

Search for cooking videos in French, biased to Canadian results:
```bash
python3 youtube_search.py "recette de cuisine" fr --country CA
```

Search for long-duration interviews in Spanish, at least 30 minutes:
```bash
python3 youtube_search.py "entrevista" es --min-duration 30
```

Save results to a JSON file:
```bash
python3 youtube_search.py "lofi hip hop" en -n 20 -o results.json
```

<br>

## ⚙️ Command-Line Arguments
| Argument               | Type / Choices                   | Description                                                  |
| ---------------------- | -------------------------------- | ------------------------------------------------------------ |
| `query`                | string                           | Search term or phrase.                                       |
| `language`             | ISO 639-1 code                   | Two-letter language code (e.g., `en`, `es`, `fr`).           |
| `-c`, `--country`      | ISO 3166-1 Alpha-2 code          | Country bias for results (e.g., `US`, `CA`, `GB`).           |
| `-d`, `--duration`     | `any`, `short`, `medium`, `long` | Built-in YouTube duration filter (default: `any`).           |
| `-m`, `--min-duration` | integer (minutes)                | Custom **minimum** duration filter (overrides `--duration`). |
| `-n`, `--max-results`  | integer (1–50)                   | Number of results to return (default: `10`).                 |
| `-o`, `--output`       | `.txt` or `.json` filename       | Save output to file instead of printing to console.          |

<br>

## Output Format
- Console:
```bash
[00:15:42] Sample Video Title - (Channel Name)
    https://www.youtube.com/watch?v=VIDEO_ID
```

- TXT file: Same format as console output.

- JSON file: Structured list of video details:
```bash
 [
    {
        "title": "Sample Video",
        "channel": "Channel Name",
        "duration": "00:15:42",
        "url": "https://www.youtube.com/watch?v=VIDEO_ID",
        "videoId": "VIDEO_ID"
    }
]
```

<br>

 ## 🛠 Troubleshooting
 
 - YOUTUBE_API_KEY environment variable not set: Make sure you’ve exported the API key in your terminal session.

- ImportError: Install the missing dependencies:
```bash
pip install google-api-python-client isodate
```
