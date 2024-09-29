import os
import json
from youtube_search import YoutubeSearch
from youtube_transcript_api import YouTubeTranscriptApi
import re

def clean_transcript(text):
    cleaned_text = re.sub(r'\[.*?\]', '', text)
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text

def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)

def extract_transcripts(query, output_dir, num_videos=5, channel=''):
    if channel:
        search_query = f"{query} channel:{channel}"
    else:
        search_query = query
    
    results = YoutubeSearch(search_query, max_results=num_videos).to_dict()
    
    transcripts_saved = 0
    for video in results:
        video_id = video['id']
        title = video['title']
        
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            full_text = " ".join([entry['text'] for entry in transcript])
            cleaned_text = clean_transcript(full_text)
            
            if len(cleaned_text) > 50:
                safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                filename = f"{video_id}_{safe_title[:50]}.txt"
                file_path = os.path.join(output_dir, filename)
                os.makedirs(output_dir, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_text)
                transcripts_saved += 1
                update_index(output_dir, video_id, title)
            
            print(f"Processed video: {title}")
        
        except Exception as e:
            print(f"Error processing video {video_id}: {str(e)}")

    print(f"Extraction complete for '{query}'! Saved {transcripts_saved} new transcripts.")

def run_specific_search(query, output_dir, num_videos, channel=''):
    print(f"Running search for: {query}")
    extract_transcripts(query, output_dir, num_videos, channel)

def run_all_searches():
    config = load_config()
    for thing in config['things']:
        for search in thing['searches']:
            run_specific_search(search['query'], search['output_directory'], search['num_videos'], search.get('channel', ''))

def update_index(output_dir, video_id, title):
    index_path = os.path.join(output_dir, 'index.json')
    if os.path.exists(index_path):
        with open(index_path, 'r') as f:
            index = json.load(f)
    else:
        index = {}
    
    index[video_id] = title
    
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)

def update_global_index(directory):
    for root, dirs, files in os.walk(directory):
        if 'index.json' not in files:
            # Create an empty index file if it doesn't exist
            with open(os.path.join(root, 'index.json'), 'w') as f:
                json.dump({}, f)
        else:
            # Update existing index file
            index_path = os.path.join(root, 'index.json')
            with open(index_path, 'r') as f:
                index = json.load(f)
            
            # Check for any new transcript files and add them to the index
            for file in files:
                if file.endswith('.txt'):
                    video_id = file.split('_')[0]
                    if video_id not in index:
                        title = ' '.join(file.split('_')[1:]).rsplit('.', 1)[0]
                        index[video_id] = title
            
            # Save updated index
            with open(index_path, 'w') as f:
                json.dump(index, f, indent=2)

    print(f"Global index updated for {directory}")

if __name__ == "__main__":
    print("This script is meant to be imported and used by generic_transcript_extractor.py")
    print("Please run generic_transcript_extractor.py instead.")