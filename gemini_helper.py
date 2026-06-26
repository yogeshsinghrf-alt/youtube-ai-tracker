import requests
import config

def analyze_trends(videos):
    """
    Sends the list of outperforming videos to Groq (Llama 3) to identify key trends,
    summarize why they are performing well, and generate YouTube content ideas.
    """
    if not config.GROQ_API_KEY:
        print("Warning: GROQ_API_KEY is not set. Skipping AI analysis.")
        return None

    # Format the video data for the prompt
    video_list_str = ""
    for idx, video in enumerate(videos, 1):
        video_list_str += f"""
{idx}. Title: {video['title']}
   Channel: {video['channel_title']}
   Views: {video['views']:,}
   Outperformance Ratio: {video['outperformance_ratio']:.2f}x
   Published: {video['published_at']}
   Link: https://www.youtube.com/watch?v={video['video_id']}
   Description: {video['description'][:300]}...
--------------------------------------------------"""

    prompt = f"""
You are an expert YouTube growth strategist and AI niche content curator.
Below is a list of recent YouTube videos in the AI niche that are currently OUTPERFORMING (getting significantly more views than the channel's average).

{video_list_str}

Please analyze this data and generate a professional, highly readable report with the following sections in Clean Markdown:

1. **Executive Trend Summary**: Identify the 3 most significant trends/topics driving views right now (e.g., specific tool updates, major industry news, new open-source models).
2. **Video-by-Video Analysis**: Briefly explain *why* each video is performing so well (e.g., is it a tutorial, breaking news, a comparison, or addressing a specific community pain point?). Keep each explanation to 1-2 clear sentences.
3. **Content Strategy Suggestions**: Propose 3 specific, clickable video title ideas with descriptions that the user should create for their own YouTube channel to ride these current trends. Explain what angle they should take.

Format the output clearly and beautifully using markdown so it can be directly embedded into an email. Avoid using generic boilerplate text.
"""

    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    # Llama 3 8B is extremely fast, accurate, and completely free on Groq's tier
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    try:
        print("Connecting to Groq API (using llama3-8b-8192)...")
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers
        )
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"Error calling Groq API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Exception calling Groq API: {e}")
        return None
