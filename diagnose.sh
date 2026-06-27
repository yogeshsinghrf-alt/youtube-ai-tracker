#!/usr/bin/env bash

echo "=========================================================="
echo "      YouTube AI Video Tracker - VPS Diagnostic Tool      "
echo "=========================================================="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# 1. Check current timezone and time
echo "--- 1. Time & Timezone Check ---"
echo "Current VPS Time: $(date)"
echo "Current Timezone: $(cat /etc/timezone 2>/dev/null || timedatectl | grep 'Time zone' | awk '{print $3}')"
echo ""

# 2. Check .env file
echo "--- 2. Environment Configuration Check ---"
if [ -f .env ]; then
    echo "SUCCESS: .env file exists."
    # Check if keys are filled (non-empty)
    yt_key=$(grep -E "^YOUTUBE_API_KEY=" .env | cut -d'=' -f2)
    groq_key=$(grep -E "^GROQ_API_KEY=" .env | cut -d'=' -f2)
    resend_key=$(grep -E "^RESEND_API_KEY=" .env | cut -d'=' -f2)
    recipient=$(grep -E "^RECIPIENT_EMAIL=" .env | cut -d'=' -f2)

    if [ -z "$yt_key" ]; then
        echo "WARNING: YOUTUBE_API_KEY is empty in .env!"
    else
        echo "YouTube Key: Configured (ends with ...${yt_key: -4})"
    fi

    if [ -z "$groq_key" ]; then
        echo "WARNING: GROQ_API_KEY is empty in .env!"
    else
        echo "Groq Key: Configured (ends with ...${groq_key: -4})"
    fi

    if [ -z "$resend_key" ]; then
        echo "WARNING: RESEND_API_KEY is empty in .env!"
    else
        echo "Resend Key: Configured (ends with ...${resend_key: -4})"
    fi

    if [ -z "$recipient" ]; then
        echo "WARNING: RECIPIENT_EMAIL is empty in .env!"
    else
        echo "Recipient Email: $recipient"
    fi
else
    echo "ERROR: .env file does not exist! Run cp .env.example .env and fill in your keys."
fi
echo ""

# 3. Check virtual environment
echo "--- 3. Python Virtual Environment Check ---"
if [ -d venv ]; then
    echo "SUCCESS: venv folder exists."
    if [ -f venv/bin/python ]; then
        echo "SUCCESS: Python executable found in venv."
        # Check installed packages
        pip_check=$(./venv/bin/pip freeze)
        if echo "$pip_check" | grep -q "google-api-python-client"; then
            echo "SUCCESS: google-api-python-client is installed."
        else
            echo "ERROR: google-api-python-client is NOT installed in venv! Run: ./venv/bin/pip install -r requirements.txt"
        fi
    else
        echo "ERROR: Python executable NOT found in venv/bin/!"
    fi
else
    echo "ERROR: venv directory does not exist! Run setup.sh to create it."
fi
echo ""

# 4. Check Cron Scheduler
echo "--- 4. Cron Job Schedule Check ---"
cron_list=$(crontab -l 2>/dev/null)
if echo "$cron_list" | grep -q "youtube_tracker.py"; then
    echo "SUCCESS: Cron job is scheduled:"
    echo "$cron_list" | grep "youtube_tracker.py"
else
    echo "WARNING: No cron job scheduled for youtube_tracker.py! Run setup.sh or add it manually."
fi
echo ""

# 5. Check Log Files
echo "--- 5. Tracker Log Output Check (Last 15 lines) ---"
if [ -f tracker.log ]; then
    echo "Showing last 15 lines of tracker.log:"
    tail -n 15 tracker.log
else
    echo "No tracker.log file found yet. (This is normal if the script has never run)."
fi
echo ""

# 6. Manual Test Run Prompt
echo "--- 6. Manual Test Run ---"
read -p "Would you like to run the script manually right now to test it? [y/N]: " run_now
if [[ "$run_now" =~ ^[Yy]$ ]]; then
    echo "Running tracker manually..."
    ./venv/bin/python youtube_tracker.py
else
    echo "Skipped manual run."
fi
echo "=========================================================="
