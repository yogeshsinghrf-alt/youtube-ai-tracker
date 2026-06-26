import os
import json
import math
from datetime import datetime, timedelta, timezone
from googleapiclient.discovery import build
import config
import gemini_helper
import email_helper

# Cache file path for Channel IDs
CACHE_FILE = os.path.join(os.path.dirname(__file__), "channels_cache.json")

def get_youtube_client():
    """Initializes and returns the YouTube Data API client."""
    if not config.YOUTUBE_API_KEY:
        raise ValueError("YOUTUBE_API_KEY is not set in environment variables.")
    return build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)

def load_cached_channels():
    """Loads channel handle to ID mappings from local cache."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cached_channels(cache):
    """Saves channel handle to ID mappings to local cache."""
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=4)
    except Exception as e:
        print(f"Failed to write channel cache: {e}")

def resolve_handles(youtube, handles):
    """
    Resolves custom handles (e.g., @WesRoth) to channel IDs.
    Uses local cache to save quota.
    """
    cache = load_cached_channels()
    resolved = {}
    missing_handles = []

    # Check cache first
    for handle in handles:
        if handle in cache:
            resolved[handle] = cache[handle]
        else:
            missing_handles.append(handle)

    if missing_handles:
        print(f"Resolving {len(missing_handles)} new handles via YouTube API...")
        for handle in missing_handles:
            try:
                # Query YouTube channels list by handle
                response = youtube.channels().list(
                    part="id,snippet",
                    forHandle=handle
                ).execute()

                items = response.get("items", [])
                if items:
                    channel_id = items[0]["id"]
                    title = items[0]["snippet"]["title"]
                    resolved[handle] = {"id": channel_id, "title": title}
                    cache[handle] = resolved[handle]
                    print(f"Resolved {handle} -> {title} ({channel_id})")
                else:
                    print(f"Warning: Could not resolve handle {handle}")
            except Exception as e:
                print(f"Error resolving handle {handle}: {e}")
        
        save_cached_channels(cache)

    return resolved

def get_video_details(youtube, video_ids):
    """
    Fetches detailed statistics and snippets for a batch of video IDs.
    Quota cost: 1 unit.
    """
    if not video_ids:
        return []

    videos_details = []
    # YouTube allows fetching up to 50 videos in a single request
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i+50]
        try:
            response = youtube.videos().list(
                part="snippet,statistics",
                id=",".join(batch_ids)
            ).execute()
            videos_details.extend(response.get("items", []))
        except Exception as e:
            print(f"Error fetching video details: {e}")
            
    return videos_details

def calculate_median(lst):
    """Calculates median of a list of numbers."""
    if not lst:
        return 0
    n = len(lst)
    s = sorted(lst)
    return (s[n//2] + s[-(n//2+1)]) / 2.0

def process_videos(video_details, channel_title=None):
    """
    Processes video API details, calculates age, views, and identifies
    candidate videos for outperformance analysis.
    """
    processed = []
    now_utc = datetime.now(timezone.utc)

    for item in video_details:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        
        video_id = item["id"]
        title = snippet.get("title", "")
        published_at_str = snippet.get("publishedAt", "")
        description = snippet.get("description", "")
        ch_title = channel_title or snippet.get("channelTitle", "")
        ch_id = snippet.get("channelId", "")

        try:
            published_at = datetime.strptime(published_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            # Fallback if YouTube changes format
            published_at = now_utc

        age_hours = (now_utc - published_at).total_seconds() / 3600.0
        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))

        processed.append({
            "video_id": video_id,
            "title": title,
            "channel_title": ch_title,
            "channel_id": ch_id,
            "published_at": published_at_str,
            "age_hours": age_hours,
            "views": views,
            "likes": likes,
            "description": description
        })
    
    return processed

def get_outperforming_videos_for_channel(youtube, channel_id, channel_title):
    """
    Fetches the latest uploads of a channel, calculates their median views,
    and identifies any videos published within the lookback window that are outperforming.
    """
    # Channel uploads playlist is usually 'UU' + channel_id[2:]
    uploads_playlist_id = "UU" + channel_id[2:]
    
    try:
        response = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=15
        ).execute()
    except Exception as e:
        print(f"Error fetching uploads for {channel_title}: {e}")
        return []

    items = response.get("items", [])
    if not items:
        return []

    video_ids = [item["snippet"]["resourceId"]["videoId"] for item in items]
    video_details = get_video_details(youtube, video_ids)
    processed_videos = process_videos(video_details, channel_title)

    if not processed_videos:
        return []

    # Calculate median view count of all fetched videos to establish baseline
    views_list = [v["views"] for v in processed_videos]
    median_views = calculate_median(views_list)

    print(f"Channel: {channel_title} | Median views (last 15 uploads): {median_views:,.0f}")

    outperforming = []
    for v in processed_videos:
        # Check if the video is within our lookback window
        if v["age_hours"] <= config.LOOKBACK_HOURS:
            # Avoid dividing by zero or flagging extremely low-view videos
            if median_views > 0 and v["views"] >= config.MIN_VIEWS:
                ratio = v["views"] / median_views
                if ratio >= config.OUTPERFORMANCE_MULTIPLIER:
                    v["outperformance_ratio"] = ratio
                    v["median_views_baseline"] = median_views
                    outperforming.append(v)
                    print(f"  [OUTPERFORMER] {v['title'][:40]}...: {v['views']:,} views ({ratio:.2f}x median)")
            elif v["views"] >= config.MIN_VIEWS * 2 and median_views == 0:
                # If channel is new/no baseline, flag if it has high absolute views
                v["outperformance_ratio"] = 2.0
                v["median_views_baseline"] = 0
                outperforming.append(v)

    return outperforming

def get_outperforming_videos_from_search(youtube):
    """
    Searches YouTube for trending AI videos based on keywords, fetches
    statistics of their parent channels, and checks for outperformance.
    """
    print("\nRunning broader YouTube keyword search...")
    # Join keywords with OR to save quota by doing a single search
    query = " OR ".join(config.SEARCH_KEYWORDS)
    now_utc = datetime.now(timezone.utc)
    published_after = (now_utc - timedelta(hours=config.LOOKBACK_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        response = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            order="relevance",
            publishedAfter=published_after,
            maxResults=15
        ).execute()
    except Exception as e:
        print(f"Error during YouTube search: {e}")
        return []

    items = response.get("items", [])
    if not items:
        return []

    video_ids = [item["id"]["videoId"] for item in items if "videoId" in item["id"]]
    video_details = get_video_details(youtube, video_ids)
    processed_videos = process_videos(video_details)

    # To calculate if these are outperforming, we'll fetch the uploads playlist for each channel
    # involved. To save quota, we keep track of unique channel IDs.
    unique_channels = {}
    for v in processed_videos:
        unique_channels[v["channel_id"]] = v["channel_title"]

    print(f"Verifying {len(unique_channels)} channels from search results...")
    
    channel_medians = {}
    for ch_id, ch_title in unique_channels.items():
        # Get upload playlist
        uploads_playlist_id = "UU" + ch_id[2:]
        try:
            ch_resp = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=10
            ).execute()
            ch_items = ch_resp.get("items", [])
            if ch_items:
                ch_video_ids = [ci["snippet"]["resourceId"]["videoId"] for ci in ch_items]
                ch_details = get_video_details(youtube, ch_video_ids)
                ch_views = [int(cd.get("statistics", {}).get("viewCount", 0)) for cd in ch_details]
                channel_medians[ch_id] = calculate_median(ch_views)
            else:
                channel_medians[ch_id] = 0
        except Exception:
            channel_medians[ch_id] = 0

    outperforming = []
    for v in processed_videos:
        median = channel_medians.get(v["channel_id"], 0)
        if median > 0 and v["views"] >= config.MIN_VIEWS:
            ratio = v["views"] / median
            if ratio >= config.OUTPERFORMANCE_MULTIPLIER:
                v["outperformance_ratio"] = ratio
                v["median_views_baseline"] = median
                outperforming.append(v)
                print(f"  [SEARCH OUTPERFORMER] {v['title'][:40]}...: {v['views']:,} views ({ratio:.2f}x median)")
                
    return outperforming

def main():
    print(f"--- Starting AI YouTube Outperformance Tracker ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ---")
    
    try:
        youtube = get_youtube_client()
    except Exception as e:
        print(f"Initialization Error: {e}")
        return

    # 1. Track Curated Channels
    print("\nTracking Curated Channels...")
    resolved = resolve_handles(youtube, config.TARGET_CHANNELS)
    
    all_outperforming = []
    seen_video_ids = set()

    for handle, ch_info in resolved.items():
        channel_id = ch_info["id"]
        channel_title = ch_info["title"]
        
        videos = get_outperforming_videos_for_channel(youtube, channel_id, channel_title)
        for v in videos:
            if v["video_id"] not in seen_video_ids:
                all_outperforming.append(v)
                seen_video_ids.add(v["video_id"])

    # 2. Run Broader Search
    search_videos = get_outperforming_videos_from_search(youtube)
    for v in search_videos:
        if v["video_id"] not in seen_video_ids:
            all_outperforming.append(v)
            seen_video_ids.add(v["video_id"])

    # Sort videos by outperformance ratio descending
    all_outperforming.sort(key=lambda x: x["outperformance_ratio"], reverse=True)

    print(f"\nFound {len(all_outperforming)} outperforming videos total.")

    if not all_outperforming:
        print("No outperforming videos found today. Sending empty status email...")
        email_helper.send_report([], "No outperforming videos detected in the last 48 hours.")
        return

    # 3. Analyze with Gemini
    print("Calling Gemini to summarize trends and brainstorm content...")
    ai_analysis = gemini_helper.analyze_trends(all_outperforming)

    # 4. Email Report
    print("Sending email report...")
    email_helper.send_report(all_outperforming, ai_analysis)
    
    print("--- Tracker execution complete! ---")

if __name__ == "__main__":
    main()
