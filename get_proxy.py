# %%
from requests.exceptions import ProxyError, SSLError, ConnectTimeout
import requests
from scrapy import Selector

proxy_url = "https://free-proxy-list.net/"

resp = requests.get(proxy_url)
sel = Selector(resp)
tr_list = sel.xpath('//*[@id="list"]/div/div[2]/div/table/tbody/tr')

proxy_server_list = []

for tr in tr_list:
    ip = tr.xpath("td[1]/text()").extract_first()
    port = tr.xpath("td[2]/text()").extract_first()
    https = tr.xpath("td[7]/text()").extract_first()

    if https == "yes":
        server = f"{ip}:{port}"
        proxy_server_list.append(server)

# %%
proxy_server_list
# %%
