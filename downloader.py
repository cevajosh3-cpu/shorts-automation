import os
import requests
import re

def download_youtube_short(url, output_path):
    """
    Upgraded multi-platform media proxy scraper. Pulls from optimized 
    conversion links to sidestep data-center 403 blocks.
    """
    if os.path.exists(output_path):
        os.remove(output_path)
        
    try:
        # Detect clear video string signatures
        video_id_match = re.search(r'(?:shorts/|v=|be/|embed/)([a-zA-Z0-9_-]{11})', url)
        if not video_id_match:
            return False
        video_id = video_id_match.group(1)
        
        # Pull direct high-speed streams from open-source conversion layers
        api_urls = [
            f"https://cobalt.tools",
            f"https://as93.net"
        ]
        
        payload = {
            "url": f"https://youtube.com{video_id}",
            "videoQuality": "720"
        }
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        
        for endpoint in api_urls:
            try:
                response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
                if response.status_code == 200:
                    media_url = response.json().get("url")
                    if media_url:
                        with requests.get(media_url, stream=True, timeout=30) as r:
                            r.raise_for_status()
                            with open(output_path, "wb") as f:
                                for chunk in r.iter_content(chunk_size=16384):
                                    if chunk: f.write(chunk)
                        if os.path.exists(output_path) and os.path.getsize(output_path) > 5000:
                            return True
            except Exception:
                continue
        return False
    except Exception:
        return False
