#ifndef _USB_CONFIG_H
#define _USB_CONFIG_H

/* EP0 plus one interrupt-IN endpoint required by the HID interface. */
#define ENDPOINTS 2

/* UIAPduino Pro Micro CH32V003 V1.4 USB wiring. */
#define USB_PORT D
#define USB_PIN_DP 3
#define USB_PIN_DM 4
/* The board provides the low-speed D- pull-up in hardware. */

#define RV003USB_OPTIMIZE_FLASH 1
#define RV003USB_EVENT_DEBUGGING 0
#define RV003USB_HANDLE_IN_REQUEST 1
#define RV003USB_HANDLE_USER_DATA 1
#define RV003USB_HID_FEATURES 1
#define RV003USB_OTHER_CONTROL 1

#define LED_REPORT_ID 0x01
#define LED_COUNT 8
#define LED_REPORT_PAYLOAD_SIZE (LED_COUNT * 3)
#define LED_REPORT_TOTAL_SIZE (1 + LED_REPORT_PAYLOAD_SIZE)

#ifndef __ASSEMBLER__

#include <stdint.h>
#include "rv003usb.h"

#ifdef INSTANCE_DESCRIPTORS

/*
 * Temporary proof-of-concept IDs only.
 * Do not use these as public/product VID:PID assignments.
 */
#define UIAP_USB_VID 0x1209
#define UIAP_USB_PID 0xD008

static const uint8_t device_descriptor[] = {
    18,                 /* bLength */
    1,                  /* bDescriptorType: Device */
    0x10, 0x01,         /* bcdUSB 1.10 */
    0x00,               /* bDeviceClass */
    0x00,               /* bDeviceSubClass */
    0x00,               /* bDeviceProtocol */
    0x08,               /* bMaxPacketSize0: USB low-speed requires 8 */
    UIAP_USB_VID & 0xff, UIAP_USB_VID >> 8,
    UIAP_USB_PID & 0xff, UIAP_USB_PID >> 8,
    0x00, 0x01,         /* bcdDevice 1.00 */
    1,                  /* iManufacturer */
    2,                  /* iProduct */
    3,                  /* iSerialNumber */
    1                   /* bNumConfigurations */
};

/*
 * Vendor-defined HID Feature Report:
 *   Report ID 1
 *   payload = eight RGB triples, LED 1 through LED 8
 *   byte order in the USB report is RGB; firmware converts to WS2812 GRB.
 */
static const uint8_t special_hid_desc[] = {
    0x06, 0x00, 0xff,   /* Usage Page (Vendor-defined 0xFF00) */
    0x09, 0x08,         /* Usage 8 */
    0xa1, 0x01,         /* Collection (Application) */
    0x85, LED_REPORT_ID,
    0x09, 0x08,         /* Usage 8 */
    0x15, 0x00,         /* Logical Minimum 0 */
    0x26, 0xff, 0x00,   /* Logical Maximum 255 */
    0x75, 0x08,         /* Report Size 8 */
    0x95, LED_REPORT_PAYLOAD_SIZE,
    0xb1, 0x02,         /* Feature (Data, Variable, Absolute) */
    0xc0                /* End Collection */
};

static const uint8_t config_descriptor[] = {
    /* Configuration descriptor */
    9, 2,
    34, 0,             /* wTotalLength */
    1,                 /* bNumInterfaces */
    1,                 /* bConfigurationValue */
    0,                 /* iConfiguration */
    0x80,              /* bus powered */
    250,               /* bMaxPower: 500 mA */

    /* HID interface descriptor */
    9, 4,
    0,                 /* bInterfaceNumber */
    0,                 /* bAlternateSetting */
    1,                 /* bNumEndpoints */
    0x03,              /* HID class */
    0x00,              /* no boot subclass */
    0x00,              /* no keyboard/mouse protocol */
    0,                 /* iInterface */

    /* HID class descriptor */
    9, 0x21,
    0x11, 0x01,        /* HID 1.11 */
    0x00,              /* country code */
    0x01,              /* one subordinate descriptor */
    0x22,              /* report descriptor */
    sizeof(special_hid_desc), 0x00,

    /* Interrupt IN endpoint. Feature Reports use EP0 control transfers. */
    7, 5,
    0x81,              /* endpoint 1 IN */
    0x03,              /* interrupt */
    0x01, 0x00,        /* one byte */
    100                /* polling interval, endpoint unused */
};

#define STR_MANUFACTURER u"UIAP Workshop"
#define STR_PRODUCT      u"UIAP WS2812B8 PoC"
#define STR_SERIAL       u"UIAPLED8POC01"

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

#endif /* INSTANCE_DESCRIPTORS */
#endif /* __ASSEMBLER__ */
#endif /* _USB_CONFIG_H */
