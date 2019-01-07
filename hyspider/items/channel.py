from hyspider.items.base import ChannelBase


class ChannelTB(ChannelBase):
    @classmethod
    def get_channel_name(cls):
        return 'tb'


class ChannelMT(ChannelBase):
    @classmethod
    def get_channel_name(cls):
        return 'mt'


class ChannelLM(ChannelBase):
    @classmethod
    def get_channel_name(cls):
        return 'lm'


class ChannelDB(ChannelBase):
    @classmethod
    def get_channel_name(cls):
        return 'db'