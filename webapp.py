import os
import uuid
import json
from flask import Flask, request, redirect, url_for, render_template, jsonify, Response
from werkzeug import secure_filename
import subprocess
import time

UPLOAD_FOLDER = '/var/www/index_mult'
ALLOWED_EXTENSIONS = set(['jpg', 'png'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def generate_random_folder():
    temp_folder_name = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_' + str(uuid.uuid4()) + str(uuid.uuid4()))
    while os.path.exists(temp_folder_name):
        temp_folder_name = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_' + str(uuid.uuid4()) + str(uuid.uuid4()))
    return temp_folder_name


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
    #while not process.poll() is not None:
    #    time.sleep(0)
    #    pass
    return process.returncode


@app.route('/upload', methods=['POST'])
def upload_file():
    res = dict()
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            temp_folder_name = generate_random_folder()
            photo_folder = os.path.join(app.config['UPLOAD_FOLDER'], temp_folder_name)
            os.system("mkdir -p " + photo_folder)
            uploaded_file.save(os.path.join(photo_folder, filename))
            eval_file(os.path.join(photo_folder, filename))
            res["exec_path"] = os.path.basename(temp_folder_name)
            res["photo_name"] = os.path.basename(filename)
            return jsonify(res), 200
        else :
            return "file extension not allowed, only jpg and png",  400
    return "", 404


@app.route('/upload_url', methods=['POST'])
def upload_url():
    res = dict()
    if request.method == 'POST':
        print request.data
        dataDict = json.loads(request.data)
        photo_url = dataDict['url']
        if not (photo_url.startswith("http://") or photo_url.startswith("https://")):
            return "Wrong url must begin with http:// or https://", 400
        elif not allowed_file(photo_url):
            return "file extension not allowed, only jpg and png", 400
        else:
            folder_name = generate_random_folder()
            file_name = os.path.basename(photo_url)
            os.mkdir(folder_name)
            os.system('curl ' + photo_url + ' > ' + os.path.join(folder_name, file_name))
            if not os.path.exists(os.path.join(folder_name, file_name)):
                return "We were not able to dowload the photo, was the url correct ?", 500
            eval_file(os.path.join(folder_name, file_name))
            res["exec_path"] = os.path.basename(folder_name)
            res["photo_name"] = os.path.basename(file_name)
            return jsonify(res), 200
    return "", 404

if __name__ == "__main__":
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.system("mkdir -p " + app.config['UPLOAD_FOLDER'])
    app.run(host='0.0.0.0', port=5000, debug=True)
