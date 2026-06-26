import google.generativeai as genai
import config

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
        # Use gemini-1.5-flash for fast and reliable performance
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None
