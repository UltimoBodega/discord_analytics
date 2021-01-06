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

## License

MIT License

Copyright (c) 2020 Ultimo Bodega

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
