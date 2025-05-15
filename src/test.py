# import minimalmodbus
# import serial

# # Configure Modbus RTU
# instrument = minimalmodbus.Instrument(
#     port='/dev/ttyACM3',  # Confirm port with ls /dev/tty*
#     slaveaddress=1,       # Default DAM-3918 address
#     debug=False
# )
# instrument.serial.baudrate = 9600
# instrument.serial.parity = serial.PARITY_NONE
# instrument.serial.timeout = 0.2

# def read_pressure():
#     """Reads raw ADC value and converts to pressure"""
#     raw_value = instrument.read_register(
#         registeraddress=6,  # IN7 register (verify in DAM-3918 docs)
#         numberOfDecimals=0,
#         functioncode=4
#     )
#     # Convert to PSI (0-200 range for 4-20mA)
#     pressure_psi = (raw_value - 3277) * (200 / 26214)  # Linear scaling
#     return pressure_psi

# print(f"Current pressure: {read_pressure():.2f} PSI")

# Install required library first
!pip install minimalmodbus  # Run this only once

import minimalmodbus
import serial

def test_connection():
    try:
        # Configure communication - REPLACE PORT NAME IF NEEDED
        instrument = minimalmodbus.Instrument(
            port='/dev/ttyACM43',  # Common alternatives: /dev/ttyAMA0, /dev/ttyS0
            slaveaddress=1,       # Default address (confirm DIP switch settings)
        )
        instrument.serial.baudrate = 9600
        instrument.serial.parity = serial.PARITY_NONE
        instrument.serial.timeout = 0.5

        # Test read device identification (Modbus function code 43)
        device_info = instrument.read_registers(300, 4, 4)
        return f"Connection successful. Device ID: {device_info}"
        
    except Exception as e:
        return f"Connection failed: {str(e)}"

print(test_connection())
