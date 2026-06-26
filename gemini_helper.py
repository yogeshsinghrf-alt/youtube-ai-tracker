import requests
import config

def get_best_groq_model():
    """
    Queries the Groq API for available models and selects the best active model.
    Falls back to a standard default if listing fails.
    """
    fallback_models = [
        "llama-3.3-70b-versatile",
        "llama-3.1-70b-versatile",
        "llama3-70b-8192",
        "mixtral-8x7b-32768",
        "llama-3.2-3b-preview",
        "gemma2-9b-it"
    ]
    headers = {
        "Authorization": f"Bearer {config.GROQ_API_KEY}"
    }
    try:
        response = requests.get("https://api.groq.com/openai/v1/models", headers=headers)
        if response.status_code == 200:
            models_data = response.json().get("data", [])
            available_models = [m["id"] for m in models_data]
            
            # Find the best matching model from our fallback list
            for model in fallback_models:
                if model in available_models:
                    print(f"Selected Groq model: {model}")
                    return model
            
            # If none of our fallbacks match, return the first one available
            if available_models:
                print(f"Selected first available Groq model: {available_models[0]}")
                return available_models[0]
    except Exception as e:
        print(f"Warning: Could not list Groq models ({e}). Defaulting to 'llama-3.3-70b-versatile'.")
    
    return "llama-3.3-70b-versatile"

def analyze_trends(videos):
    """
    Sends the list of outperforming videos to Groq to identify key trends,
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

    # Dynamically resolve active model
    model_name = get_best_groq_model()

    payload = {
        "model": model_name,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7
    }

    try:
        print(f"Connecting to Groq API (using {model_name})...")
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
