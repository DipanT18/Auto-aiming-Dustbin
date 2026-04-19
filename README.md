# Auto-aiming Dustbin

Prototype system that uses a camera to detect thrown objects, predicts trajectory, and aims a motorized bin opening (pan/tilt) via an Arduino.

## Layout

| Path | Purpose |
|------|---------|
| `docs/` | Setup, hardware, calibration, protocol, timeline |
| `firmware/` | Arduino motor sketch |
| `vision/` | Camera, detection, trajectory, serial bridge, entrypoint |
| `tests/` | Pytest suite (mock hardware where possible) |
| `config/` | YAML configuration |
| `calibration/` | Saved transforms (gitignored artifacts) |

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m vision.main --config config/default.yaml --show
```

Use `--no-serial` without hardware attached. Copy `config/default.yaml` to `config/local.yaml` for machine-specific settings.

## Documentation

- [Prototype guide](docs/PROTOTYPE_GUIDE.md)
- [Hardware specs](docs/HARDWARE_SPECS.md)
- [Calibration](docs/CALIBRATION_GUIDE.md)
- [Serial protocol](docs/COMMUNICATION_PROTOCOL.md)

## License

Use and modify for your course project as needed.
