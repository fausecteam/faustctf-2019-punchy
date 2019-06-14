from ctf_gameserver.checker import BaseChecker
from ctf_gameserver.checker.constants import *
from jinja2 import Template
from base64 import b32encode, b64encode, b64decode
import urllib.request as req
import random
import string
import pickle
import os
from PIL import ImageDraw
from .api import Endpoint
from .crap_gen import gen_crap


with open(os.path.join(os.path.dirname(__file__),'template_cobol.cob')) as f:
    global template
    template = Template(f.read())


class PunchyChecker(BaseChecker):
    def flag_hash(self, tick):
        return str(tick)

    def deconstruct_flag(self, tick):
        return b32encode(self.get_flag(tick).encode('ascii')).decode('ascii')

    def place_flag(self):
        flag = self.deconstruct_flag(self.tick)
        endpoint = Endpoint('http://{}:7654'.format(self._ip))
        try:
            c = endpoint.fetch_cookie()
        except RuntimeError as e:
            self.logger.debug('place_flag: could not fetch cookie: {}'.format(e))
            return NOTWORKING

        self.logger.debug('place_flag: retrieved cookie: {}'.format(c))

        flag_representation = template.render(flg1=flag[0:32], flg2=flag[32:])
        self.logger.debug('place_flag: uploading flag as\n{}'.format(flag_representation))

        cookie_string = b64encode(pickle.dumps(c)).decode('ascii')
        self.logger.debug('place_flag: storing cookie for tick {} key {} keytype {} data {}'.format(self.tick, self.flag_hash(self.tick), type(self.flag_hash(self.tick)), cookie_string))
        flghash = self.flag_hash(self.tick)
        self.store_yaml(flghash, cookie_string)
        self.logger.debug('checking store_yaml {} -> {}'.format(flghash, self.retrieve_yaml(flghash)))

        try:
            n = endpoint.upload_string(flag_representation)
            endpoint.join(*range(0,n+1))
        except RuntimeError as e:
            self.logger.debug('place_flag: could upload or join flag: {}'.format(e))
            return NOTWORKING

        self.logger.debug('place_flag: running to verify...')
        try:
            ret = endpoint.run(0).strip()
        except RuntimeError:
            return NOTWORKING

        self.logger.debug('place_flag: placed flag returned {}'.format(ret))
        self.logger.debug('place_flag: wanted {} for tick {}'.format(self.deconstruct_flag(self.tick), self.tick))

        if ret == self.deconstruct_flag(self.tick):
            self.logger.debug('place_flag: success')
            return OK
        else:
            self.logger.debug('place_flag: not the expected flag')
            return NOTWORKING

    def check_flag(self, tick):
        endpoint = Endpoint('http://{}:7654'.format(self._ip))
        cookies_base64 = self.retrieve_yaml(self.flag_hash(tick))
        if cookies_base64 is None:
            self.logger.debug('check_flag: could not retrieve cookie for tick {} key {} keytype {} value {}'.format(tick, self.flag_hash(tick), type(self.flag_hash(tick)), cookies_base64))
            return NOTFOUND

        cookies = pickle.loads(b64decode(cookies_base64))


        self.logger.debug('check_flag: loading cookies {}'.format(cookies))
        if cookies is not None:
            endpoint.set_cookie(cookies)
            try:
                self.logger.debug('check_flag: data is {}'.format(endpoint.get_data()))
                ret = endpoint.run(0).rstrip('\n').strip()
                self.logger.debug('check_flag: got {}'.format(ret))
                self.logger.debug('check_flag: expected {} for tick {}'.format(self.deconstruct_flag(tick), tick))
                if ret == self.deconstruct_flag(tick):
                    self.logger.debug('check_flag: found flag {}'.format(ret))
                    return OK
                else:
                    self.logger.debug('check_flag: missing flag, got {}'.format(ret))
                    return NOTFOUND
            except RuntimeError as ex:
                self.logger.debug('check_flag: could not run flag ex {}'.format(ex))
                return NOTFOUND
        else:
            self.logger.debug('check_flag: no cookies')
            return NOTFOUND

    def check_service(self):
        try:
            endpoint = Endpoint('http://{}:7654'.format(self._ip))
            c = endpoint.fetch_cookie()
            self.logger.debug('check_service: fetched cookie {}'.format(c))
            test, expected = gen_crap()
            self.logger.debug('check_service: running tc {} with expected result {}'.format(test, expected))
            n = endpoint.upload_string(test)
            self.logger.debug('check_service: uploaded {} cards'.format(n))
            endpoint.join(*range(0,n+1))
            self.logger.debug('check_service: joined cards')
            ret = endpoint.run(0).rstrip('\n').strip()
            self.logger.debug('check_service: got result {}'.format(ret))
            if ret != expected:
                self.logger.debug('check_service: did not match')
                return NOTWORKING
            else:
                self.logger.debug('check_service: did match')
                return OK
        except RuntimeError as ex:
            self.logger.debug('check_service: problem running programm ex {}'.format(ex))
            return NOTWORKING
