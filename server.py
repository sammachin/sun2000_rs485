#! /usr/bin/env python
# -*- coding: utf-8
#import minimalmodbus
import datetime
from flask import Flask, jsonify
import string
import pickle
import json

app = Flask(__name__, static_url_path='')
port = 8000




status_map = { 
    "0" : "Idle Initialising",
    "1" : "Idle ISO Detecting",
    "2" : "Idle Irradiation Detecting",
    "256" : "Starting",
    "512" : "On-grid",
    "513" : "On-grid Limited",
    "768" : "Shutdown Abnormal",
    "769" : "Shutdown Forced",
    "1025" : "Grid Dispatch: cosψ-P Curve",
    "1026" : "Grid Dispatch: Q-U Curve",
    "40960" : "Idle: No Irradiation"
    }


  
@app.route('/data', methods=['GET'])
def data():
    instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1) # port name, slave address (in decimal)
    instrument.serial.baudrate = 9600
    resp = {}
    resp['time'] = datetime.fromtimestamp(instrument.read_long(40000)).strftime("%Y-%m-%d %H:%M:%S")
    resp['status'] = status_map[str(instrument.read_register(40939, 0))]
    resp['temperature'] = instrument.read_register(40533, 1) 
    resp['inverter_efficency'] = instrument.read_register(40685, 2) 
    resp['frequency'] = instrument.read_register(40546, 2)
    resp['current_power'] = instrument.read_long(40525)
    resp['day_power'] = instrument.read_long(40562)/100
    resp['total_power'] = instrument.read_long(40560)/100
    return jsonify(resp)
    

@app.route('/', methods=['GET'])
def root():
  d = datetime.date.today()
  file = d.strftime('%Y%m%d.pkl')
  arr = pickle.load(open(file, "rb"))
  data={ 'data':json.dumps(arr)}
  filein = open('static/graph.html')
  src = string.Template(filein.read())
  page = src.substitute(data)
  return page
  
    
        
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=port)
    