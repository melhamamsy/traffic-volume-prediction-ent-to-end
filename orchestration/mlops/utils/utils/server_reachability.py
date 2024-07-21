import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def is_server_reachable(url, retries = 2, timeout = 5):
    session = requests.Session()
    retry = Retry(total=retries, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        response = session.get(url, timeout=timeout)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException:
        return False