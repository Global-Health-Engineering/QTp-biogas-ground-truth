def test_connection():
    try:
        instrument = minimalmodbus.Instrument('/dev/ttyUSB0', 1)
        instrument.serial.baudrate = 9600
        instrument.serial.parity = serial.PARITY_NONE
        
        # Read module type (40129-40130)
        module_type = instrument.read_registers(
            registeraddress=128,  # 40129 - 40001 = 128
            number_of_registers=2,
            functioncode=3
        )
        hex_value = f"{module_type[0]:04X}{module_type[1]:04X}"
        return f"Connected to DAM-{hex_value[2:]}"
    
    except Exception as e:
        return f"Connection failed: {str(e)}"

