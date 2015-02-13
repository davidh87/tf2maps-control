#!/usr/bin/python

from flask import Flask
from flask import jsonify
from flask import request
from flask import Response
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
	}
}

deploymentOptions = {}

ALLOWED_EXTENSIONS = set(['bsp', 'bsp.bz2'])

def getCurrentMaps():
	maps = {
		'uncompressed': [],
		'compressed': []
	}

	mapsDir = deploymentOptions['mapsDir']
	for f in listdir(mapsDir):
		if not isfile(join(mapsDir, f)):
			continue
		if f.endswith('.bsp'):
			maps['uncompressed'].append(f)
		elif f.endswith('.bsp.bz2'):
			maps['compressed'].append(f)

	return maps

@app.route('/maps', methods=['GET'])
def listMaps():
	return jsonify(getCurrentMaps())

@app.route('/maps/add/url', methods=['POST'])
def addMap():
	data = request.get_json(force=True)
	if 'mapName' not in data:
		return Response(response='{error: "Missing required parameter - mapName"}', status=400)
	elif 'mapUrl' not in data:
		return Response(response='{error: "Missing required parameter - mapUrl"}', status=400)

	currentMaps = getCurrentMaps()
	if data['mapName'] in currentMaps['uncompressed']:
		return Response(status=204)

	mapsDir = deploymentOptions['mapsDir']
	testfile = urllib.URLopener()
	testfile.retrieve(data['mapUrl'], join(mapsDir,data['mapName']))

	return Response(status=201)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/maps/add/upload', methods=['POST'])
def addMapViaUpload():
	file = request.files['file']
	mapName = file.filename
	data = request.data

	currentMaps = getCurrentMaps()
	if mapName in currentMaps['uncompressed']:
		return Response(status=204)

	if file and allowed_file(mapName):
		filename = secure_filename(mapName)

		mapsDir = deploymentOptions['mapsDir']
		file.save(join(mapsDir, filename))

	return Response(status=201)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Simple web server for listing maps in a given directory')
	parser.add_argument('--config', metavar='config', type=str, nargs=1, help='Which config to use', default='dev')
	
	args = parser.parse_args()
	deploymentOptions = configOptions[args.config]

	app.debug = True
	app.run()