import json
import os
import requests
import pdb
from yattag import Doc

USERNAME = 'cad1d95f-9233-4933-9dfb-2a7472764e22-bluemix'
PASSWORD = '5d1b13d6c400a298a3a6301e5826b7da71a517fcb30343050d6689fbf8530461'
ACCOUNT_NAME = 'my-cloudant'
creds = (USERNAME, PASSWORD)
baseURI = "https://{0}.cloudant.com/{1}".format(USERNAME, ACCOUNT_NAME)

def createDb():
	# Create Database
	response = requests.put(
	    baseURI,
	    auth=creds
	)
	print "Created database at {0}".format(baseURI)

def createDocument(docName):
	# Create a document on the database
	response = requests.get(
	    "{0}/{1}".format(baseURI, docName),
	    auth=creds
	)
	# if document already present, ignore
	if response.status_code == 404: 
		response = requests.post(
		    baseURI,
		    data=json.dumps({
		    	"_id": docName,
		    	"files": []	        
		    }),
		    auth=creds,
		    headers={"Content-Type": "application/json"}
		)
		docId = response.json()["id"]
		print "The new document's ID is {0}".format(docId)	

def updateDocument(docName, fname, fileData, hashValue, curTime):
	# add data to the document
	response = requests.get(
	    "{0}/{1}".format(baseURI, docName),
	    auth=creds
	)
	doc = response.json()
	print "The document's rev is {0}".format(doc["_rev"])

	found = False
	filesArray = doc['files']
	max_version = 0;

	# Scan through all the files
	for f in filesArray:
		if str(f['filename']) == fname:
			if max_version < int(f['version_number']):
				max_version = int(f['version_number'])
			if str(f['hashed_value']) == hashValue:
				found = True
				break
			else:
				found = False
	
	max_version = max_version + 1 				

	# append to the existing list and increment version
	if found == False:
		doc['files'].append(dict(filename=fname, 
                	version_number=max_version,
                	last_modified_date=curTime,
                	contents=fileData,
                	hashed_value= hashValue,
            	))
	else:
		# Duplicate file found
		return 'Duplicate File'

	response = requests.put(
	    "{0}/{1}".format(baseURI, docName),
	    data=json.dumps(doc),
	    auth=creds
	)
	rev2 = response.json()['rev']
	print "The document's new rev is {0}".format(rev2)
	return 'File uploaded with version ' + str(max_version)

def deleteMyFile(docName, fname, version):
	# add data to the document
	response = requests.get(
	    "{0}/{1}".format(baseURI, docName),
	    auth=creds
	)
	doc = response.json()
	print "The document's rev is {0}".format(doc["_rev"])
	found = False
	filesArray = doc['files']
	# Scan through all the files
	for f in filesArray:
		if str(f['filename']) == fname:
			if version == int(f['version_number']):
				found = True
				filesArray.remove(f)
				break
			else:
				found = False

	if found == False:
		return 'File not found'
	else:
		response = requests.put(
	    	"{0}/{1}".format(baseURI, docName),
	    	data=json.dumps(doc),
	    	auth=creds
		)
		return 'File Deleted'


def getMyFile(filename, docName, version_number):
	# Download file request
	response = requests.get(
	    "{0}/{1}".format(baseURI, docName),
	    auth=creds
	)
	doc = response.json()
	filesArray = doc['files']

	for f in filesArray:
		if f['filename'] == filename:
			if int(f['version_number']) == version_number:
				return str(f['contents'])

	return 'Not Found'

def listMyFiles(docName):
	response = requests.get(
	    "{0}/{1}".format(baseURI, docName),
	    auth=creds
	)
	doc = response.json()
	filesArray = doc['files']
	# Scan through all the files
	doc, tag, text = Doc().tagtext()
	with tag('html'):
		with tag('style'):text('table, th, td {border: 1px solid black; border-collapse: collapse;}th, td {padding: 5px;}')
		with tag('body'):
			with tag('table'):
				with tag('tr', style="font-weight:bold"):
					with tag('td'): text('Filename')   
					with tag('td'): text('Version')
					with tag('td'): text('Last Modified On')
				for f in filesArray:
					with tag('tr'):
						with tag('td'): text(str(f['filename']))   
						with tag('td'): text(str(f['version_number']))
						with tag('td'): text(str(f['last_modified_date']))
	result = doc.getvalue()
	return result				

def deleteDocument(docName):
	print "Deleting document"
	response = requests.delete(
	    "{0}/{1}".format(baseURI, docName),
	    params={"rev": rev2},
	    auth=creds
	)

	print " > doc: ", response.json()

def deleteDatabase(baseURI, creds):
	print 'Deleting database'
	response = requests.delete(
	    baseURI,
	    auth=creds
	)
	print " > db: ", response.json()
