import os
import pandas as pd
from googleapiclient.discovery import build

# Set up your API key (replace with your own key)
API_KEY = 'AIzaSyD2ogIU51VeXqLdWdww5UwwqziJuLEGHFs'

# Build the YouTube service
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_channel_videos(channel_id, max_videos=500):
    video_ids = []
    next_page_token = None
    while len(video_ids) < max_videos:
        request = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=50,  # Maximum allowed per request
            pageToken=next_page_token,
            type="video"
        )
        response = request.execute()

        for item in response['items']:
            video_ids.append(item['id']['videoId'])

        # Get the next page token
        next_page_token = response.get('nextPageToken')

        # Break the loop if there are no more results
        if next_page_token is None:
            break

    return video_ids[:max_videos]

# Example: Fetch up to 500 videos
channel_id = 'UCCW-mJ_bpGDd5kaUI4rpFgg'
video_ids = get_channel_videos(channel_id, max_videos=500)


def get_video_stats(video_ids):
    stats = []
    
    # YouTube API allows a maximum of 50 video IDs per request
    batch_size = 50
    
    # Loop through the video_ids in batches of 50
    for i in range(0, len(video_ids), batch_size):
        batch_ids = video_ids[i:i + batch_size]
        
        # Make the request for each batch of video IDs
        request = youtube.videos().list(
            part="statistics,snippet",
            id=','.join(batch_ids)  # Join IDs with commas
        )
        response = request.execute()
        
        # Extract statistics for each video
        for item in response['items']:
            video_info = {
                'video_id': item['id'],
                'title': item['snippet']['title'],
                'publishedAt': item['snippet']['publishedAt'],
                'views': int(item['statistics'].get('viewCount', 0)),
                'likes': int(item['statistics'].get('likeCount', 0)),
                'comments': int(item['statistics'].get('commentCount', 0))
            }
            stats.append(video_info)
    
    return stats


# Get video stats
video_stats = get_video_stats(video_ids)

# Convert to a DataFrame for easier analysis
df = pd.DataFrame(video_stats)
print(df)

df.to_csv('youtube_video_stats.csv', index=False)
