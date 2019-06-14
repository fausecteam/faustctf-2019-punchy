from card_gen import *
import requests
from bs4 import BeautifulSoup

endpoint = "http://localhost:5000"

class Endpoint:
    def __init__(self, url):
        self.endpoint = url

    def fetch_cookie(self):
        r = requests.get('{}/list-data.htm'.format(self.endpoint))
        self.cookies = r.cookies
        if r.status_code != 200:
            raise RuntimeError('could not get cookie')
        return self.cookies

    def set_cookie(self, cookie):
        self.cookies = cookie

    def upload(self, f):
        r = requests.post('{}/upload-image.htm'.format(self.endpoint),
                          data={'bwthreshold': 200, 'encoding': '1401 IBM'},
                          files={'image': f},
                          cookies=self.cookies)
        if r.status_code != 200:
            raise RuntimeError('could not upload')

    def get_data(self):
        r = requests.get('{}/list-data.htm'.format(self.endpoint),
                         cookies=self.cookies)
        if r.status_code != 200:
            raise RuntimeError('could not get data')
        soup = BeautifulSoup(r.text, 'lxml')
        return list(map(lambda x: x.text, soup.find_all('pre')))

    def upload_string(self, s):
        cards = string_to_png_ios(s)
        for i in cards:
            self.upload(i)

        return len(cards)

    def join(self, *indices):
        r = requests.post('{}/list-data.htm'.format(self.endpoint),
                          data=dict([(str(i+1), 'on') for i in indices]),
                          cookies=self.cookies)
        if r.status_code != 200:
            raise RuntimeError('could not join data')

    def run(self, index):
        r = requests.post('{}/run-help.htm'.format(self.endpoint),
                          data={'id': index},
                          cookies=self.cookies)
        if r.status_code != 200:
            raise RuntimeError('could not run')

        return r.text

    def find_index():
        pass

if __name__ == '__main__':
    e = Endpoint(endpoint)
    e.fetch_cookie()
    e.upload_string(open('../../foo.cob').read())
    e.join(*range(0,15))
    print(e.get_data()[0])
    print(e.run(0))
