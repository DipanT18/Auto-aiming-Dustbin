# Serial communication protocol

Host (Python) talks to Arduino over USB serial at **115200 baud** by default (configurable).

## Line-oriented text

Each message is a single line terminated by `\n` (LF). ASCII only.

### Commands (host → Arduino)

| Command | Meaning |
|---------|---------|
| `P <steps>` | Pan: signed integer step count (or µs offset for servo builds—see firmware) |
| `T <steps>` | Tilt: signed integer |
| `HOME` | Move to a defined home pose (if implemented in firmware) |
| `STOP` | Halt motion / disable drivers if supported |
| `PING` | Health check |

### Responses (Arduino → host)

| Prefix | Meaning |
|--------|---------|
| `OK` | Command accepted |
| `ERR <code>` | Error (e.g. `ERR BOUNDS`) |
| `POS <p> <t>` | Optional telemetry: current pan/tilt |

## Binary mode (optional extension)

For high rates, a fixed-length binary frame can replace text; the reference sketch uses text for simplicity and debuggability.

## Configuration

Mirror settings in:

- `firmware/arduino_motor_control.ino` (`Serial.begin(...)`)
- `config/default.yaml` under `serial`
