#!/usr/bin/env python3

import os
import re
import argparse
from datetime import timedelta, datetime

# Third-party libraries
# You may need to install these:
# pip install google-api-python-client isodate
try:
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import isodate
except ImportError:
    print("Required libraries not found. Please run:")
    print("pip install google-api-python-client isodate")
    exit(1)


def get_youtube_service():
    """Initializes and returns the YouTube Data API service object."""
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY environment variable not set.")
        print("Please get an API key from the Google Cloud Console and set it.")
        return None
    try:
        return build('youtube', 'v3', developerKey=api_key)
    except Exception as e:
        print(f"Error building YouTube service: {e}")
        return None

def parse_url(url):
    """Parses a YouTube URL to find a playlist, channel, or video ID."""
    playlist_match = re.search(r'list=([a-zA-Z0-9_-]+)', url)
    if playlist_match:
        return 'playlist', playlist_match.group(1)
    video_match = re.search(r'(?:watch\?v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})', url)
    if video_match:
        return 'video', video_match.group(1)
    channel_match = re.search(r'/(channel|c|@)/([a-zA-Z0-9_.-]+)', url)
    if channel_match:
        return 'channel', channel_match.group(2)
    return None, None

def get_uploads_playlist_id(youtube, channel_id_or_handle):
    """Given a channel ID or handle, finds the ID of its 'uploads' playlist."""
    try:
        request = youtube.channels().list(
            part='contentDetails',
            id=channel_id_or_handle if channel_id_or_handle.startswith('UC') else None,
            forUsername=channel_id_or_handle if not channel_id_or_handle.startswith('@') and not channel_id_or_handle.startswith('UC') else None,
        )
        response = request.execute()
        if not response.get('items') and channel_id_or_handle.startswith('@'):
             search_request = youtube.search().list(part='id', q=channel_id_or_handle, type='channel', maxResults=1)
             search_response = search_request.execute()
             if not search_response.get('items'): return None
             channel_id = search_response['items'][0]['id']['channelId']
             request = youtube.channels().list(part='contentDetails', id=channel_id)
             response = request.execute()
        if not response.get('items'): return None
        return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return None

def get_playlist_video_ids(youtube, playlist_id):
    """Fetches all video IDs from a playlist, handling pagination."""
    video_ids = []
    next_page_token = None
    while True:
        try:
            request = youtube.playlistItems().list(part='contentDetails', playlistId=playlist_id, maxResults=50, pageToken=next_page_token)
            response = request.execute()
            video_ids.extend([item['contentDetails']['videoId'] for item in response.get('items', [])])
            next_page_token = response.get('nextPageToken')
            if not next_page_token: break
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred while fetching playlist items: {e.content}")
            return []
    return video_ids

def get_videos_duration(youtube, video_ids, min_duration_minutes, save_links):
    """
    Fetches durations for video IDs, filters them, and returns aggregated data.
    Returns a tuple: (total_duration, included_links, included_count).
    """
    total_duration = timedelta()
    included_links = []
    included_count = 0
    min_duration_td = timedelta(minutes=min_duration_minutes)
    
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        try:
            request = youtube.videos().list(part='contentDetails', id=','.join(chunk))
            response = request.execute()
            for item in response.get('items', []):
                duration_td = isodate.parse_duration(item['contentDetails']['duration'])
                if duration_td >= min_duration_td:
                    total_duration += duration_td
                    included_count += 1
                    if save_links:
                        included_links.append(f"https://www.youtube.com/watch?v={item['id']}")
        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred while fetching video details: {e.content}")
            continue
    return total_duration, included_links, included_count

def format_timedelta(td):
    """Formats a timedelta object into a human-readable string."""
    total_seconds = int(td.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    if days > 0:
        return f"{days} days, {hours:02}:{minutes:02}:{seconds:02}"
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def main():
    parser = argparse.ArgumentParser(
        description="Calculate video duration from a YouTube URL or a file of URLs.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("source", help="A YouTube URL (channel, playlist, video) OR a path to a .txt file containing URLs (one per line).")
    parser.add_argument("-m", "--min-duration", type=int, default=0, help="Minimum duration in MINUTES for a video to be included. Default: 0.")
    parser.add_argument("-s", "--save-links", action="store_true", help="Save the links of included videos to a .txt file.")
    args = parser.parse_args()

    youtube = get_youtube_service()
    if not youtube: return

    urls_to_process = []
    if os.path.isfile(args.source) and args.source.lower().endswith('.txt'):
        print(f"Reading URLs from file: {args.source}")
        with open(args.source, 'r') as f:
            urls_to_process = [line.strip() for line in f if line.strip()]
        if not urls_to_process:
            print("File is empty or contains no valid lines.")
            return
    else:
        urls_to_process = [args.source]

    # --- Aggregators for the final report ---
    grand_total_duration = timedelta()
    total_videos_found = 0
    total_videos_included = 0
    all_included_links = []
    
    print(f"\nProcessing {len(urls_to_process)} source(s)...")

    for i, url in enumerate(urls_to_process):
        print(f"\n[{i+1}/{len(urls_to_process)}] Processing: {url}")
        url_type, entity_id = parse_url(url)
        if not url_type:
            print("--> Error: Invalid or unsupported YouTube URL. Skipping.")
            continue

        video_ids = []
        if url_type == 'video':
            video_ids = [entity_id]
        elif url_type == 'channel':
            playlist_id = get_uploads_playlist_id(youtube, entity_id)
            if not playlist_id:
                print("--> Error: Could not find uploads playlist for this channel. Skipping.")
                continue
            video_ids = get_playlist_video_ids(youtube, playlist_id)
        elif url_type == 'playlist':
            video_ids = get_playlist_video_ids(youtube, entity_id)

        if not video_ids:
            print("--> No videos found for this source.")
            continue
        
        current_found_count = len(video_ids)
        total_videos_found += current_found_count
        print(f"--> Found {current_found_count} video(s). Fetching details...")

        duration, links, count = get_videos_duration(youtube, video_ids, args.min_duration, args.save_links)
        
        grand_total_duration += duration
        total_videos_included += count
        if args.save_links:
            all_included_links.extend(links)
        
        print(f"--> Done. Added {count} videos with a total duration of {format_timedelta(duration)} to the calculation.")

    # --- Final Report ---
    print("\n" + "="*20)
    print("      FINAL REPORT")
    print("="*20)
    print(f"Total videos found across all sources: {total_videos_found}")
    if args.min_duration > 0:
        print(f"Videos included in calculation (>= {args.min_duration} min): {total_videos_included}")
    else:
        print(f"Videos included in calculation: {total_videos_included}")
    print(f"Total duration of included videos: {format_timedelta(grand_total_duration)}")
    print("="*20)

    if args.save_links:
        if all_included_links:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"youtube_links_{timestamp}.txt"
            with open(output_filename, 'w') as f:
                for link in all_included_links:
                    f.write(link + '\n')
            print(f"Successfully saved {len(all_included_links)} video link(s) to '{output_filename}'")
        else:
            print("No videos met the criteria to be saved to the links file.")

if __name__ == '__main__':
    main()
