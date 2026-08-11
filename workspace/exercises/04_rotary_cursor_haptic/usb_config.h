#ifndef UIAP_ENCODER_USB_CONFIG_H
#define UIAP_ENCODER_USB_CONFIG_H

#include "funconfig.h"

#define ENDPOINTS 2
#define USB_PORT D
#define USB_PIN_DP 3
#define USB_PIN_DM 4
#define USB_PIN_DPU 5
#define RV003USB_OPTIMIZE_FLASH 1
#define RV003USB_HANDLE_IN_REQUEST 1
#define RV003USB_OTHER_CONTROL 1
#define RV003USB_HANDLE_USER_DATA 1
#define RV003USB_HID_FEATURES 1
#define RV003USB_USE_REBOOT_FEATURE_REPORT 0

#define ENCODER_REPORT_ID 0x01
#define HAPTIC_REPORT_ID 0x02
#include "haptic_pattern_protocol.h"
#define HAPTIC_REPORT_PAYLOAD_SIZE HAPTIC_PATTERN_PAYLOAD_SIZE
#define HAPTIC_REPORT_TOTAL_SIZE HAPTIC_PATTERN_TOTAL_SIZE

#ifndef __ASSEMBLER__
#include <stdint.h>
#ifdef INSTANCE_DESCRIPTORS

static const uint8_t device_descriptor[] = {
    18, 0x01, 0x10, 0x01,
    0x00, 0x00, 0x00, 0x08,
    0x09, 0x12, 0x05, 0xC0,
    0x13, 0x00, 1, 2, 3, 1
};

static const uint8_t encoder_hid_desc[] = {
    0x06, 0x00, 0xFF,
    0x09, 0x01,
    0xA1, 0x01,
    0x85, ENCODER_REPORT_ID,
    0x15, 0x00,
    0x26, 0xFF, 0x00,
    0x75, 0x08,
    0x95, 0x02,
    0x09, 0x01,
    0x81, 0x02,
    0x85, HAPTIC_REPORT_ID,
    0x15, 0x00,
    0x26, 0xFF, 0x00,
    0x75, 0x08,
    0x95, HAPTIC_REPORT_PAYLOAD_SIZE,
    0x09, 0x02,
    0xB1, 0x02,
    0xC0
};

static const uint8_t config_descriptor[] = {
    9, 0x02, 0x22, 0x00, 1, 1, 0, 0x80, 0x32,
    9, 0x04, 0, 0, 1, 0x03, 0x00, 0x00, 0,
    9, 0x21, 0x11, 0x01, 0, 1, 0x22, sizeof(encoder_hid_desc), 0,
    7, 0x05, 0x81, 0x03, 0x03, 0x00, 10
};

#define STR_MANUFACTURER u"UIAP Workshop"
#define STR_PRODUCT u"UIAP Rotary Haptic"
#define STR_SERIAL u"TEST8-001"

struct usb_string_descriptor_struct {
    uint8_t bLength;
    uint8_t bDescriptorType;
    uint16_t wString[];
};
static const struct usb_string_descriptor_struct string0 = {4, 3, {0x0409}};
static const struct usb_string_descriptor_struct string1 = {sizeof(STR_MANUFACTURER), 3, STR_MANUFACTURER};
static const struct usb_string_descriptor_struct string2 = {sizeof(STR_PRODUCT), 3, STR_PRODUCT};
static const struct usb_string_descriptor_struct string3 = {sizeof(STR_SERIAL), 3, STR_SERIAL};

static const struct descriptor_list_struct {
    uint32_t lIndexValue;
    const uint8_t *addr;
    uint8_t length;
} descriptor_list[] = {
    {0x00000100, device_descriptor, sizeof(device_descriptor)},
    {0x00000200, config_descriptor, sizeof(config_descriptor)},
    {0x00002200, encoder_hid_desc, sizeof(encoder_hid_desc)},
    {0x00002100, config_descriptor + 18, 9},
    {0x00000300, (const uint8_t *)&string0, 4},
    {0x04090301, (const uint8_t *)&string1, sizeof(STR_MANUFACTURER)},
    {0x04090302, (const uint8_t *)&string2, sizeof(STR_PRODUCT)},
    {0x04090303, (const uint8_t *)&string3, sizeof(STR_SERIAL)}
};
#define DESCRIPTOR_LIST_ENTRIES (sizeof(descriptor_list) / sizeof(descriptor_list[0]))
#endif
#endif
#endif
