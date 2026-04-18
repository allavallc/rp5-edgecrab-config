# EdgeCrab Memory Template for Arduino

Paste into ~/.edgecrab/memories/MEMORY.md

---

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
