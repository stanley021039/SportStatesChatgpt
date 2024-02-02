# SportStatesChatgpt

## Introduction

SportStatesChatgpt is a website designed to provide quick access to daily NBA game scores and season records. Additionally, it features ChatGPT for rapid Q&A sessions.

## Demo Page

Visit the [demo page](https://www.hd0619-info.site/SportChatGPT/NBA/Standings) to explore SportStatesChatgpt and view NBA standings.

## Installation

To set up the project, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/stanley021039/SportStatesChatgpt.git
    ```

2. **Establish Virtual Environment:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. **Setup Apache Environment:**
    Add the following configuration to your Apache virtual host file:
    ```apache
    <Location "/SportChatGPT">
        RequestHeader set X-Script-Name "/SportChatGPT"
        ProxyPass "http://127.0.0.1:8000"
        ProxyPassReverse "http://127.0.0.1:8000"
    </Location>
    ```
    This configuration will proxy requests to the ImageCrawler application running on `http://127.0.0.1:8000`. Adjust the `Location` directive and proxy URLs as needed based on your server setup.
    Make sure to reload or restart Apache for the changes to take effect:
    ```bash
    sudo service apache2 reload
    ```

3. Run the application using Gunicorn:

    ```bash
    gunicorn -c gunicorn_config.py SportStatesChatgpt:app --log-level debug --daemon
    ```

## Features

### NBA Standings

- **Endpoint:** `/NBA/Standings`
- **Description:** Displays the season standings for the NBA.
- **Resource:** `StandingsPage`

### NBA Standings Data

- **Endpoint:** `/api/NBA/Standings_season_data`
- **Description:** Provides the season standings data for the NBA.
- **Resource:** `StandingsData`

### Today's NBA Scoreboard

- **Endpoint:** `/NBA/scoreboard`
- **Description:** Shows the scoreboard for NBA games on the current day.
- **Resource:** `TodayScoreboardPage`

### Today's NBA Scoreboard Data

- **Endpoint:** `/api/NBA/scoreboard_data`
- **Description:** Retrieves the scoreboard data for NBA games on the specified date.
- **Resource:** `TodayScoreboardData`
