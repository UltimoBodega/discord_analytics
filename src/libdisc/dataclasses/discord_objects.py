from dataclasses import dataclass


@dataclass
class DiscordUser:
    name: str
    nickname: str
    discriminator: str
