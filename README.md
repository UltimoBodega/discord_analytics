# Discord Analytics Bot

Discord-Analytics-Bot can be used to display who's been doing the most talking on your discord text channels. It ranks all users in descending order by how many characters they've typed since the inception of a particular discord channel.

## Dependencies

While sqllite is supported out of the box, we recommend installing MySQL and the required drivers:

```
sudo apt-get install libmysqlclient-dev
sudo apt-get install python3-dev
sudo apt-get install python3.7-dev
pip install mysqlclient
```

## Installation

1. Clone git repo to a dedicated server.
2. Install Python dependencies found in `requirements.txt`.
3. Input configuration parameters to `/discord_analytics/app_config/config_example.json` and rename to `config.json`
4. run `main.py`

## Commands

| Command  | Description                                                    |
| -------- | -------------------------------------------------------------- |
| `.stats` | Ranks users in descending order by total number of chars typed |

## Screenshots

![discord_ranking](.attachments/discord_ranking.png)
