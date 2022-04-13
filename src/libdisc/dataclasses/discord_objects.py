from typing import List, Union
from dataclasses import dataclass, field


@dataclass
class DiscordUser:
    name: str
    nickname: str
    discriminator: str


@dataclass
class StockItem:
    """Class for collecting stock info"""
    price: int
    price_day_low: int
    price_day_high: int
    symbol: str

    def __str__(self):
        return f'{self.symbol}: {self.price}'


@dataclass
class AlertItem:
    """Class for collecting stock info"""
    timestamp: int
    channel_id: int
    low: int
    high: int
    symbol: str
    note: str

    def __str__(self):
        return f'{self.symbol}: {self.low} {self.high}'


@dataclass
class StatItem:
    """Class for grouping stats"""
    timestamps: List[Union[int, float]] = field(default_factory=list)
    values: List[Union[int, float]] = field(default_factory=list)
