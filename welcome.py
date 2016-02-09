import os
import requests
from flask import Flask, request, send_file
import pdb
import StringIO
from couchdbclient import *
from time import gmtime, strftime
import hashlib

UPLOAD_FOLDER = './uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'

@app.route('/')
def Welcome():
    return app.send_static_file('index.html')

@app.route('/upload', methods=['POST'])
def Uploaded():
    # File uploaded will be handled here
    fd = request.files['myfile']
    if not fd:
        return "No file"
    docName = 'myFiles'
    fname = fd.filename
    fileData = fd.read()
    hashValue = getHashValue(fileData)
    curTime  =strftime('%Y-%m-%d %H:%M:%S', gmtime())
    #createDb()        
    createDocument(docName)
    result = updateDocument(docName, fname, fileData, hashValue, curTime)
    #deleteDocument(docName)
    return result

@app.route("/action", methods=['GET','POST'])
def downloadOrDeleteFile():
    # File download request will be handled here
    #pdb.set_trace()
    version = int(request.form.get('Version'))
    fname = str(request.form.get('Filename'))

    if request.form['submit'] == 'Download':
        print 'In download'
        data = getMyFile(fname, 'myFiles', version) 
        if data == 'Not Found':
            return 'File Not Found'
        else:
            print 'Got file'
            strIO = StringIO.StringIO()
            strIO.write(str(data))
            strIO.seek(0)
            return send_file(strIO, attachment_filename=fname, as_attachment=True)
    else:
        return deleteFile(fname, version)

@app.route("/list", methods=['GET','POST'])
def listFiles():
    # File download request will be handled here
    return listMyFiles('myFiles')

def deleteFile(fname, version):
    # File download request will be handled here
    version = int(request.form.get('Version'))
    fname = str(request.form.get('Filename'))
    print 'In Delete File'
    data = deleteMyFile('myFiles', fname, version)     
    return data

def getHashValue(fileData):
    # Hashing of the file contents 
    hasher = hashlib.md5()
    buf = fileData
    hasher.update(buf)
    print(hasher.hexdigest())
    return str(hasher.hexdigest())

@app.route('/myapp')
def WelcomeToMyapp():
    return 'Welcome again to my app running on Bluemix!'

port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
