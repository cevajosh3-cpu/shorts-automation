import os
import requests
import re

def download_youtube_short(url, output_path):
    """
    Advanced Multi-Server Failover Engine.
    Bypasses platform firewalls by shifting between completely independent 
    distributed proxy networks automatically until a clean connection is established.
    """
    if os.path.exists(output_path):
        os.remove(output_path)
        
    # Isolate the clean 11-character video ID from the input URL path
    video_id_match = re.search(r'(?:shorts/|v=|be/|embed/)([a-zA-Z0-9_-]{11})', url)
    if not video_id_match:
        return False
    video_id = video_id_match.group(1)
    clean_watch_url = f"https://www.youtube.com/watch?v={video_id}"

    # Distributed infrastructure API pool (Rotates dynamically if firewalls trigger a 403 block)
    api_pool = [
        "https://cobalt.tools",
        "https://kwiatekniewidomek.pl",
        "https://cobalt.lol",
        "https://as93.net"
    ]
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Redmi A3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    }
    
    payload = {
        "url": clean_watch_url,
        "videoQuality": "720", # Optimization threshold for high-speed cloud rendering
        "audioFormat": "mp3",
        "filenameStyle": "basic"
    }

    # Execute the rotation queue loop
    for current_api in api_pool:
        try:
            response = requests.post(current_api, json=payload, headers=headers, timeout=8)
            if response.status_code == 200:
                data = response.json()
                stream_download_url = data.get("url")
                
                if stream_download_url:
                    # Stream the raw file blocks directly onto the server system
                    with requests.get(stream_download_url, stream=True, timeout=25) as r:
                        r.raise_for_status()
                        with open(output_path, "wb") as f:
                            for chunk in r.iter_content(chunk_size=16384):
                                if chunk:
                                    f.write(chunk)
                                    
                    # Verify asset container integrity
                    if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                        return True # Success achieved, break out of execution block
        except Exception:
            continue # Silent handoff: instantly drops broken server node and moves to next line
            
    return False # Final safeguard: returns false if entire pool fails, routing cleanly to file upload
