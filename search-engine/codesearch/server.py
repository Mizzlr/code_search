import os
from flask import Flask, request, redirect, url_for, flash, jsonify, abort, send_file, render_template_string
from werkzeug.utils import secure_filename
import subprocess
import timeout_decorator
from codesearch.utils.redis_queue import RedisQueueExchange
import time
import json
import pathlib

UPLOAD_FOLDER = 'storage/uploads'
ALLOWED_EXTENSIONS = set(['py', 'zip'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
queue_exchange = RedisQueueExchange()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploaded/<filename>')
def uploaded_file(filename):
    return f'''
        <!doctype html>
        <title>Uploaded and successfully semantically indexed your files.</title>
        <h1>Your file ({filename}) uploaded successfully.</h1>
        <p> <a href="/home/"> Back to home </a> </p> <br/>
    '''


@app.route('/home/', methods=['GET', 'POST'])
@app.route('/upload/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            subprocess.check_output(['/bin/bash', '-c', './indexer.sh'])
            queue_exchange.delete('output')
            return redirect(url_for('uploaded_file', filename=filename))

    return '''
    <!doctype html>
    <style>
        body {
            margin: auto;
        }
    </style>
    <title>Upload new File</title>
    <body>
    <h1>Upload a zip or python file for semantic indexing</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>

    <p> <a href="/browse/"> Browse files here </a> </p>
    <p> <a href="/semantic/index/"> Click here to re index everything again. </a> </p> <br/>

    <h1>Type search term here</h1>
    <form method="GET" action="/semantic/search/">
      <p>
        <input type="text" name="q">
         <input type=submit value=Search>
      </p>
    </form>
    </body>
    '''


@app.route('/semantic/index/', methods=['GET', 'POST'])
def semantic_index():
    subprocess.check_output(['/bin/bash', '-c', './indexer.sh'])
    queue_exchange.delete('input')
    queue_exchange.delete('output')
    return '''
    <!doctype html>
    <title>Semantic Index</title>
    <h1>Semantic indexing completed!</h1>
    <p> <a href="/home/"> Back to home </a> </p> <br/>
    '''


def fetch_result(query):
    while True:
        result = queue_exchange.fetch('output', query)
        if result:
            return result
        time.sleep(0.025)


@app.route('/semantic/search/', methods=['GET'])
def semantic_search():
    queue_exchange.delete('input')
    queue_exchange.delete('output')

    query = request.args.get('q', '')
    print('Search term: ', query)
    if not query:
        return "Please provide query param `q` for example /search/?q=load+data+from+files", 400
    queue_exchange.write('input', query)
    results = timeout_decorator.timeout(10, use_signals=False)(fetch_result)(query)
    results = json.loads(results)
    for result in results:
        result['file'] = '/'.join(request.url.split('/', maxsplit=3)[:-1]) +\
            url_for('browse') +\
            result['file'].split(app.config['UPLOAD_FOLDER'], maxsplit=1)[1].lstrip('/')

    queue_exchange.delete('output', query)
    return jsonify(results), 200


@app.route('/browse/', defaults={'req_path': ''})
@app.route('/browse/<path:req_path>')
def browse(req_path):

    # Joining the base and the requested path
    abs_path = os.path.abspath(os.path.join(app.config['UPLOAD_FOLDER'], req_path))

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path)

    # Show directory contents
    files = [str(path).split(app.config['UPLOAD_FOLDER'], maxsplit=1)[1].lstrip('/')
             for path in pathlib.Path(abs_path).glob('**/*.py')]

    return render_template_string("""
    <h1> Browse for files here </h1>
    <p> <a href="/home/"> Back to home </a> </p> <br/>
    <ul>
        {% for file in files %}
        <li><a href="/browse/{{ file }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
    """, files=files)


if __name__ == '__main__':
    import sys
    app.run('0.0.0.0', int(sys.argv[1]), threaded=True)
