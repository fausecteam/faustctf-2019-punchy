import cv2
import matplotlib.pyplot as plt
import numpy as np

from io import BytesIO

import matplotlib
matplotlib.use('Agg')

def preprocess_image(data, thres, inv):
    img  = cv2.imdecode(np.asarray(bytearray(data.read()), dtype=np.uint8), -1)
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(grey, (7,7))
    bw   = cv2.threshold(blur, thres, 255, cv2.THRESH_BINARY)[1]
    if inv:
        bw = 255 - bw
    return bw


def export_image(imgbuffer):
    return cv2.imencode('.png', imgbuffer)[1].tobytes()


def find_edges(bw):
    edges = cv2.Canny(bw, 100, 200)
    lines = cv2.HoughLines(edges, 1, np.pi/180, 200)

    lines_vert = []
    lines_horiz = []
    for line in lines:
        theta = line[0][1]
        if abs(theta - 1.5708) < 0.001:
            lines_horiz.append(line[0][0])
        elif abs(theta) < 0.001:
            lines_vert.append(line[0][0])

    if len(lines_vert) > 200 or len(lines_horiz) > 200:
        raise RuntimeError("Too many lines detected")
    if len(lines_vert) < 2 or len(lines_horiz) < 2:
        raise RuntimeError("Not enough lines detected")

    lines_vert.sort()
    lines_horiz.sort()

    def collate_lines(lines, dir):
        while True:
            lines_new = list()
            change = False
            i = 0
            while i < len(lines) - 1:
                if ((lines[i+1] - lines[i]) / bw.shape[dir]) < .001:
                    new_line = (lines[i] + lines[i+1]) / 2.0
                    lines_new.append(new_line)
                    i += 2
                    change = True
                else:
                    lines_new.append(lines[i])
                    i += 1
            if not change:
                break
            else:
              lines = lines_new
        return lines

    lines_vert  = collate_lines(lines_vert , 0)
    lines_horiz = collate_lines(lines_horiz, 1)

    if len(lines_vert) < 2 or len(lines_horiz) < 2:
        raise RuntimeError("Too few or too many edges detected")
    else:
        lines_vert = [lines_vert[0], lines_vert[-1]]
        lines_horiz = [lines_horiz[0], lines_horiz[-1]]
        return lines_vert, lines_horiz

def export_edges(bw, lines_vert, lines_horiz):
    ax = plt.imshow(bw)
    box = ax.axes
    box.vlines(lines_vert,  0, bw.shape[0])
    box.hlines(lines_horiz, 0, bw.shape[1])

    buf = BytesIO()
    plt.savefig(buf, format='png')
    return buf.getbuffer()


def find_segments(lines_vert, lines_horiz):
    height = lines_horiz[1] - lines_horiz[0]
    width  = lines_vert [1] - lines_vert [0]

    margin_top    = (3 / 16) / (3 + 1 / 4)
    margin_bottom = margin_top

    margin_left   = 0.2235 / (7 + 3 / 8)
    margin_right  = margin_left

    borders_horiz = np.linspace(lines_horiz[0] + margin_top  * height, lines_horiz[1] - margin_bottom * height, num=13)
    borders_vert  = np.linspace(lines_vert [0] + margin_left * width,  lines_vert [1] - margin_right  * width,  num=81)

    return borders_vert, borders_horiz


def export_segments(bw, borders_vert, borders_horiz):
    plt.figure()
    ax = plt.imshow(bw)
    box = ax.axes
    box.hlines(borders_horiz, 0, bw.shape[1])
    box.vlines(borders_vert,  0, bw.shape[0])

    buf = BytesIO()
    plt.savefig(buf, format='png')
    return buf.getbuffer()


def extract_cells(bw, borders_vert, borders_horiz):
    cells = np.zeros((12, 80))
    for x in range(80):
        for y in range(12):
            cells[y, x] = bw[int(borders_horiz[y]):int(borders_horiz[y+1]),
                             int(borders_vert [x]):int(borders_vert [x+1])].mean() > 0

    return cells


def export_cells(cells):
    plt.figure()
    plt.imshow(cells)

    buf = BytesIO()
    plt.savefig(buf, format='png')
    return buf.getbuffer()


def read_cells(cells):
    values = []
    # for i in cells.transpose():
    #     value = i[0] * 2**12 + i[1] * 2**11
    #     for x in range(3, 12):
    #         value += i[x] * 2**(x-2)
    #     values.append(int(value))
    for i in cells.transpose():
        value = 0
        for x in range(0, 12):
            value += i[x] * (2**x)
        values.append(int(value))

    return values
