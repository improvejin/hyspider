from hyspider.items.base import CinemaBase
from hyspider.items.channel import ChannelTB, ChannelMT, ChannelLM


class CinemaTB(CinemaBase, ChannelTB):
    pass


class CinemaMT(CinemaBase, ChannelMT):
    pass


class CinemaLM(CinemaBase, ChannelLM):
    pass