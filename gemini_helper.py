import google.generativeai as genai
import config

def get_best_model():
    """
    Queries the Gemini API for available models and selects the best flash model.
    Falls back to a standard default if listing fails.
    """
    fallback_models = [
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-pro"
    ]
    try:
        available_models = []
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                # model names look like 'models/gemini-1.5-flash'
                model_name = m.name.split("/")[-1]
                available_models.append(model_name)
        
        # Check our preferred models in order of priority
        for model in fallback_models:
            if model in available_models:
                print(f"Selected Gemini model: {model}")
                return model
                
        if available_models:
            print(f"Selected first available model: {available_models[0]}")
            return available_models[0]
    except Exception as e:
        print(f"Warning: Could not list models ({e}). Defaulting to 'gemini-2.0-flash'.")
    
    return "gemini-2.0-flash"

def analyze_trends(videos):
    """
    Sends the list of outperforming videos to Gemini to identify key trends,
    summarize why they are performing well, and generate YouTube content ideas.
    """
    if not config.GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY is not set. Skipping AI analysis.")
        return None

    # Configure Gemini API
    genai.configure(api_key=config.GEMINI_API_KEY)
    
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

    try:
        model_name = get_best_model()
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None

