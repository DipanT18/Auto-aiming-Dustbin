/*
 * protocol.h — Serial protocol constants shared between Python (Pi) and Arduino firmware
 *
 * All messages are newline-terminated ASCII at 115200 baud.
 *
 * Commands (Pi → Arduino):
 *   MOVE <vx> <vy>   Drive platform; vx, vy are signed integers in -255..255
 *   STOP             Halt all motors immediately
 *   HOME             Return to origin (STOP in current firmware)
 *   PING             Health check
 *
 * Responses (Arduino → Pi):
 *   OK PONG          Reply to PING
 *   OK               Command accepted
 *   ERR PARSE        Command not recognised
 */

#ifndef PROTOCOL_H
#define PROTOCOL_H

#define SERIAL_BAUD       115200
#define CMD_BUF_LEN       64

// Command strings
#define CMD_PING          "PING"
#define CMD_STOP          "STOP"
#define CMD_HOME          "HOME"
#define CMD_MOVE_PREFIX   "MOVE "

// Response strings
#define RESP_PONG         "OK PONG"
#define RESP_OK           "OK"
#define RESP_ERR_PARSE    "ERR PARSE"

// PWM range
#define PWM_MIN   -255
#define PWM_MAX    255

#endif // PROTOCOL_H
