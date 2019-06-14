from flask import Flask, session, redirect, render_template, request
from flask_session import Session

from jinja2 import Template

from base64 import b64encode

from parser import preprocess_image, export_image, find_edges, export_edges, \
    find_segments, export_segments, extract_cells, export_cells, read_cells

from libs import get_encodings, decode_card, join_commands, check_help, run_help

import os
import os.path

app = Flask(__name__)
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = os.path.join(os.path.dirname(__file__), 'data')
app.config.from_object(__name__)
Session(app)

global counter
counter = 0

@app.route('/')
def main():
    global counter
    counter += 1
    return redirect('/static/site.htm', code=302)


@app.route('/counter.htm')
def get_count():
    global counter
    counter += 1
    return render_template('counter.htm', n=counter)


@app.route('/upload.htm')
def show_upload():
    global counter
    counter += 1
    return render_template('upload.htm', encoding=get_encodings())


@app.route('/list-data.htm')
def list_data():
    global counter
    counter += 1

    try:
        data = session['data']
    except KeyError:
        data = []


    help_description = None
    help_map = []
    for id, i in enumerate(data):
        h = check_help(i)
        if h is not None:
            help_description, help_html = h.split('---')
            help_map.append(Template(help_html).render(id=id))
        else:
            help_map.append(None)

    return render_template('list-data.htm', data=list(zip(data, help_map)), help=help_description)


def upload_parse():
    try:
        img = request.files['image']
        bwthreshold = int(request.form['bwthreshold'])
        invert = 'invert' in request.form
        return preprocess_image(img, bwthreshold, invert)
    except KeyError:
        raise RuntimeError('Your request does not conform: {},  {}'.format(request.form, request.files))
    except RuntimeError as err:
        raise RuntimeError('Could not preprocess request: {}'.format(err))


@app.route('/preview-segments.htm', methods=['POST'])
def preview_segemnts():
    global counter
    counter += 1

    try:
        img = upload_parse()
        img = export_segments(img, *find_segments(*find_edges(img)))
    except RuntimeError as err:
        return 'Could not export segments: {}'.format(err)

    return render_template('preview.htm', preview=b64encode(img).decode('utf-8'))


@app.route('/preview-edges.htm', methods=['POST'])
def preview_edges():
    global counter
    counter += 1

    try:
        img = upload_parse()
        img = export_edges(img, *find_edges(img))
    except RuntimeError as err:
        return 'Could not export edges: {}'.format(err)

    return render_template('preview.htm', preview=b64encode(img).decode('utf-8'))


@app.route('/preview-cells.htm', methods=['POST'])
def preview_cells():
    global counter
    counter += 1

    try:
        img = upload_parse()
        img = export_cells(extract_cells(img, *find_segments(*find_edges(img))))
    except RuntimeError as err:
        return 'Could extract cells: {}'.format(err)

    return render_template('preview.htm', preview=b64encode(img).decode('utf-8'))


@app.route('/preview-image.htm', methods=['POST'])
def preview_image():
    global counter
    counter += 1

    try:
      img = export_image(upload_parse())
    except RuntimeError as err:
        return 'Could not preview image: {}'.format(err)

    return render_template('preview.htm', preview=b64encode(img).decode('utf-8'))


@app.route('/upload-image.htm', methods=['POST'])
def upload_image():
    global counter
    counter += 1

    try:
        img = upload_parse()
        data = read_cells(extract_cells(img, *find_segments(*find_edges(img))))
    except Exception as err:
        return 'Could not parse card: {}'.format(err)

    try:
        encoding = request.form['encoding'].encode('ASCII')
    except KeyError:
        return 'Your request is missing the encoding field'

    d = decode_card(encoding, data)
    if d is None:
        d = b'Encoding Error'

    try:
        sess_data = session['data']
    except KeyError:
        sess_data = []

    sess_data.append(d)
    session['data'] = sess_data

    return redirect('/list-data.htm', code=302)


@app.route('/list-data.htm', methods=['POST'])
def join_data():
    global counter
    counter += 1

    try:
        sess_data = session['data']
    except KeyError:
        sess_data = []

    res = []
    for i, d in enumerate(sess_data, 1):
        if str(i) in request.form:
            res.append(d)

    cmd = join_commands(res)

    for r in res:
        sess_data.remove(r)
    session['data'] = [cmd.encode('ascii')] + sess_data

    return redirect('/list-data.htm', code=302)

@app.route('/run-help.htm', methods=['POST'])
def run_help_lib():
    try:
        sess_data = session['data']
    except KeyError:
        sess_data = []

    if sess_data is None:
        sess_data = []

    id = int(request.form['id'])

    if int(id) < len(sess_data):
        ret = run_help(sess_data[id])
        return ret
    else:
        raise RuntimeError('id {} not found'.format(id))
