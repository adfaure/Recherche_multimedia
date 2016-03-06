import os
from flask import Flask, request, redirect, url_for
from werkzeug import secure_filename
import subprocess
import time

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['jpg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def eval_file(file_path):
    process = subprocess.Popen([
        './scripts/eval_image.py',
        '--config', 'install.ini',
        '--image-path', file_path,
        '--result', 'nothing'
    ])
    while not process.poll() is not None:
        time.sleep(0)
        pass
    app.logger.debug("fin eval")


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            app.logger.debug("getting file " + filename)
            eval_file(os.path.join(UPLOAD_FOLDER, filename))
            return redirect(url_for('index'))
    return """
    <!doctype html>
    <title>Upload new File</title>
        <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <p>%s</p>
    """ % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'],))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)