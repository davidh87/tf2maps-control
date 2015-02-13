#!/usr/bin/python

from flask import Flask
from flask import jsonify
from flask import request
from flask import Response

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

@app.route('/maps', methods=['GET'])
def listMaps():
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

	return jsonify(maps)

@app.route('/maps/add/url', methods=['POST'])
def addMap():
	data = request.get_json(force=True)
	if 'mapName' not in data:
		return Response(response='{error: "Missing required parameter - mapName"}', status=400)
	elif 'mapUrl' not in data:
		return Response(response='{error: "Missing required parameter - mapUrl"}', status=400)

	mapsDir = deploymentOptions['mapsDir']
	testfile = urllib.URLopener()
	testfile.retrieve(data['mapUrl'], join(mapsDir,data['mapName']))

	return Response(status=204)


if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Simple web server for listing maps in a given directory')
	parser.add_argument('--config', metavar='config', type=str, nargs=1, help='Which config to use', default='dev')
	
	args = parser.parse_args()
	deploymentOptions = configOptions[args.config]

	app.debug = True
	app.run()