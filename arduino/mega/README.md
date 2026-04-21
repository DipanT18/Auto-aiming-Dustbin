# Arduino Mega — Placeholder

Firmware for the Arduino Mega target is not yet implemented.

When ready, add the sketch here as:

```
arduino/mega/auto_aiming_mega.ino
```

## Notes

- The Mega has more PWM pins and SRAM than the Uno, making it a good choice
  if you need extra sensors or more complex control logic.
- The serial protocol is identical to the Uno variant — see
  `arduino/common/protocol.h` and `arduino/uno/auto_aiming_uno.ino` as
  a reference implementation.
- Prefer higher-numbered digital pins (e.g. D22–D25) for direction signals
  to free D2–D13 for PWM-capable uses.
