import argparse
import sys
import time
from typing import List

import minimalmodbus


# --------------------------------------------------------------------------------------
# Mapping from human‑readable range names to lambda that turns raw counts into units
# --------------------------------------------------------------------------------------

def _make_range(name: str):
    name = name.lower()
    if name in {"4-20ma", "4‑20ma", "4_20ma", "4to20ma", "default"}:
        return name, lambda c: 4.0 + 16.0 * (c - 819) / (4095 - 819), "mA"
    if name in {"0-20ma", "0‑20ma", "0_20ma"}:
        return name, lambda c: 20.0 * c / 4095.0, "mA"
    if name in {"0-5v", "0‑5v", "0_5v"}:
        return name, lambda c: 5.0 * c / 4095.0, "V"
    if name in {"1-5v", "1‑5v", "1_5v"}:
        return name, lambda c: 1.0 + 4.0 * (c - 819) / (4095 - 819), "V"
    if name in {"0-2.5v", "0‑2.5v", "0_2.5v", "0-2v5"}:
        return name, lambda c: 2.5 * c / 2048.0, "V"
    raise argparse.ArgumentTypeError(f"Unknown range '{name}'")


# default 8 channels all 4‑20 mA
DEFAULT_RANGES = [_make_range("4-20mA") for _ in range(8)]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Read DF Robot DAM‑3918 analog inputs over Modbus RTU"
    )
    p.add_argument("--port", default="/dev/ttyUSB0", help="Serial port path")
    p.add_argument("--slave", type=int, default=1, help="Modbus slave address (1‑247)")
    p.add_argument("--baud", type=int, default=9600, help="Serial baud‑rate")
    p.add_argument(
        "--parity",
        choices=["N", "E", "O"],
        default="N",
        help="Parity (N=None, E=Even, O=Odd)",
    )
    p.add_argument(
        "--range",
        nargs=8,
        metavar="R",
        help="Eight range names (per channel). Each can be one of: '4-20mA', '0-20mA', '0-5V', '1-5V', '0-2.5V'. If omitted, all channels assumed 4-20mA.",
    )
    p.add_argument("--debug", action="store_true", help="Enable verbose debug output")
    return p.parse_args()


def main() -> None:
    ns = parse_args()

    # Build range converters
    ranges: List[tuple] = (
        [_make_range(r) for r in ns.range]
        if ns.range is not None
        else DEFAULT_RANGES
    )

    instrument = minimalmodbus.Instrument(ns.port, ns.slave, mode=minimalmodbus.MODE_RTU)
    instrument.serial.baudrate = ns.baud
    instrument.serial.bytesize = 8
    instrument.serial.parity = {"N": minimalmodbus.serial.PARITY_NONE, "E": minimalmodbus.serial.PARITY_EVEN, "O": minimalmodbus.serial.PARITY_ODD,}[ns.parity]
    instrument.serial.stopbits = 1
    instrument.serial.timeout = 0.2  # seconds
    instrument.debug = ns.debug

    print(
        f"Opened {ns.port} @ {ns.baud} baud, slave {ns.slave}. Press Ctrl‑C to abort.\n"
    )

    try:
        while True:
            # The holding registers start at 0; 40001 => register 0
            raw_vals = instrument.read_registers(registeraddress=0, number_of_registers=8, functioncode=3)
            # raw_vals is list[int]
            ts = time.strftime("%Y‑%m‑%d %H:%M:%S")
            print(ts)
            for ch, raw in enumerate(raw_vals):
                rng_name, conv, unit = ranges[ch]
                try:
                    eng = conv(raw)
                    print(
                        f"  CH{ch}: {raw:4d} counts  -->  {eng:6.3f} {unit}  ({rng_name})"
                    )
                except Exception as exc:
                    print(f"  CH{ch}: {raw:4d} counts  (conversion error: {exc})")
            print("-" * 60)
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nDone.")


if __name__ == "__main__":
    main()
