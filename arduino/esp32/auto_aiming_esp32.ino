/*
 * auto_aiming_esp32.ino  –  Auto-Aiming Dustbin – ESP32 variant
 *
 * Differences from the Uno sketch:
 *  • Uses ESP32's LEDC hardware PWM (analogWrite() not available on ESP32).
 *  • GPIO numbers differ — update the #defines below for your board.
 *  • Optional: Wi-Fi task skeleton included but disabled by default.
 *
 * Hardware
 * --------
 * Two L298N dual-channel motor driver boards, four DC motors (omni-wheel
 * X-drive platform).
 *
 * Default GPIO assignments (ESP32-WROOM-32 DevKit):
 *
 *   Motor W1 (front-left):   EN=GPIO32  IN1=GPIO25  IN2=GPIO26
 *   Motor W2 (front-right):  EN=GPIO33  IN1=GPIO27  IN2=GPIO14
 *   Motor W3 (rear-right):   EN=GPIO15  IN1=GPIO12  IN2=GPIO13
 *   Motor W4 (rear-left):    EN=GPIO4   IN1=GPIO16  IN2=GPIO17
 * Serial Protocol  (same as Uno variant — see docs/COMMUNICATION_PROTOCOL.md)
 *   Baud: 115200, USB-serial (UART0 on the DevKit USB connector).
 *   Commands: MOVE <vx> <vy>  |  STOP  |  HOME  |  PING
 *   See arduino/common/protocol.h for the full protocol definition.
 */

#include <Arduino.h>
#include "../common/protocol.h"

// ── LEDC PWM configuration ───────────────────────────────────────────────────
#define PWM_FREQ       5000   // Hz
#define PWM_RESOLUTION    8   // bits (0-255)

// LEDC channels (0-15 available on ESP32)
#define CH_W1 0
#define CH_W2 1
#define CH_W3 2
#define CH_W4 3

// ── Pin assignments ──────────────────────────────────────────────────────────
#define W1_EN  32
#define W1_IN1 25
#define W1_IN2 26

#define W2_EN  33
#define W2_IN1 27
#define W2_IN2 14

#define W3_EN  15
#define W3_IN1 12
#define W3_IN2 13

#define W4_EN   4
#define W4_IN1 16
#define W4_IN2 17

// ── Helpers ──────────────────────────────────────────────────────────────────

void motorWrite(uint8_t ledcCh, uint8_t in1, uint8_t in2, int speed) {
    speed = constrain(speed, -255, 255);
    ledcWrite(ledcCh, (uint32_t)abs(speed));
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

void driveXY(int vx, int vy) {
    int w1 = +vx - vy;
    int w2 = -vx - vy;
    int w3 = -vx + vy;
    int w4 = +vx + vy;

    int maxAbs = max(max(abs(w1), abs(w2)), max(abs(w3), abs(w4)));
    if (maxAbs > 255) {
        w1 = (int)((long)w1 * 255 / maxAbs);
        w2 = (int)((long)w2 * 255 / maxAbs);
        w3 = (int)((long)w3 * 255 / maxAbs);
        w4 = (int)((long)w4 * 255 / maxAbs);
    }

    motorWrite(CH_W1, W1_IN1, W1_IN2, w1);
    motorWrite(CH_W2, W2_IN1, W2_IN2, w2);
    motorWrite(CH_W3, W3_IN1, W3_IN2, w3);
    motorWrite(CH_W4, W4_IN1, W4_IN2, w4);
}

void stopAll() { driveXY(0, 0); }

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
    // Configure LEDC PWM
    ledcSetup(CH_W1, PWM_FREQ, PWM_RESOLUTION);
    ledcSetup(CH_W2, PWM_FREQ, PWM_RESOLUTION);
    ledcSetup(CH_W3, PWM_FREQ, PWM_RESOLUTION);
    ledcSetup(CH_W4, PWM_FREQ, PWM_RESOLUTION);

    ledcAttachPin(W1_EN, CH_W1);
    ledcAttachPin(W2_EN, CH_W2);
    ledcAttachPin(W3_EN, CH_W3);
    ledcAttachPin(W4_EN, CH_W4);

    // Direction pins
    uint8_t dirPins[] = {
        W1_IN1, W1_IN2, W2_IN1, W2_IN2,
        W3_IN1, W3_IN2, W4_IN1, W4_IN2
    };
    for (uint8_t i = 0; i < sizeof(dirPins); i++) {
        pinMode(dirPins[i], OUTPUT);
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
