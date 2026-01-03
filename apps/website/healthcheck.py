import urllib.request


try:
    urllib.request.urlopen('http://127.0.0.1:8000/')
except urllib.error.HTTPError:
    exit(1)
