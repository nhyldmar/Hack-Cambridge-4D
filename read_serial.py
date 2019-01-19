"""Reads serial output."""

import serial as s;p=s.Serial('COM5')
while 1:print(p.readline().decode('utf-8'))