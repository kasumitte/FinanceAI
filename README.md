# <img src="assets/readme_icon.png" width="29" style="vertical-align:middle;"> Financial AI Tracker
AI built for tracking your transactions

## How it works
**Give a file which must contain your transactions, use commands from list to interact with your transactions.**
Use 'import' command to categorize all of your transactions with AI.
'graph' builds graphics for your transactions. (there are might be a several issues with importing csv, just keep it in mind)
> You can change configuration in config.py if its needed

## Setup
**Requirements:** Python 3.13, uv
> .env.example has template for your .env

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install dependencies
uv sync

# 3. Initialize database
docker-compose up -d db

# 4. Run commands
uv run python setup.py {your command from list}
```
