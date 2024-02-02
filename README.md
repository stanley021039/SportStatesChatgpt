# SportStatesChatgpt

## Introduction

SportStatesChatgpt is a website designed to provide quick access to daily NBA game scores and season records. Additionally, it features ChatGPT for rapid Q&A sessions.

## Installation

To set up the project, follow these steps:

1. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

2. Set up Apache server.

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
