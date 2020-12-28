# Discord Analytics Bot

Discord-Analytics-Bot can be used to display who's been doing the most talking on your discord text channels. It ranks all users in descending order by how many characters they've typed since the inception of a particular discord channel.

## Dependencies
Discord-Analytics-Bot currently depends on DiscordChatExporter. You can download the CLI [here](https://github.com/Tyrrrz/DiscordChatExporter).

Important: DiscordChatExporter requires .NET Core v3.1 runtime in order to run. To install the runtime, find a suitable download option below:

- Windows: [x64](https://dotnet.microsoft.com/download/dotnet-core/thank-you/runtime-desktop-3.1.0-windows-x64-installer) | [x86](https://dotnet.microsoft.com/download/dotnet-core/thank-you/runtime-desktop-3.1.0-windows-x86-installer)
- macOS: [x64](https://dotnet.microsoft.com/download/dotnet-core/thank-you/runtime-3.1.0-macos-x64-installer)
- Linux: [find your distribution here](https://docs.microsoft.com/en-us/dotnet/core/install/linux)

## Installation
1. Clone git repo to a dedicated server.
2. Install Python 3.5 or higher.
3. Install Python dependencies found in `requirements.txt`.
2. Input configuration parameters to `/discord_analytics/config_example.json` and rename to `config.json`
3. run `main.py`

## Commands

|Command|Description|
|--|--|
|`.stats`| Ranks users in descending order by total number of chars typed|


## Screenshots
![discord_ranking.png](\.attachments\discord_ranking.png)