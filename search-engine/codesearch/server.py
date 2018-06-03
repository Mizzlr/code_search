import os
from flask import Flask, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import subprocess
from codesearch.query.searcher import SemanticCodeSearchEngine

UPLOAD_FOLDER = 'uploads'
INDEX_FOLDER = 'index'
ALLOWED_EXTENSIONS = set(['py', 'zip'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['INDEX_FOLDER'] = INDEX_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploaded/<filename>')
def uploaded_file(filename):
    return f'''
        <!doctype html>
        <title>Upload Success </title>
        <h1>Your file ({filename}) uploaded successfully.</h1>
    '''


@app.route('/upload/', methods=['GET', 'POST'])
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
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/semantic/index/', methods=['GET', 'POST'])
def semantic_index():
    subprocess.check_output(['python3', 'codesearch/code/indexer.py',
                             app.config['UPLOAD_FOLDER'], app.config['INDEX_FOLDER']])
    return '''
    <!doctype html>
    <title>Semantic Index</title>
    <h1>Semantic indexing completed!</h1>
    '''


@app.route('/semantic/search/', methods=['GET'])
def semantic_search():
    search_engine = SemanticCodeSearchEngine(app.config['INDEX_FOLDER'])
    return jsonify(search_engine.search(query=request.args.get('q', '').replace('+', ' ')))


if __name__ == '__main__':
    app.run('0.0.0.0', 8080, threaded=True)
