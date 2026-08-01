#ifndef UIAP_VIBRATION_MOTOR_USB_CONFIG_H
#define UIAP_VIBRATION_MOTOR_USB_CONFIG_H

#define ENDPOINTS 2

#define USB_PORT D
#define USB_PIN_DP 3
#define USB_PIN_DM 4

#define RV003USB_OPTIMIZE_FLASH 1
#define RV003USB_EVENT_DEBUGGING 0
#define RV003USB_HANDLE_IN_REQUEST 1
#define RV003USB_HANDLE_USER_DATA 1
#define RV003USB_HID_FEATURES 1

#define MOTOR_REPORT_ID 0x01
#define MOTOR_REPORT_PAYLOAD_SIZE 1
#define MOTOR_REPORT_TOTAL_SIZE (1 + MOTOR_REPORT_PAYLOAD_SIZE)

#ifndef __ASSEMBLER__

#include <stdint.h>
#include "rv003usb.h"

#ifdef INSTANCE_DESCRIPTORS

#define UIAP_USB_VID 0x1209
#define UIAP_USB_PID 0xD003

static const uint8_t device_descriptor[] = {
    18, 1,
    0x10, 0x01,
    0x00, 0x00, 0x00,
    0x08,
    UIAP_USB_VID & 0xff, UIAP_USB_VID >> 8,
    UIAP_USB_PID & 0xff, UIAP_USB_PID >> 8,
    0x00, 0x01,
    1, 2, 3,
    1
};

/*
 * Vendor-defined Feature Report:
 *   Report ID 1
 *   payload 0..100
 *   0      = OFF
 *   1..100 = vibration level
 */
static const uint8_t special_hid_desc[] = {
    0x06, 0x00, 0xff,
    0x09, 0x01,
    0xa1, 0x01,
    0x85, MOTOR_REPORT_ID,
    0x09, 0x01,
    0x15, 0x00,
    0x25, 0x64,
    0x75, 0x08,
    0x95, MOTOR_REPORT_PAYLOAD_SIZE,
    0xb1, 0x02,
    0xc0
};

static const uint8_t config_descriptor[] = {
    9, 2,
    34, 0,
    1,
    1,
    0,
    0x80,
    100,

    9, 4,
    0,
    0,
    1,
    0x03,
    0x00,
    0x00,
    0,

    9, 0x21,
    0x11, 0x01,
    0x00,
    0x01,
    0x22,
    sizeof(special_hid_desc), 0x00,

    7, 5,
    0x81,
    0x03,
    0x01, 0x00,
    100
};

#define STR_MANUFACTURER u"UIAP Workshop"
#define STR_PRODUCT      u"UIAP Vibration Motor"
#define STR_SERIAL       u"UIAPVMOTOR001"

struct usb_string_descriptor_struct {
    uint8_t bLength;
    uint8_t bDescriptorType;
    uint16_t wString[];
};

static const struct usb_string_descriptor_struct string0 = {
    4, 3, { 0x0409 }
};
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
    { 0x00000100, device_descriptor, sizeof(device_descriptor) },
    { 0x00000200, config_descriptor, sizeof(config_descriptor) },
    { 0x00002200, special_hid_desc, sizeof(special_hid_desc) },
    { 0x00002100, config_descriptor + 18, 9 },
    { 0x00000300, (const uint8_t *)&string0, 4 },
    { 0x04090301, (const uint8_t *)&string1, sizeof(STR_MANUFACTURER) },
    { 0x04090302, (const uint8_t *)&string2, sizeof(STR_PRODUCT) },
    { 0x04090303, (const uint8_t *)&string3, sizeof(STR_SERIAL) }
};

#define DESCRIPTOR_LIST_ENTRIES \
    ((sizeof(descriptor_list)) / (sizeof(struct descriptor_list_struct)))

#endif
#endif
#endif
