# EdgeCrab Memory Template for Arduino

Paste into ~/.edgecrab/memories/MEMORY.md

---

MCP Server:
- An MCP server is running at /home/YOUR_USERNAME/arduino-mcp/server.py
- It exposes 8 tools in the mcp-arduino toolset: list_boards, list_cores, compile_sketch, upload_sketch, serial_send, serial_read, capture_image, capture_frames
- Always prefer these MCP tools over running arduino-cli or python scripts directly
- capture_image: captures a single frame from the USB camera at /dev/video0 — use to visually verify hardware state (e.g. is LED on?)
- capture_frames: captures multiple frames over a duration — use to detect blinking, motion, or state changes

Arduino Hardware Interface:
- /dev/ttyAMA10 is the Pi's built-in GPIO UART — always present, always shows as "Unknown" in board list, not a connected device, ignore it.
- arduino-cli location: /home/YOUR_USERNAME/bin/arduino-cli (or wherever installed)
- To discover connected boards: `arduino-cli board list`
- To list installed cores: `arduino-cli core list`
- To search/install a core: `arduino-cli core search <name>`, `arduino-cli core install arduino:avr`
- Always run `arduino-cli board list` first to confirm port and FQBN before compiling or uploading
- Default baud: 9600

Uploading a sketch:
  arduino-cli compile --fqbn arduino:avr:uno <sketch_dir>
  arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:avr:uno <sketch_dir>

Serial communication (use instead of interactive arduino-cli monitor):
  python3 /path/to/arduino-mcp/server.py  # via MCP tools, not direct invocation
