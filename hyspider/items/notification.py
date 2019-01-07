from hyspider.items.base import NotificationBase
from hyspider.items.channel import ChannelTB, ChannelMT, ChannelLM


class NotificationTB(NotificationBase, ChannelTB):
    pass


class NotificationMT(NotificationBase, ChannelMT):
    pass


class NotificationLM(NotificationBase, ChannelLM):
    pass