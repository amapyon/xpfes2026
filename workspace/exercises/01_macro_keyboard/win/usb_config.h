#ifndef UIAP_MACRO_USB_CONFIG_H
#define UIAP_MACRO_USB_CONFIG_H

#define ENDPOINTS 2
#define USB_PORT D
#define USB_PIN_DP 3
#define USB_PIN_DM 4

#define RV003USB_OPTIMIZE_FLASH 1
#define RV003USB_EVENT_DEBUGGING 0
#define RV003USB_HANDLE_IN_REQUEST 1
#define RV003USB_OTHER_CONTROL 1
#define RV003USB_HANDLE_USER_DATA 1
#define RV003USB_HID_FEATURES 0
#define RV003USB_SUPPORT_CONTROL_OUT 0
#define RV003USB_USE_REBOOT_FEATURE_REPORT 0

#ifndef __ASSEMBLER__
#include <stdint.h>
#ifdef INSTANCE_DESCRIPTORS

#define UIAP_USB_VID 0x1209
#define UIAP_USB_PID 0xC003

static const uint8_t device_descriptor[] = {
    18, 1, 0x10, 0x01,
    0x00, 0x00, 0x00, 0x08,
    UIAP_USB_VID & 0xff, UIAP_USB_VID >> 8,
    UIAP_USB_PID & 0xff, UIAP_USB_PID >> 8,
    0x00, 0x01,
    1, 2, 3, 1
};

static const uint8_t keyboard_hid_desc[] = {
    0x05, 0x01,       /* Usage Page (Generic Desktop) */
    0x09, 0x06,       /* Usage (Keyboard) */
    0xA1, 0x01,       /* Collection (Application) */
    0x05, 0x07,       /* Usage Page (Keyboard) */
    0x19, 0xE0,       /* Usage Minimum (Left Control) */
    0x29, 0xE7,       /* Usage Maximum (Right GUI) */
    0x15, 0x00,
    0x25, 0x01,
    0x75, 0x01,
    0x95, 0x08,
    0x81, 0x02,       /* Input (Data, Variable, Absolute) */
    0x95, 0x01,
    0x75, 0x08,
    0x81, 0x03,       /* Reserved */
    0x95, 0x05,
    0x75, 0x01,
    0x05, 0x08,       /* Usage Page (LEDs) */
    0x19, 0x01,
    0x29, 0x05,
    0x91, 0x02,
    0x95, 0x01,
    0x75, 0x03,
    0x91, 0x03,
    0x95, 0x06,
    0x75, 0x08,
    0x15, 0x00,
    0x25, 0x65,
    0x05, 0x07,
    0x19, 0x00,
    0x29, 0x65,
    0x81, 0x00,
    0xC0
};

static const uint8_t config_descriptor[] = {
    9, 2, 34, 0, 1, 1, 0, 0x80, 50,
    9, 4, 0, 0, 1, 0x03, 0x01, 0x01, 0,
    9, 0x21, 0x11, 0x01, 0, 1, 0x22, sizeof(keyboard_hid_desc), 0,
    7, 5, 0x81, 0x03, 8, 0, 10
};

#define STR_MANUFACTURER u"UIAP Workshop"
#define STR_PRODUCT      u"UIAP Macro Keyboard"
#define STR_SERIAL       u"TEST3-001"

struct usb_string_descriptor_struct {
    uint8_t bLength;
    uint8_t bDescriptorType;
    uint16_t wString[];
};
static const struct usb_string_descriptor_struct string0 = { 4, 3, { 0x0409 } };
static const struct usb_string_descriptor_struct string1 = { sizeof(STR_MANUFACTURER), 3, STR_MANUFACTURER };
static const struct usb_string_descriptor_struct string2 = { sizeof(STR_PRODUCT), 3, STR_PRODUCT };
static const struct usb_string_descriptor_struct string3 = { sizeof(STR_SERIAL), 3, STR_SERIAL };

static const struct descriptor_list_struct {
    uint32_t lIndexValue;
    const uint8_t *addr;
    uint8_t length;
} descriptor_list[] = {
    { 0x00000100, device_descriptor, sizeof(device_descriptor) },
    { 0x00000200, config_descriptor, sizeof(config_descriptor) },
    { 0x00002200, keyboard_hid_desc, sizeof(keyboard_hid_desc) },
    { 0x00002100, config_descriptor + 18, 9 },
    { 0x00000300, (const uint8_t *)&string0, 4 },
    { 0x04090301, (const uint8_t *)&string1, sizeof(STR_MANUFACTURER) },
    { 0x04090302, (const uint8_t *)&string2, sizeof(STR_PRODUCT) },
    { 0x04090303, (const uint8_t *)&string3, sizeof(STR_SERIAL) }
};
#define DESCRIPTOR_LIST_ENTRIES (sizeof(descriptor_list) / sizeof(descriptor_list[0]))
#endif
#endif
#endif
