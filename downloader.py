import os
import requests

def download_youtube_short(url, output_path):
    """
    Production-tier bypass downloader. 
    Wipes out 403 blocks by routing requests through a sanitized public format extractor api
    instead of calling flagged data-center terminal commands.
    """
    if os.path.exists(output_path):
        os.remove(output_path)
        
    try:
        # Extract unique 11-character video ID from any YouTube URL structure safely
        video_id = ""
        if "shorts/" in url:
            video_id = url.split("shorts/")[1].split("?")[0].split("&")[0]
        elif "v=" in url:
            video_id = url.split("v=")[1].split("?")[0].split("&")[0]
        else:
            video_id = url.split("/")[-1].split("?")[0].split("&")[0]
            
        if not video_id or len(video_id) != 11:
            return False

        # Accessing an open distributed stream conversion endpoint to fetch a clean, direct mp4 data pipe
        api_endpoint = f"https://cobalt.tools"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        payload = {
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "videoQuality": "720", # Forces standard 720p HD grid for rapid, reliable rendering speeds
            "audioFormat": "mp3"
        }
        
        response = requests.post(api_endpoint, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            download_url = data.get("url")
            
            if download_url:
                # Streams the raw video binary data file straight onto the cloud server filesystem chunk-by-chunk
                with requests.get(download_url, stream=True, timeout=30) as r:
                    r.raise_for_stdio = True
                    with open(output_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    return True
        return False
        
    except Exception:
        # Emergency local safety fallback rule: returns false so frontend triggers localized upload route seamlessly
        return False
