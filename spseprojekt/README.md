# SkolaOnline Discord Bot

Template for a Discord bot that reads configuration from `.env` and keeps website fetching/parsing code separate from Discord commands.

## Setup

1. Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Fill in `.env`:

```dotenv
DISCORD_BOT_TOKEN=your-token
DISCORD_GUILD_ID=optional-test-server-id
SKOLAONLINE_USERNAME=your-login
SKOLAONLINE_PASSWORD=your-password
```

`DISCORD_GUILD_ID` is optional. If set, slash commands sync only to that Discord server, which is faster for development. If empty, commands sync globally and can take longer to appear.

4. Run the bot:

```bash
python run.py
```

## Project Structure

```text
bot/
  config.py              Loads .env configuration
  discord_bot.py         Discord client and slash commands
  skolaonline/
    client.py            HTTP session and request helpers
    parser.py            HTML parsing helpers
run.py                   App entrypoint
```

## Next Steps

- Update `bot/skolaonline/client.py` with the real SkolaOnline login flow.
- Update `bot/skolaonline/parser.py` with selectors for the exact page data you want.
- Add new slash commands in `bot/discord_bot.py`.

## Škola OnLine API Test

The integration test uses the unofficial API documented at:

```text
https://libre-skolaonline.github.io/API-docs/
```

Run the test with:

```bash
venv/bin/python -m pytest tests/test_skolaonline_api.py -q
```

The test requires valid values in `.env`:

```dotenv
SKOLAONLINE_BASE_URL=https://aplikace.skolaonline.cz/solapi/api
SKOLAONLINE_USERNAME=your-login
SKOLAONLINE_PASSWORD=your-password
```

By default it only fetches the current user profile. To also fetch marks, run:

```bash
SKOLAONLINE_FETCH_MARKS=1 venv/bin/python -m pytest tests/test_skolaonline_api.py -q
```

Do not commit real credentials. This template includes `.env` for local editing, but `.gitignore` excludes it from git.
