/*
 * auto_aiming_uno.ino  –  Auto-Aiming Dustbin – Arduino Uno / Mega variant
 *
 * Hardware
 * --------
 * Two L298N dual-channel motor driver boards control four DC motors arranged
 * in an omni-wheel (X-drive) platform.
 *
 * Wiring (default — adjust #defines below to match your board):
 *
 *   Motor Driver A (front wheels)
 *     ENA  → D10 (PWM)    ENB  → D11 (PWM)
 *     IN1  → D2            IN2  → D3   (motor W1, front-left)
 *     IN3  → D4            IN4  → D5   (motor W2, front-right)
 *
 *   Motor Driver B (rear wheels)
 *     ENA  → D6  (PWM)    ENB  → D9  (PWM)
 *     IN1  → D7            IN2  → D8   (motor W3, rear-right)
 *     IN3  → D12           IN4  → D13  (motor W4, rear-left)
 *     Note: Mega users may prefer higher-numbered digital pins (e.g. D22–D25)
 *     to free up D7/D8/D12/D13 for other purposes — update #defines accordingly.
 *
 * Serial Protocol  (see arduino/common/protocol.h and docs/COMMUNICATION_PROTOCOL.md)
 * ---------------
 * Baud: 115200.  All messages are newline-terminated ASCII.
 *
 * Commands from laptop:
 *   MOVE <vx> <vy>  — move platform; vx,vy in -255..255
 *   STOP            — halt all motors
 *   HOME            — stop (no encoder-based homing in this sketch)
 *   PING            — health check
 *
 * Responses:
 *   OK PONG         — reply to PING
 *   OK              — command accepted
 *   ERR PARSE       — command not recognised
 */

#include "../common/protocol.h"

// ── Pin assignments ──────────────────────────────────────────────────────────

// Motor W1 — front-left
#define W1_EN  10
#define W1_IN1  2
#define W1_IN2  3

// Motor W2 — front-right
#define W2_EN  11
#define W2_IN1  4
#define W2_IN2  5

// Motor W3 — rear-right
#define W3_EN   6
#define W3_IN1  7
#define W3_IN2  8

// Motor W4 — rear-left
#define W4_EN   9
#define W4_IN1 12
#define W4_IN2 13

// ── Helpers ──────────────────────────────────────────────────────────────────

void motorWrite(uint8_t enPin, uint8_t in1, uint8_t in2, int speed) {
    // speed: -255 to 255
    speed = constrain(speed, -255, 255);
    analogWrite(enPin, abs(speed));
    if (speed > 0) {
        digitalWrite(in1, HIGH);
        digitalWrite(in2, LOW);
    } else if (speed < 0) {
        digitalWrite(in1, LOW);
        digitalWrite(in2, HIGH);
    } else {
        digitalWrite(in1, LOW);
        digitalWrite(in2, LOW);
    }
}

// X-drive omni mixing: vx = right, vy = forward (both -255..255)
void driveXY(int vx, int vy) {
    int w1 = +vx - vy;   // front-left
    int w2 = -vx - vy;   // front-right
    int w3 = -vx + vy;   // rear-right
    int w4 = +vx + vy;   // rear-left

    // Scale if any value exceeds 255
    int maxAbs = max(max(abs(w1), abs(w2)), max(abs(w3), abs(w4)));
    if (maxAbs > 255) {
        w1 = (int)((long)w1 * 255 / maxAbs);
        w2 = (int)((long)w2 * 255 / maxAbs);
        w3 = (int)((long)w3 * 255 / maxAbs);
        w4 = (int)((long)w4 * 255 / maxAbs);
    }

    motorWrite(W1_EN, W1_IN1, W1_IN2, w1);
    motorWrite(W2_EN, W2_IN1, W2_IN2, w2);
    motorWrite(W3_EN, W3_IN1, W3_IN2, w3);
    motorWrite(W4_EN, W4_IN1, W4_IN2, w4);
}

void stopAll() {
    driveXY(0, 0);
}

// ── Command parser ───────────────────────────────────────────────────────────

char cmdBuf[CMD_BUF_LEN];
uint8_t cmdLen = 0;

void handleCommand(const char* cmd) {
    if (strcmp(cmd, "PING") == 0) {
        Serial.println("OK PONG");

    } else if (strcmp(cmd, "STOP") == 0 || strcmp(cmd, "HOME") == 0) {
        stopAll();
        Serial.println("OK");

    } else if (strncmp(cmd, "MOVE ", 5) == 0) {
        int vx = 0, vy = 0;
        if (sscanf(cmd + 5, "%d %d", &vx, &vy) == 2) {
            driveXY(vx, vy);
            Serial.println("OK");
        } else {
            Serial.println("ERR PARSE");
        }

    } else {
        Serial.println("ERR PARSE");
    }
}

// ── Arduino lifecycle ────────────────────────────────────────────────────────

void setup() {
    // Motor pins
    uint8_t pins[] = {
        W1_EN, W1_IN1, W1_IN2,
        W2_EN, W2_IN1, W2_IN2,
        W3_EN, W3_IN1, W3_IN2,
        W4_EN, W4_IN1, W4_IN2
    };
    for (uint8_t i = 0; i < sizeof(pins); i++) {
        pinMode(pins[i], OUTPUT);
    }
    stopAll();
    Serial.begin(SERIAL_BAUD);
}

void loop() {
    while (Serial.available()) {
        char c = (char)Serial.read();
        if (c == '\n' || c == '\r') {
            if (cmdLen > 0) {
                cmdBuf[cmdLen] = '\0';
                handleCommand(cmdBuf);
                cmdLen = 0;
            }
        } else if (cmdLen < CMD_BUF_LEN - 1) {
            cmdBuf[cmdLen++] = c;
        }
    }
}
