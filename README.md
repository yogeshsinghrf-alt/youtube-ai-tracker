# YouTube AI Video Outperformance Tracker & News Curator

A simple, automated Python application that runs on a Hostinger KVM1 Linux VPS. It tracks outperforming videos in the AI niche, analyzes key trends using the Gemini API, and sends a daily formatted email report (newsletter-style) to help you build your own AI YouTube channel.

---

## Step-by-Step Setup Guide

This guide is designed for **non-technical users**. Follow these steps to set up the tracker.

### Step 1: Push the Code to GitHub from your Local Computer

Since we have created all the files in your local workspace, we need to push them to GitHub so they can be easily downloaded on your VPS.

1. Open your browser and go to [GitHub](https://github.com/). Sign in or create a free account.
2. On the top right, click the **`+`** icon and select **New repository**.
3. Fill in the following details:
   - **Repository name**: `youtube-ai-tracker`
   - **Public/Private**: Select **Public**.
     > [!IMPORTANT]
     > Select **Public** because it makes downloading the code on your VPS 100x easier (no need to set up complex passwords or SSH keys on the VPS).
     > **Is it safe?** Yes! Your API keys will be stored in a file called `.env`, which is automatically ignored by Git (using the `.gitignore` file we created) and will **never** be uploaded to GitHub.
   - Do **NOT** check any boxes for adding a README, .gitignore, or license (we already created them).
4. Click **Create repository**.
5. Copy the HTTPS URL shown on the page (it will look like `https://github.com/YOUR_GITHUB_USERNAME/youtube-ai-tracker.git`).
6. On your local Windows computer:
   - Open **Command Prompt** (search for `cmd` in the Start Menu).
   - Navigate to the project directory by running:
     ```cmd
     cd c:\Users\Dell\Youtube-AI-Agent
     ```
   - Run the following commands one by one:
     ```cmd
     git init
     git add .
     git commit -m "Initial commit"
     git branch -M main
     git remote add origin https://github.com/YOUR_GITHUB_USERNAME/youtube-ai-tracker.git
     git push -u origin main
     ```
     *(Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username).*
     *If it asks you to sign in to GitHub, follow the prompt in the browser to authorize.*

---

### Step 2: Log into your Hostinger VPS

1. Open **Command Prompt** or **PowerShell** on your Windows computer.
2. Connect to your VPS via SSH by running:
   ```cmd
   ssh root@YOUR_VPS_IP_ADDRESS
   ```
   *(Replace `YOUR_VPS_IP_ADDRESS` with the IP address of your Hostinger VPS, which you can find in your Hostinger dashboard).*
3. When prompted, type your VPS password and press **Enter**. (Note: the password text will not appear on the screen as you type it for security. Just type it and press Enter).

---

### Step 3: Download and Set Up the Tracker on your VPS

Once you are logged into your VPS (you will see a prompt like `root@vps-...:~#`), run the following commands:

1. **Clone (Download) your code:**
   ```bash
   git clone https://github.com/YOUR_GITHUB_USERNAME/youtube-ai-tracker.git
   ```
   *(Replace with your GitHub username).*

2. **Navigate into the folder:**
   ```bash
   cd youtube-ai-tracker
   ```

3. **Run the setup script:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   - The script will install Python, install all required dependencies, and schedule the cron job.
   - When asked: *"Would you like to set your VPS server timezone to Asia/Kolkata (IST)..."*, type **`y`** and press **Enter**. This ensures the daily email triggers at exactly **1:00 PM local time**.

---

### Step 4: Enter your API Keys

Now, we need to add your API keys to the configuration:

1. Open the configuration file using the built-in text editor:
   ```bash
   nano .env
   ```
2. You will see a file like this:
   ```env
   YOUTUBE_API_KEY=
   GEMINI_API_KEY=
   RESEND_API_KEY=
   ...
   ```
3. Copy-paste your keys into the respective fields after the `=` sign:
   - **`YOUTUBE_API_KEY`**: Your YouTube API Key.
   - **`GEMINI_API_KEY`**: Your Gemini API Key.
   - **`RESEND_API_KEY`**: Your Resend API Key.
   - **`RECIPIENT_EMAIL`**: Already set to `yogeshsingh.rf@gmail.com`.
4. To save and exit the editor:
   - Press **`Ctrl + O`** (to write out/save).
   - Press **`Enter`** (to confirm the file name).
   - Press **`Ctrl + X`** (to exit the editor).

---

### Step 5: Test the Tracker

Test that everything works immediately by running:
```bash
./venv/bin/python youtube_tracker.py
```

Check your email inbox at **`yogeshsingh.rf@gmail.com`**. You should receive a beautifully styled HTML report listing the outperforming videos from the last 48 hours, along with a detailed AI trend summary and content ideas!

---

## How It Works

1. **Automation**: A Linux cron job is scheduled to run every day at 13:00 (1:00 PM) local time.
2. **Detection**: It fetches the last 15 videos of top AI channels and calculates their median views. If a video published in the last 48 hours has views **1.5x higher** than the median, it's flagged as outperforming.
3. **Keyword Search**: It searches YouTube for trending AI videos, calculates the average views of those channels, and filters outperforming ones.
4. **Insights**: The Gemini API summarizes why these videos are popular and suggests 3 ideas for your own channel.
5. **Newsletter**: The Resend API sends a customized newsletter directly to your inbox.
