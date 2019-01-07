from hyspider.items.base import CityBase
from hyspider.items.channel import ChannelTB, ChannelMT, ChannelLM


class CityTB(CityBase, ChannelTB):
    pass


class CityMT(CityBase, ChannelMT):
    pass


class CityLM(CityBase, ChannelLM):
    pass
