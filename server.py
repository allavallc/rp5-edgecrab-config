#!/usr/bin/env python3
"""MCP server exposing Arduino tools to EdgeCrab."""

import subprocess
import time
import serial
from mcp.server.fastmcp import FastMCP

PORT = "/dev/ttyACM0"
BAUD = 9600
ARDUINO_CLI = "/home/pi/bin/arduino-cli"

mcp = FastMCP("arduino")


@mcp.tool()
def list_boards() -> str:
    """List all connected Arduino boards and their ports/FQBNs."""
    result = subprocess.run(
        [ARDUINO_CLI, "board", "list"],
        capture_output=True, text=True
    )
    return result.stdout or result.stderr


@mcp.tool()
def list_cores() -> str:
    """List installed Arduino cores."""
    result = subprocess.run(
        [ARDUINO_CLI, "core", "list"],
        capture_output=True, text=True
    )
    return result.stdout or result.stderr


@mcp.tool()
def compile_sketch(sketch_dir: str, fqbn: str = "arduino:avr:uno") -> str:
    """Compile an Arduino sketch. sketch_dir is the path to the sketch folder."""
    result = subprocess.run(
        [ARDUINO_CLI, "compile", "--fqbn", fqbn, sketch_dir],
        capture_output=True, text=True
    )
    return (result.stdout + result.stderr).strip()


@mcp.tool()
def upload_sketch(sketch_dir: str, port: str = PORT, fqbn: str = "arduino:avr:uno") -> str:
    """Compile and upload an Arduino sketch to the board."""
    compile_result = subprocess.run(
        [ARDUINO_CLI, "compile", "--fqbn", fqbn, sketch_dir],
        capture_output=True, text=True
    )
    if compile_result.returncode != 0:
        return "Compile failed:\n" + compile_result.stderr

    upload_result = subprocess.run(
        [ARDUINO_CLI, "upload", "-p", port, "--fqbn", fqbn, sketch_dir],
        capture_output=True, text=True
    )
    return (upload_result.stdout + upload_result.stderr).strip()


@mcp.tool()
def serial_send(command: str, read_seconds: float = 2.0, baud: int = BAUD) -> str:
    """Send a command over serial and return the response."""
    try:
        with serial.Serial(PORT, baud, timeout=0.1) as ser:
            time.sleep(0.1)
            ser.reset_input_buffer()
            ser.write((command + "\n").encode())
            ser.flush()
            deadline = time.time() + read_seconds
            lines = []
            while time.time() < deadline:
                line = ser.readline()
                if line:
                    lines.append(line.decode(errors="replace").rstrip())
            return "\n".join(lines) if lines else "(no response)"
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def serial_read(read_seconds: float = 2.0, baud: int = BAUD) -> str:
    """Read serial output from the Arduino for a given number of seconds."""
    try:
        with serial.Serial(PORT, baud, timeout=0.1) as ser:
            time.sleep(0.1)
            ser.reset_input_buffer()
            deadline = time.time() + read_seconds
            lines = []
            while time.time() < deadline:
                line = ser.readline()
                if line:
                    lines.append(line.decode(errors="replace").rstrip())
            return "\n".join(lines) if lines else "(no output)"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
