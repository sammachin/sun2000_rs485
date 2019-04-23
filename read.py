#! /usr/bin/env python
# -*- coding: utf-8

import minimalmodbus
import datetime
import argparse
import json
import pickle

instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1) # port name, slave address (in decimal)
instrument.serial.baudrate = 9600


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


def get_data():
  resp = {}
  resp['time'] = datetime.datetime.fromtimestamp(instrument.read_long(40000)).strftime("%Y-%m-%d %H:%M:%S")
  resp['status'] = status_map[str(instrument.read_register(40939, 0))]
  resp['temperature'] = instrument.read_register(40533, 1) 
  resp['inverter_efficency'] = instrument.read_register(40685, 2) 
  resp['frequency'] = instrument.read_register(40546, 2)
  resp['current_power'] = instrument.read_long(40525)
  resp['day_power'] = instrument.read_long(40562)*10
  resp['total_power'] = instrument.read_long(40560)*10
  return resp


def new_day():
  d = datetime.datetime.now()
  file = d.strftime('%Y%m%d.pkl')
  arr = []
  data = ['Time', 'Power']
  arr.append(data)
  pickle.dump(arr, open(file, "wb")) 



def update_power():
  d = datetime.datetime.now()
  file = d.strftime('%Y%m%d.pkl')
  arr = pickle.load(open(file, "rb"))
  ts = d.strftime('%H:%M')
  power = instrument.read_long(40525)
  data = [ts, power]
  arr.append(data)
  pickle.dump(arr, open(file, "wb"))
  
  
def totals():
  d = datetime.datetime.now()
  file = 'totals.pkl'
  arr = pickle.load(open(file, "rb"))
  ts = d.strftime('%Y%m%d')
  power = instrument.read_long(40562)*10
  total = instrument.read_long(40560)*10
  data = [ts, daily, total]
  arr.append(data)
  pickle.dump(arr, open(file, "wb"))
  

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('function', help='The function to execute, newday|update|get')
  args = parser.parse_args()
  if args.function == 'newday':
    new_day()
  elif args.function == 'update':
    update_power()
  elif args.function == 'get':
    data = get_data()
    print(json.dumps(data, indent=4, sort_keys=True))
  else:
    print('Unknown function: '+args.function)


if __name__ == "__main__":
  main()
