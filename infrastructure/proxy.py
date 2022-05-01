from infrastructure.api import Api
from module import helper
from constant import constant
from os import path
from uuid import uuid4


class Proxy:
    def __init__(self, **kwargs):
        for name, value in kwargs.items():
            setattr(self, name, value)
        self.string = self.to_string()

    def __repr__(self):
        return self.string

    def server(self):
        return f"{self.scheme}://{self.hostname}:{self.port}"

    def to_string(self):
        if hasattr(self, "username"):
            return f"{self.scheme}://{self.username}:{self.password}@{self.hostname}:{self.port}"
        else:
            return self.server()

    def plugin_file(self):
        file_name = path.join('resources', 'proxy', 'extensions', str(uuid4()) + '.zip')
        plugin_file = helper.create_proxyauth_extension(proxy_host=self.hostname, proxy_username=self.username,
                                                        proxy_password=self.password, proxy_port=self.port,
                                                        plugin_path=None)
        return plugin_file

    def get_ip(self):
        ip = dict()
        api = Api()
        api.proxies = {"http": self.string, "https": self.string}
        for ipv, address in constant.api_check_ip_address.items():
            try:
                response = api.get(url=address, timeout=constant.API_TIMEOUT)
            except:
                api.close()
                ip[ipv] = ""
            else:
                ip[ipv] = response.text
        api.close()
        return ip
