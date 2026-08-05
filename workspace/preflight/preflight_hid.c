#include "ch32fun.h"
#include "rv003usb.h"
#include "usb_config.h"

#include <stdint.h>
#include <string.h>

#define CMD_PING          0x01u
#define CMD_GET_INFO      0x02u
#define CMD_GET_BOARD     0x03u
#define CMD_GET_MCU_ID    0x04u
#define RSP_PONG          0x81u
#define RSP_INFO          0x82u
#define RSP_BOARD         0x83u
#define RSP_MCU_ID        0x84u
#define STATUS_OK         0x01u

#define PROTOCOL_VERSION_MAJOR 1u
#define PROTOCOL_VERSION_MINOR 2u
#define FIRMWARE_VERSION_MAJOR 1u
#define FIRMWARE_VERSION_MINOR 0u
#define FIRMWARE_VERSION_PATCH 2u
#define BOARD_TARGET "UIAPduino Pro Micro CH32V003 V1.4"
#define BOARD_CHUNK_BYTES 5u
#define MCU_ID_ADDRESS 0x1FFFF7E8u
#define MCU_ID_BYTES 8u
#define MCU_ID_CHUNK_BYTES 5u

/*
 * Every Feature Report is exactly 8 bytes including Report ID.
 *
 * PING request: [id,01,nonce0,nonce1,nonce2,nonce3,0,0]
 * PONG reply:   [id,81,nonce0,nonce1,nonce2,nonce3,status,0]
 * INFO request: [id,02,0,0,0,0,0,0]
 * INFO reply:   [id,82,pMaj,pMin,fMaj,fMin,fPat,boardLen]
 * BOARD req:    [id,03,chunk,0,0,0,0,0]
 * BOARD reply:  [id,83,chunk,char0,char1,char2,char3,char4]
 * MCU ID req:   [id,04,chunk,0,0,0,0,0]
 * MCU ID reply: [id,84,chunk,id0,id1,id2,id3,id4]
 *
 * CH32V003 unique device data starts at 0x1FFFF7E8.  The first
 * 8 bytes are the Part UUID shown by minichlink; the following 4 bytes
 * are part-type data and are intentionally not included here.
 */

static volatile uint8_t report_ready;
static uint8_t feature_report[PREFLIGHT_REPORT_TOTAL_SIZE] = { PREFLIGHT_REPORT_ID };

static void response_ping(const uint8_t *request)
{
    uint8_t nonce[4];
    memcpy(nonce, request + 2, sizeof(nonce));
    memset(feature_report, 0, sizeof(feature_report));
    feature_report[0] = PREFLIGHT_REPORT_ID;
    feature_report[1] = RSP_PONG;
    memcpy(feature_report + 2, nonce, sizeof(nonce));
    feature_report[6] = STATUS_OK;
}

static void response_info(void)
{
    const uint8_t board_len = (uint8_t)(sizeof(BOARD_TARGET) - 1u);
    memset(feature_report, 0, sizeof(feature_report));
    feature_report[0] = PREFLIGHT_REPORT_ID;
    feature_report[1] = RSP_INFO;
    feature_report[2] = PROTOCOL_VERSION_MAJOR;
    feature_report[3] = PROTOCOL_VERSION_MINOR;
    feature_report[4] = FIRMWARE_VERSION_MAJOR;
    feature_report[5] = FIRMWARE_VERSION_MINOR;
    feature_report[6] = FIRMWARE_VERSION_PATCH;
    feature_report[7] = board_len;
}

static void response_board(uint8_t chunk)
{
    const char board[] = BOARD_TARGET;
    const uint8_t board_len = (uint8_t)(sizeof(board) - 1u);
    uint16_t offset = (uint16_t)chunk * BOARD_CHUNK_BYTES;
    uint8_t i;

    memset(feature_report, 0, sizeof(feature_report));
    feature_report[0] = PREFLIGHT_REPORT_ID;
    feature_report[1] = RSP_BOARD;
    feature_report[2] = chunk;

    for (i = 0; i < BOARD_CHUNK_BYTES; ++i) {
        uint16_t pos = offset + i;
        if (pos < board_len) {
            feature_report[3 + i] = (uint8_t)board[pos];
        }
    }
}

static void response_mcu_id(uint8_t chunk)
{
    const volatile uint8_t *mcu_id = (const volatile uint8_t *)MCU_ID_ADDRESS;
    uint16_t offset = (uint16_t)chunk * MCU_ID_CHUNK_BYTES;
    uint8_t i;

    memset(feature_report, 0, sizeof(feature_report));
    feature_report[0] = PREFLIGHT_REPORT_ID;
    feature_report[1] = RSP_MCU_ID;
    feature_report[2] = chunk;

    for (i = 0; i < MCU_ID_CHUNK_BYTES; ++i) {
        uint16_t pos = offset + i;
        if (pos < MCU_ID_BYTES) {
            feature_report[3 + i] = mcu_id[pos];
        }
    }
}

int main(void)
{
    SystemInit();
    Delay_Ms(100);
    usb_setup();

    for (;;) {
        if (report_ready) {
            uint8_t request[PREFLIGHT_REPORT_TOTAL_SIZE];
            uint8_t command;

            report_ready = 0;
            memcpy(request, feature_report, sizeof(request));
            command = request[1];

            if (command == CMD_PING) {
                response_ping(request);
            } else if (command == CMD_GET_INFO) {
                response_info();
            } else if (command == CMD_GET_BOARD) {
                response_board(request[2]);
            } else if (command == CMD_GET_MCU_ID) {
                response_mcu_id(request[2]);
            } else {
                memset(feature_report, 0, sizeof(feature_report));
                feature_report[0] = PREFLIGHT_REPORT_ID;
            }
        }
    }
}

void usb_handle_user_in_request(struct usb_endpoint *e,
                                uint8_t *scratchpad,
                                int endp,
                                uint32_t sendtok,
                                struct rv003usb_internal *ist)
{
    (void)e; (void)scratchpad; (void)ist;
    if (endp) usb_send_empty(sendtok);
}

void usb_handle_user_data(struct usb_endpoint *e,
                          int current_endpoint,
                          uint8_t *data,
                          int len,
                          struct rv003usb_internal *ist)
{
    int offset;
    int to_copy;
    (void)current_endpoint; (void)ist;

    offset = e->count << 3;
    to_copy = e->max_len - offset;
    if (to_copy > len) to_copy = len;

    if (to_copy > 0 && offset < (int)sizeof(feature_report)) {
        if (to_copy > (int)sizeof(feature_report) - offset)
            to_copy = (int)sizeof(feature_report) - offset;
        memcpy(feature_report + offset, data, (size_t)to_copy);
    }

    e->count++;
    if ((e->count << 3) >= e->max_len) {
        if (feature_report[0] == PREFLIGHT_REPORT_ID)
            report_ready = 1;
    }
}

void usb_handle_hid_get_report_start(struct usb_endpoint *e,
                                     int reqLen,
                                     uint32_t lValueLSBIndexMSB)
{
    (void)lValueLSBIndexMSB;
    if (reqLen > (int)sizeof(feature_report)) reqLen = sizeof(feature_report);
    e->opaque = feature_report;
    e->max_len = reqLen;
}

void usb_handle_hid_set_report_start(struct usb_endpoint *e,
                                     int reqLen,
                                     uint32_t lValueLSBIndexMSB)
{
    (void)lValueLSBIndexMSB;
    memset(feature_report, 0, sizeof(feature_report));
    if (reqLen > (int)sizeof(feature_report)) reqLen = sizeof(feature_report);
    e->max_len = reqLen;
}
