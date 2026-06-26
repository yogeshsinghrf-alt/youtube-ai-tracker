import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# Email Settings
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")  # Resend's default free sandbox sender
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "yogeshsingh.rf@gmail.com")

# Timezone (UTC+5:30)
TIMEZONE = "Asia/Kolkata"

# Tracker Settings
OUTPERFORMANCE_MULTIPLIER = 1.5  # Video views must be >= 1.5x of the channel's median views
MIN_VIEWS = 5000                 # Filter out noise from very small channels/videos
LOOKBACK_HOURS = 48              # Search for videos published in the last 48 hours

# Target AI YouTube Channels by handle
TARGET_CHANNELS = [
    "@matthew_berman",
    "@WesRoth",
    "@AIExplained-official",
    "@TwoMinutePapers",
    "@Fireship",
    "@mwtuts",            # Matt Wolfe
    "@PromptEngineering",
    "@ykilcher",          # Yannic Kilcher
    "@ColdFusion",
    "@AllAboutAI",
    "@TrelisResearch",
    "@SamWitteveen"
]

# General Search Keywords to find trending videos outside target channels
SEARCH_KEYWORDS = [
    "AI news",
    "artificial intelligence",
    "ChatGPT",
    "Claude 3.5",
    "Gemini 1.5",
    "AI agents",
    "LLM developments"
]
