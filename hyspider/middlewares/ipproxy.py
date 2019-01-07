from hyspider.utils import proxy


class ProxyMiddleware(object):

    def process_request(self, request, spider):
        ip_port = proxy.get_random_ip_port()
        request.meta['proxy'] = "http://" + ip_port