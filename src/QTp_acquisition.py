import serial
import logging
import RPi.GPIO as GPIO
import time
from datetime import datetime
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException


class FlowMeter(object):
    def __init__(self, pin):
        self.pulse_gen = pin # GPIO pin number (BCM numbering)
        self.pulse_freq = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pulse_gen,
                   GPIO.IN,
                   pull_up_down = GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.pulse_gen,
                              GPIO.RISING,
                              callback = self.pulse)

    def pulse(self, channel):
        self.pulse_freq += 1

    def flow_rate_generator(self):
        last_time = time.time()
        try:
            while True:
                current_time = time.time()
                if current_time - last_time >= 1.0:
                    last_time = current_time
                    flow_rate = self.pulse_freq + 0.005 * 60 # liters/min
                    yield flow_rate
                    self.pulse_freq = 0
                time.sleep(0.01)
        except GeneratorExit:
            GPIO.cleanup()
            raise


def read_flow():
    meter = FlowMeter(pin=2)
    try:
        for flow_rate in meter.flow_rate_generator():
            print(flow_rate)
    except KeyboardInterrupt:
        pass


def read_pressure():
    client = ModbusSerialClient(port = '/dev/ttyACM3',
                                baudrate = 9600,
                                bytesize = 8,
                                parity = 'N',
                                stopbits = 1)

    try:
        if client.connect():
            response = client.read_input_registers(address = 7,
                                                   #address = 0x0007,
                                                   count = 1,
                                                   slave = 1)
            if response.isError():
                print(f"Modbus error: {response}")
                return None
            raw_value = response.registers[0]
            if raw_value is not None:
                current = 4 + (16 * raw_value / 32767) # convert to 4-20 mA
                return (current - 4) / 16 * 10 # 0-10 bar conversion
            else:
                return raw_value

    except ModbusException as e:
        print(f"Modbus exception: {e}")

    finally:
        client.close()


def read_temperature():
    ser = serial.Serial('/dev/ttyACM4',
                        baudrate = 9600,
                        timeout = 1)
    ser.reset_input_buffer()

    while True:
        if ser.in_waiting > 0:
            temp = ser.readline().decode('utf-8').rstrip()
            return float(temp)


def main():
    while True:
        v = read_pressure()
        # v = read_temperature()
        print(v)
        time.sleep(1)



if __name__ == "__main__":
    main()
