#!/usr/bin/env python3

import os
import json
import argparse
from datetime import timedelta

# Third-party libraries
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
        return None
    try:
        return build('youtube', 'v3', developerKey=api_key)
    except Exception as e:
        print(f"Error building YouTube service: {e}")
        return None

def format_timedelta(td):
    """Formats a timedelta object into a human-readable HH:MM:SS string."""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def search_youtube(youtube, query, language, country, duration, max_results, min_duration_minutes):
    """
    Searches YouTube and returns a list of dictionaries containing video details.
    """
    # Build a descriptive search string for user feedback
    search_desc = f"Searching for '{query}' (lang: {language}"
    if country:
        search_desc += f", country: {country.upper()}"
    if min_duration_minutes:
        search_desc += f", min duration: {min_duration_minutes}m"
    else:
        search_desc += f", duration: {duration}"
    search_desc += f", max: {max_results})"
    print(f"\n{search_desc}")

    # --- Logic for custom --min-duration filter ---
    if min_duration_minutes:
        print("Note: Custom duration filter requires fetching more results initially, this may take longer.")
        min_duration_td = timedelta(minutes=min_duration_minutes)
        final_results = []
        next_page_token = None
        
        for _ in range(5): # Loop a max of 5 times to avoid exhausting quota
            try:
                params = {
                    'part': 'id,snippet', 'q': query, 'relevanceLanguage': language,
                    'type': 'video', 'maxResults': 50, 'pageToken': next_page_token
                }
                if country: params['regionCode'] = country
                
                search_request = youtube.search().list(**params)
                search_response = search_request.execute()
            except HttpError as e:
                print(f"--> An HTTP error {e.resp.status} occurred: {e.content}")
                break

            video_ids = [item['id']['videoId'] for item in search_response.get('items', [])]
            if not video_ids: break
            
            try:
                video_request = youtube.videos().list(part="contentDetails", id=",".join(video_ids))
                video_response = video_request.execute()
            except HttpError as e:
                print(f"--> An HTTP error {e.resp.status} occurred while fetching details: {e.content}")
                break
            
            video_details = {item['id']: item for item in video_response.get('items', [])}
            
            for search_item in search_response.get('items', []):
                video_id = search_item['id']['videoId']
                if video_id in video_details:
                    duration_iso = video_details[video_id]['contentDetails'].get('duration', 'PT0S')
                    duration_td = isodate.parse_duration(duration_iso)
                    
                    if duration_td >= min_duration_td:
                        final_results.append({
                            "title": search_item['snippet']['title'],
                            "channel": search_item['snippet']['channelTitle'],
                            "duration": format_timedelta(duration_td),
                            "url": f"https://www.youtube.com/watch?v={video_id}",
                            "videoId": video_id
                        })
                        if len(final_results) >= max_results:
                            return final_results[:max_results]
            
            next_page_token = search_response.get('nextPageToken')
            if not next_page_token: break
        return final_results[:max_results]

    # --- Default logic for built-in duration filters ---
    else:
        try:
            params = {
                'part': 'id,snippet', 'q': query, 'relevanceLanguage': language,
                'type': 'video', 'videoDuration': duration, 'maxResults': max_results
            }
            if country: params['regionCode'] = country

            search_request = youtube.search().list(**params)
            search_response = search_request.execute()
        except HttpError as e:
            print(f"--> An HTTP error {e.resp.status} occurred: {e.content}")
            return []

        search_results = search_response.get('items', [])
        if not search_results: return []
        video_ids = [item['id']['videoId'] for item in search_results]
        
        try:
            video_request = youtube.videos().list(part="contentDetails", id=",".join(video_ids))
            video_response = video_request.execute()
        except HttpError as e:
            print(f"--> An HTTP error {e.resp.status} occurred while fetching details: {e.content}")
            return []

        video_durations = {
            item['id']: format_timedelta(isodate.parse_duration(item['contentDetails'].get('duration', 'PT0S')))
            for item in video_response.get('items', [])
        }
        return [{
            "title": item['snippet']['title'], "channel": item['snippet']['channelTitle'],
            "duration": video_durations.get(item['id']['videoId'], "[N/A]"),
            "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}", "videoId": item['id']['videoId']
        } for item in search_results]


def save_results(results, filename):
    # (This function remains unchanged)
    if filename.lower().endswith('.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"\nSuccessfully saved {len(results)} results to '{filename}' (JSON format).")
    elif filename.lower().endswith('.txt'):
        with open(filename, 'w', encoding='utf-8') as f:
            for item in results:
                f.write(f"[{item['duration']}] {item['title']} - ({item['channel']})\n")
                f.write(f"    {item['url']}\n\n")
        print(f"\nSuccessfully saved {len(results)} results to '{filename}' (TXT format).")
    else:
        print(f"\nError: Invalid output file format. Please use a '.txt' or '.json' extension.")


def print_results_to_console(results):
    # (This function remains unchanged)
    print("\n--- Search Results ---")
    for item in results:
        print(f"[{item['duration']}] {item['title']} - ({item['channel']})")
        print(f"    {item['url']}\n")

def main():
    parser = argparse.ArgumentParser(
        description="Search YouTube with advanced filters for language, country, and duration.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("query", help="The search term or phrase.")
    parser.add_argument("language", help="The ISO 639-1 two-letter language code (e.g., en, es, fr).")
    
    # NEW --country flag
    parser.add_argument(
        "-c", "--country",
        metavar='CODE',
        help="Bias search results to a country (ISO 3166-1 Alpha-2 code, e.g., US, CA, GB)."
    )

    duration_group = parser.add_argument_group('Duration Filters (use only one)')
    duration_group.add_argument(
        "-d", "--duration", choices=['any', 'short', 'medium', 'long'], default='any',
        help="Filter by built-in duration categories."
    )
    duration_group.add_argument(
        "-m", "--min-duration", type=int, metavar='MIN',
        help="Custom minimum video duration in MINUTES. Overrides --duration."
    )
    
    parser.add_argument(
        "-n", "--max-results", type=int, default=10, metavar='N', choices=range(1, 51),
        help="Number of results to return (1-50). Default: 10."
    )
    parser.add_argument(
        "-o", "--output", help="Output filename (.txt or .json). Prints to console if omitted."
    )
    args = parser.parse_args()
        
    youtube = get_youtube_service()
    if not youtube: return

    results = search_youtube(
        youtube, args.query, args.language, args.country,
        args.duration, args.max_results, args.min_duration
    )

    if not results:
        print("No results found matching the criteria.")
        return

    if args.output:
        save_results(results, args.output)
    else:
        print_results_to_console(results)


if __name__ == '__main__':
    main()
