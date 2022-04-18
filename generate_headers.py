import requests
from bs4 import BeautifulSoup


proxy, user_agents = "http://user-kocstaging:EV!L&D!hJ6Ugy5Rs@vn.smartproxy.com:46000", list()
with open("resources/headers/whatismybrowser-user-agent-database.txt", 'rt') as fp:
    for line in fp:
        user_agents.append(line.strip())


headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "vi-VI, en-US",
    "Cache-Control": "no-cache",
    "User-Agent": "PostmanRuntime/7.29.0",
    "Connection": "close"
}



for user_agent in user_agents:
    session = requests.Session()
    session.proxies = {'http': proxy, 'https': proxy}
    session.headers = headers
    # session.headers['User-Agent'] = user_agent
    print(user_agent)
    resp = session.get("https://www.facebook.com/lamkhaiingan")
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, 'html.parser')
        for meta in soup.find_all("meta"):
            print(meta.get("content"))
    else:
        print(resp.status_code, resp.headers)
    session.close()