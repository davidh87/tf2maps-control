#!/usr/local/bin/python

from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
from flask import render_template

from werkzeug import secure_filename

import sys
import urllib
import argparse

from os import listdir
from os.path import isfile, join

app = Flask(__name__)

configOptions = {
	'dev': {
		'mapsDir': '/Users/davidh/Documents/tf2center/mapsDir'
	},
	'live': {
		'mapsDir': '/home/tf2/shared/maps'
	}
}

deploymentOptions = {}

ALLOWED_EXTENSIONS = set(['bsp'])

def getCurrentMaps():
	maps = []

	mapsDir = deploymentOptions['mapsDir']
	for f in listdir(mapsDir):
		if not isfile(join(mapsDir, f)):
			continue
		if f.endswith('.bsp'):
			maps.append(f)

	return maps

@app.route('/maps', methods=['GET'])
def listMaps():
	return jsonify({'maps':getCurrentMaps()})

def addMapFromUrl(mapName, mapUrl):
	currentMaps = getCurrentMaps()
	if mapName in currentMaps:
		return False

	mapsDir = deploymentOptions['mapsDir']
	testfile = urllib.URLopener()
	testfile.retrieve(mapUrl, join(mapsDir,mapName))

	return True

@app.route('/maps/add/url', methods=['POST'])
def addMap():
	data = request.get_json(force=True)
	if 'mapName' not in data:
		return Response(response='{error: "Missing required parameter - mapName"}', status=400)
	elif 'mapUrl' not in data:
		return Response(response='{error: "Missing required parameter - mapUrl"}', status=400)

	result = addMapFromUrl(data['mapName'], data['mapUrl'])

	if result == True:
		return Response(status=201)
	else:	
		return Response(status=204)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/maps/add/upload', methods=['POST'])
def addMapViaUpload():
	file = request.files['file']
	mapName = file.filename

	currentMaps = getCurrentMaps()
	if mapName in currentMaps:
		return Response(status=204)

	if file and allowed_file(mapName):
		filename = secure_filename(mapName)

		mapsDir = deploymentOptions['mapsDir']
		file.save(join(mapsDir, filename))

		return Response(status=201)

	return Response(response='{error: "Invalid file extension"}', status=400)

@app.route('/maps/upload', methods=['GET'])
def getMapUploadForm():
	return render_template('uploadFile.html')

@app.route('/maps/upload', methods=['POST'])
def addMapViaUIUpload():
	file = request.files['file']
	mapName = file.filename

	currentMaps = getCurrentMaps()
	if mapName in currentMaps:
		return Response(status=204)

	if file and allowed_file(mapName):
		filename = secure_filename(mapName)

		mapsDir = deploymentOptions['mapsDir']
		file.save(join(mapsDir, filename))

		return render_template('uploadSuccessful.html')

	return render_template('uploadFailed.html')

@app.route('/maps/upload/url', methods=['POST'])
def addMapViaUIURL():
	mapName = request.form['mapName']
	mapUrl = request.form['mapUrl']

	result = addMapFromUrl(mapName, mapUrl)
	if result == True:
		return render_template('uploadSuccessful.html')
	else:
		return render_template('mapExists.html')

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Simple web server for listing maps in a given directory')
	parser.add_argument('--config', metavar='config', type=str, nargs=1, help='Which config to use', default=['dev'])
	
	args = parser.parse_args()
	deploymentOptions = configOptions[args.config[0]]

	app.debug = True
	app.run()