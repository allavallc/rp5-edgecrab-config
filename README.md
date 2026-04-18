# EdgeCrab on Raspberry Pi 5 — Hardware AI Agent

This repo documents a working setup that turns a Raspberry Pi 5 into an AI agent (EdgeCrab) that can control Arduino hardware and see through a USB camera.

## What it does

- EdgeCrab (edgecrab.ai) runs on the Pi as an LLM-powered agent
- It can write, compile, and upload Arduino sketches
- It can send/receive serial commands to the Arduino
- It can capture images from a USB camera and visually verify hardware state (e.g. "is the LED blinking?")

## Hardware

- Raspberry Pi 5 (64-bit Raspberry Pi OS)
- Arduino Uno (connected via USB)
- Any UVC-compatible USB webcam

## Repo contents

| File | Purpose |
|------|---------|
| `SETUP.md` | Full step-by-step setup instructions |
| `edgecrab-config-snippet.yaml` | The MCP server config block to add to `~/.edgecrab/config.yaml` |
| `memory-template.md` | Seed memory for EC about the Arduino hardware |
| `soul-snippet.md` | Addition to `~/.edgecrab/SOUL.md` to make EC proactively use its memory |

## The MCP server

The actual MCP server lives at `/home/pi/arduino-mcp/server.py` (not in this repo — path is hardcoded in EC's config). It exposes Arduino and camera tools to EdgeCrab via the MCP protocol.

To install it:
```bash
git clone https://github.com/allavallc/rp5-edgecrab-config.git /home/pi/arduino-mcp
pip3 install mcp pyserial opencv-python --break-system-packages
```

See `SETUP.md` for the full walkthrough.

## Key gotcha

EC does not auto-detect attached hardware. Cameras, sensors, and other devices are invisible to EC unless a tool explicitly exposes them. That's what this MCP server does.
