#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "=========================================================="
echo "      YouTube AI Video Tracker - VPS Setup Script         "
echo "=========================================================="

# 1. Update package list and install system dependencies
echo "[1/4] Installing system dependencies (Python 3 & Pip)..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv git

# 2. Create Python virtual environment
echo "[2/4] Setting up Python virtual environment..."
python3 -m venv venv
echo "Upgrading pip and installing requirements..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 3. Handle Environment Variables File
echo "[3/4] Checking configuration file..."
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "--------------------------------------------------------"
    echo "WARNING: Created a new .env file."
    echo "Please edit the .env file using a text editor (e.g., 'nano .env')"
    echo "and insert your API keys before running the script."
    echo "--------------------------------------------------------"
else
    echo ".env file already exists."
fi

# 4. Schedule Cron Job for 1:00 PM (13:00) local time
echo "[4/4] Configuring the scheduler..."

# Prompt the user to update server timezone to Asia/Kolkata so 1:00 PM matches their time
read -p "Would you like to set your VPS server timezone to Asia/Kolkata (IST) so cron matches your local time? [Y/n]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] || [[ -z $REPLY ]]; then
    echo "Setting server timezone to Asia/Kolkata..."
    sudo timedatectl set-timezone Asia/Kolkata
    echo "Timezone updated. Current server time is now: $(date)"
else
    echo "Skipping timezone change. Cron job will run at 1:00 PM Server Time."
fi

# Construct the cron command
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CRON_CMD="0 13 * * * cd $SCRIPT_DIR && ./venv/bin/python youtube_tracker.py >> $SCRIPT_DIR/tracker.log 2>&1"

# Add cron job (avoiding duplicates)
(crontab -l 2>/dev/null | grep -Fv "youtube_tracker.py" ; echo "$CRON_CMD") | crontab -

echo "=========================================================="
echo "Setup complete!"
echo "--------------------------------------------------------"
echo "1. Run 'nano .env' to fill in your API keys."
echo "2. Test the tracker manually using:"
echo "   ./venv/bin/python youtube_tracker.py"
echo "3. The script is scheduled to run daily at 1:00 PM."
echo "   You can check the run logs anytime in 'tracker.log'."
echo "=========================================================="
