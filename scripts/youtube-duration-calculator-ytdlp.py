#!/usr/bin/env python3
import sys
import subprocess
import json
import argparse # Standard library for command-line parsing

def get_playlist_duration_ytdlp(playlist_url, min_duration_minutes=0, save_file=None):
    """
    Calculates playlist duration using yt-dlp, with optional filters and
    the ability to save the resulting video links to a file.
    
    Args:
        playlist_url (str): The URL of the YouTube playlist.
        min_duration_minutes (int): The minimum duration in minutes for a video
                                     to be included. Defaults to 0 (all videos).
        save_file (str, optional): The path to a file where included video links
                                   will be saved. Defaults to None.
    """
    min_duration_seconds = min_duration_minutes * 60
    command = ['yt-dlp', '--flat-playlist', '-j', playlist_url]

    print("Fetching video list from playlist...")
    if min_duration_seconds > 0:
        print(f"Filter active: Only including videos longer than {min_duration_minutes} minute(s).")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
    except FileNotFoundError:
        print("Error: 'yt-dlp' command not found.")
        print("Please ensure yt-dlp is installed and in your system's PATH.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running yt-dlp. It might be a private/invalid playlist.\nDetails: {e.stderr}")
        return None
    
    total_seconds = 0
    total_videos_found = 0
    included_videos_count = 0
    included_video_links = [] # List to store links that meet the criteria
    
    video_lines = result.stdout.strip().split('\n')
    total_videos_found = len(video_lines)

    print(f"\nFound {total_videos_found} videos. Processing...")
    
    for line in video_lines:
        try:
            video_meta = json.loads(line)
            duration = video_meta.get('duration')

            if duration is not None:
                # The core filtering logic
                if duration >= min_duration_seconds:
                    total_seconds += duration
                    included_videos_count += 1
                    # Add the video's URL to our list for saving
                    video_url = video_meta.get('webpage_url')
                    if video_url:
                        included_video_links.append(video_url)
            else:
                print(f"Warning: Skipping video with no duration info: {video_meta.get('title', 'N/A')}")
        except (json.JSONDecodeError, KeyError):
            print("Warning: Could not parse metadata for one entry.")
            continue
    
    summary = f"\nProcessed {total_videos_found} videos."
    if min_duration_seconds > 0:
        summary += f" Included {included_videos_count} videos longer than {min_duration_minutes} minute(s)."
    else:
        summary += f" Included {included_videos_count} videos."
    print(summary)
    
    # --- File Saving Logic ---
    if save_file and included_video_links:
        print(f"\nSaving {len(included_video_links)} video links to '{save_file}'...")
        try:
            with open(save_file, 'w', encoding='utf-8') as f:
                for link in included_video_links:
                    f.write(link + '\n')
            print("File saved successfully.")
        except IOError as e:
            print(f"Error: Could not write to file '{save_file}'. Reason: {e}")

    # Format the total duration into HH:MM:SS
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    return f"{hours:02}:{minutes:02}:{seconds:02}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate total duration of a YouTube playlist with optional filtering and link saving.",
        epilog="Example: python %(prog)s 'https://...' -d 10 -s videos_to_download.txt"
    )
    
    parser.add_argument(
        "url",
        help="The full URL of the YouTube playlist. MUST be wrapped in quotes."
    )
    
    parser.add_argument(
        "-d", "--min-duration",
        type=int,
        default=0,
        metavar="MINUTES",
        help="Optional: Only include videos longer than this number of minutes. Default is 0 (include all)."
    )

    # --- New argument for saving the file ---
    parser.add_argument(
        "-s", "--save-file",
        type=str,
        default=None,
        metavar="FILENAME",
        help="Optional: Save the links of included videos to the specified text file."
    )
    
    args = parser.parse_args()
    
    total_duration = get_playlist_duration_ytdlp(
        playlist_url=args.url, 
        min_duration_minutes=args.min_duration, 
        save_file=args.save_file
    )

    if total_duration is not None:
        print("\n" + "="*40)
        print(f"Total Duration of Included Videos: {total_duration}")
        print("="*40)
