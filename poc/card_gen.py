import numpy as np
from PIL import Image, ImageDraw
import io

def encode_char(c):
    c = c.lower()
    x = [False] * 12
    if c.isspace():
        return x
    elif c.isdigit():
        x[ord(c) - ord('0') + 2] = True
        return x
    elif c.isalpha():
        if ord(c) < ord('j'):
            x[0] = True
            x[ord(c) - ord('a') + 3] = True
        elif ord(c) <= ord('r'):
            x[1] = True
            x[ord(c) - ord('j') + 3] = True
        else:
            x[2] = True
            x[ord(c) - ord('s') + 4] = True
        pass
    else:
        if c == '.':
            x[0]  = True
            x[5]  = True
            x[10] = True
        elif c == '(':
            x[0]  = True
            x[7]  = True
            x[10] = True
        elif c == ')':
            x[1]  = True
            x[7]  = True
            x[10] = True
        elif c == '-':
            x[1]  = True
        elif c == '"':
            x[2]  = True
            x[9]  = True
            x[10] = True
        elif c == '=':
            x[2]  = True
            x[7]  = True
            x[10] = True
        elif c == ';':
            x[2]  = True
            x[6]  = True
            x[10] = True
        else:
            # TODO: maybe more characters
            raise ValueError("offending character: {}".format(c))
            assert(False)
    return x


def encode_str(s):
    res = list(map(encode_char, s))
    assert(len(res) <= 80)
    for _ in range(80 - len(res)):
        res.append([False] * 12)
    return res

def generate_punchcard(data):
    height = int((3 + 1/4) * 16 + 4) * 20
    width  = int((7 + 3/8) * 16 + 4) * 20

    top_left     = (30,30)
    top_right    = (width-30,30)
    bottom_left  = (30,height-30)
    bottom_right = (width-30,height-30)

    w = 15

    field_width  = top_right[0]   - top_left[0] - w/2
    field_height = bottom_left[1] - top_left[1] - w/2

    im = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(im)

    draw.line((top_left,top_right)       , (255,255,255), width=w)
    draw.line((bottom_left,bottom_right) , (255,255,255), width=w)
    draw.line((top_left,bottom_left)     , (255,255,255), width=w)
    draw.line((top_right,bottom_right)   , (255,255,255), width=w)

    card_height    = 3 + 1 / 4
    card_margin_v = 3 / 16

    distance_top    = top_left[1] + (card_margin_v / card_height) * field_height
    distance_bottom = distance_top + \
        field_height * (card_height - (2 * card_margin_v)) / card_height

    distance_vert = distance_bottom - distance_top
    fields_vert = np.linspace(distance_top,distance_bottom,13)

    card_width   = 7 + 3 / 8
    card_margin_h = 0.2235

    distance_left = top_left[0] + (card_margin_h / card_width) * field_width
    distance_right = distance_left + \
        field_width * (card_width - (2 * card_margin_h)) / card_width

    distance_horiz = distance_right - distance_left
    fields_horiz = np.linspace(distance_left,distance_right,81)

    delta = 8

    for i in range(80):
        for j in range(12):
            if data[i][j]:
                draw.rectangle(((int(fields_horiz[i]+delta),fields_vert[j]+delta),
                                (fields_horiz[i+1]-delta,fields_vert[j+1]-delta)),
                               (255,255,255))

    return im


def string_to_png_ios(s):
    streams = []
    for n, i in enumerate(s.split("\n")):
        l = encode_str(i)
        i = io.BytesIO()
        generate_punchcard(l).save(i, format='PNG')
        i.seek(0)
        streams.append(i)
    return streams

if __name__ == "__main__":
    import random

    import sys
    for n, i in enumerate(sys.stdin.readlines()):
        l = encode_str(i)
        generate_punchcard(l).save('{}.png'.format(n))
