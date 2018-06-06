import os
from flask import Flask, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import subprocess
import timeout_decorator
from codesearch.utils.redis_queue import RedisQueueExchange
import time
import json

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
    '''


@app.route('/home/', methods=['GET'])
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
            subprocess.check_output(['/bin/bash', '-c', 'indexer.sh'])
            queue_exchange.delete('output')
            return redirect(url_for('uploaded_file', filename=filename))

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload a zip or python file for semantic indexing</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/semantic/index/', methods=['GET', 'POST'])
def semantic_index():
    subprocess.check_output(['/bin/bash', '-c', 'indexer.sh'])
    queue_exchange.delete('output')
    return '''
    <!doctype html>
    <title>Semantic Index</title>
    <h1>Semantic indexing completed!</h1>
    '''


def fetch_result(query):
    while True:
        result = queue_exchange.fetch('output', query)
        if result:
            return result
        time.sleep(0.025)


@app.route('/semantic/search/', methods=['GET'])
def semantic_search():
    query = request.args.get('q', '')
    if not query:
        return "Please provide query param `q` for example /search/?q=load+data+from+files", 400
    queue_exchange.write('input', query)
    results = timeout_decorator.timeout(10, use_signals=False)(fetch_result)(query)
    return jsonify(json.loads(results)), 200


if __name__ == '__main__':
    app.run('0.0.0.0', 8080, threaded=True)
