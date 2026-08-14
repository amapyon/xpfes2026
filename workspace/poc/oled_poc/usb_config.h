#ifndef UIAP_OLED_USB_CONFIG_H
#define UIAP_OLED_USB_CONFIG_H

#define ENDPOINTS 2

/* UIAPduino Pro Micro CH32V003 V1.4 USB wiring. */
#define USB_PORT D
#define USB_PIN_DP 3
#define USB_PIN_DM 4
#define USB_PIN_DPU 5

#define RV003USB_OPTIMIZE_FLASH 1
#define RV003USB_EVENT_DEBUGGING 0
#define RV003USB_HANDLE_IN_REQUEST 1
#define RV003USB_HANDLE_USER_DATA 1
#define RV003USB_HID_FEATURES 1
#define RV003USB_OTHER_CONTROL 1

#define OLED_REPORT_ID 0x01
/*
 * Keep the Feature Report at the 25-byte size already proven by the
 * ws2812b8_hid_poc on Windows. Longer text is split by the host program.
 */
#define OLED_REPORT_PAYLOAD_SIZE 24
#define OLED_REPORT_TOTAL_SIZE 25

#ifndef __ASSEMBLER__
#include <stdint.h>
#include "rv003usb.h"

#ifdef INSTANCE_DESCRIPTORS

/* Temporary PoC IDs. They are not a public product VID/PID assignment. */
#define UIAP_USB_VID 0x1209
#define UIAP_USB_PID 0xD009

static const uint8_t device_descriptor[] = {
    18, 1, 0x10, 0x01, 0x00, 0x00, 0x00, 0x08,
    UIAP_USB_VID & 0xff, UIAP_USB_VID >> 8,
    UIAP_USB_PID & 0xff, UIAP_USB_PID >> 8,
    0x02, 0x01, 1, 2, 3, 1 /* bcdDevice 1.02: filled shape commands */
};

static const uint8_t oled_hid_desc[] = {
    0x06, 0x00, 0xff, 0x09, 0x09, 0xa1, 0x01,
    0x85, OLED_REPORT_ID,
    0x09, 0x09, 0x15, 0x00, 0x26, 0xff, 0x00,
    0x75, 0x08, 0x95, OLED_REPORT_PAYLOAD_SIZE,
    0xb1, 0x02, 0xc0
};

static const uint8_t config_descriptor[] = {
    9, 2, 34, 0, 1, 1, 0, 0x80, 50,
    9, 4, 0, 0, 1, 0x03, 0x00, 0x00, 0,
    9, 0x21, 0x11, 0x01, 0x00, 0x01, 0x22,
    sizeof(oled_hid_desc), 0x00,
    7, 5, 0x81, 0x03, 0x01, 0x00, 100
};

#define STR_MANUFACTURER u"UIAP Workshop"
#define STR_PRODUCT      u"UIAP OLED PoC"
#define STR_SERIAL       u"OLED-POC-001"

struct usb_string_descriptor_struct {
    uint8_t bLength;
    uint8_t bDescriptorType;
    uint16_t wString[];
};

static const struct usb_string_descriptor_struct string0 = {4, 3, {0x0409}};
static const struct usb_string_descriptor_struct string1 = {
    sizeof(STR_MANUFACTURER), 3, STR_MANUFACTURER
};
static const struct usb_string_descriptor_struct string2 = {
    sizeof(STR_PRODUCT), 3, STR_PRODUCT
};
static const struct usb_string_descriptor_struct string3 = {
    sizeof(STR_SERIAL), 3, STR_SERIAL
};

static const struct descriptor_list_struct {
    uint32_t lIndexValue;
    const uint8_t *addr;
    uint8_t length;
} descriptor_list[] = {
    {0x00000100, device_descriptor, sizeof(device_descriptor)},
    {0x00000200, config_descriptor, sizeof(config_descriptor)},
    {0x00002200, oled_hid_desc, sizeof(oled_hid_desc)},
    {0x00002100, config_descriptor + 18, 9},
    {0x00000300, (const uint8_t *)&string0, 4},
    {0x04090301, (const uint8_t *)&string1, sizeof(STR_MANUFACTURER)},
    {0x04090302, (const uint8_t *)&string2, sizeof(STR_PRODUCT)},
    {0x04090303, (const uint8_t *)&string3, sizeof(STR_SERIAL)}
};

#define DESCRIPTOR_LIST_ENTRIES \
    (sizeof(descriptor_list) / sizeof(struct descriptor_list_struct))

#endif
#endif
#endif
