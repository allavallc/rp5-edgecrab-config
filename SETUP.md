# EdgeCrab on Raspberry Pi 5 — Full Setup Reference

This repo captures a complete working setup of EdgeCrab (edgecrab.ai) on a Raspberry Pi 5,
including an Arduino MCP server for hardware control. Intended as a reference for another
LLM or human to replicate the setup from scratch.

---

## System

- Raspberry Pi 5, 64-bit Raspberry Pi OS (arm64)
- Main partition: ~29GB SD card
- `/tmp` is a RAM-based tmpfs (2GB limit) — important for Rust builds (see below)

---

## 1. Install EdgeCrab

EdgeCrab is a Rust binary installed via cargo.

**Important:** `/tmp` fills up during large Rust builds. Always redirect the build cache:

```bash
CARGO_TARGET_DIR=/home/pi/cargo-build-cache cargo install edgecrab
```

Or set permanently in `~/.cargo/config.toml`:

```toml
[build]
target-dir = "/home/pi/cargo-build-cache"
```

Verify:
```bash
edgecrab --version
```

---

## 2. Configure the API Key

EdgeCrab's `chat` command does not load `~/.edgecrab/.env` into the system environment.
The API key must be exported in `~/.bashrc`.

```bash
# ~/.bashrc
export GEMINI_API_KEY="your-key-here"
export GOOGLE_API_KEY="your-key-here"   # same key, both vars needed
```

Then `source ~/.bashrc`.

---

## 3. Configure the Model

Edit `~/.edgecrab/config.yaml`:

```yaml
model:
  default: google/gemini-2.5-flash-lite   # or gemini-2.5-flash for better quality
  api_key_env: GEMINI_API_KEY
```

Note: even if `api_key_env` is set to a different variable name, EdgeCrab will pick up
`GEMINI_API_KEY` from the environment for Google models.

---

## 4. Enable Memory and File Access

In `~/.edgecrab/config.yaml`, ensure:

```yaml
memory:
  enabled: true
  auto_flush: true

skip_memory: false

tools:
  file:
    allowed_roots:
      - /home/pi
```

Without `allowed_roots`, EdgeCrab cannot search the filesystem.

---

## 5. Teach EdgeCrab to Use Its Memory

By default, smaller models don't proactively reference stored memory. Add this to
`~/.edgecrab/SOUL.md`:

```
At the start of every session, review your memory files (MEMORY.md and USER.md)
and proactively use that context when answering questions — even if the user doesn't
explicitly ask you to recall it. If stored context is relevant to the current question,
apply it without being prompted.
```

---

## 6. Install arduino-cli

```bash
curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | sh
# installs to ~/bin/arduino-cli by default
arduino-cli core update-index
arduino-cli core install arduino:avr
```

Verify a connected Uno:
```bash
arduino-cli board list
```

Expected output includes `/dev/ttyACM0` with FQBN `arduino:avr:uno`.

Note: `/dev/ttyAMA10` is the Pi's built-in GPIO UART — always shows as "Unknown", not
a connected board. Ignore it.

---

## 7. Install the Arduino MCP Server

Install dependencies:
```bash
pip3 install mcp pyserial --break-system-packages
```

Clone this repo:
```bash
git clone https://github.com/allavallc/rp5-edgecrab-config.git /home/pi/arduino-mcp
```

Add to `~/.edgecrab/config.yaml` (see `edgecrab-config-snippet.yaml`):
```yaml
mcp_servers:
  arduino:
    command: python3
    args:
      - /home/pi/arduino-mcp/server.py
```

EdgeCrab launches the MCP server automatically at session start.

---

## 8. Seed EdgeCrab's Memory

Copy the contents of `memory-template.md` into `~/.edgecrab/memories/MEMORY.md`.
This tells EdgeCrab about the Arduino hardware interface and known serial ports.

---

## 9. Enable Camera Vision (optional)

**Important concept:** EC cannot detect attached hardware on its own. It only knows about tools explicitly given to it via MCP. Even if a USB camera appears at `/dev/video0`, EC will not know it exists unless a tool exposes it. This applies to any hardware — cameras, sensors, etc.

Install OpenCV:
```bash
pip3 install opencv-python --break-system-packages
```

The MCP server already includes `capture_image` and `capture_frames` tools — no extra config needed. Plug in any UVC-compatible USB camera and restart EC.

Tested with a Logitech USB webcam on `/dev/video0`.

---

## 10. Verify

Start a new EdgeCrab session:
```bash
edgecrab chat
```

Ask: "what tools do you have available?" — should list the arduino MCP tools.
Ask: "list connected boards" — should call `list_boards` and return the Uno on `/dev/ttyACM0`.
Ask: "capture an image and describe what you see" — should call `capture_image` and analyze the frame.

---

## Visual Analysis Pattern (key for robotics)

The camera is the robot's feedback loop. When verifying a visual condition — "is the LED on?", "is a person present?", "is the robot on grass?" — never rely on a single frame. The correct pattern:

1. Call `capture_frames` over a window of time (3–5 seconds)
2. Analyze each frame with EC's `vision_analyze` tool
3. Look for the condition to hold consistently across multiple frames
4. Only conclude the condition is met when confirmed repeatedly
5. If not confirmed within a timeout, report failure — don't assume

This loop-until-confirmed approach is fundamental to reliable robotics vision.

---

## MCP Tools Available

| Tool | Description |
|------|-------------|
| `list_boards` | Runs `arduino-cli board list` |
| `list_cores` | Lists installed Arduino cores |
| `compile_sketch` | Compiles a sketch given a directory path and FQBN |
| `upload_sketch` | Compiles and uploads to the board |
| `serial_send` | Sends a command over serial, returns response |
| `serial_read` | Reads serial output for N seconds |
| `capture_image` | Grabs a single frame from the USB camera — EC can analyze the image directly |
| `capture_frames` | Captures multiple frames over a set duration — use to detect blinking, motion, or state changes |
