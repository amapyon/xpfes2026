#include "ch32fun.h"
#include "rv003usb.h"
#include "usb_config.h"

#include <stdint.h>
#include <string.h>

/* bmRequestType is stored in the low byte and bRequest in the high byte. */
#define HID_REQ_GET_IDLE 0x02A1u
#define HID_REQ_SET_IDLE 0x0A21u

/*
 * ch32fun's WS2812 DMA/SPI driver uses SPI1 MOSI on PC6 for CH32V003.
 * On UIAPduino Pro Micro CH32V003 V1.4, PC6 is D8 / MOSI.
 *
 * Interrupt nesting is enabled because USB (rv003usb) and the DMA refill ISR
 * must coexist. This is also the arrangement used by rv003usb's HIDAPI demo.
 */
/*
 * DMALEDS is the driver's ring-buffer sizing parameter, not the physical LED
 * count. In non-WSRAW mode the buffer holds DMALEDS / 2 WS2812 "LED-time"
 * slots. The stream also needs leading reset slots and trailing low time.
 *
 * With DMALEDS=16 the first buffer held only:
 *   reset x2 + LED1..LED6
 * which matched the initial hardware failure (LED7/8 never received a valid
 * frame, and latch behavior at the truncated tail was unstable).
 *
 * DMALEDS=32 provides 16 slots = reset x2 + all 8 LEDs + 6 spare low slots,
 * while consuming only 192 bytes for the DMA buffer in this non-WSRAW mode.
 */
#define DMALEDS 32
#define WS2812B_ALLOW_INTERRUPT_NESTING
#define WS2812DMA_IMPLEMENTATION
#include "ws2812b_dma_spi_led_driver.h"

static volatile uint8_t report_ready;
static uint8_t feature_report[LED_REPORT_TOTAL_SIZE] = { LED_REPORT_ID };
static uint8_t led_rgb[LED_REPORT_PAYLOAD_SIZE];
static uint8_t idle_rate;

/*
 * The DMA driver emits the callback's 24 bits in byte order.
 * WS2812B expects GRB, while the host protocol intentionally stays RGB.
 */
uint32_t WS2812BLEDCallback(int ledno)
{
    int base;
    uint8_t r;
    uint8_t g;
    uint8_t b;

    if (ledno < 0 || ledno >= LED_COUNT) {
        return 0;
    }

    base = ledno * 3;
    r = led_rgb[base + 0];
    g = led_rgb[base + 1];
    b = led_rgb[base + 2];

    return ((uint32_t)g << 16) | ((uint32_t)r << 8) | (uint32_t)b;
}

static void sync_feature_report_from_leds(void)
{
    feature_report[0] = LED_REPORT_ID;
    memcpy(feature_report + 1, led_rgb, sizeof(led_rgb));
}

static void apply_feature_report(void)
{
    memcpy(led_rgb, feature_report + 1, sizeof(led_rgb));
    sync_feature_report_from_leds();
    WS2812BDMAStart(LED_COUNT);
}

int main(void)
{
    SystemInit();
    funGpioInitAll();

    memset(led_rgb, 0, sizeof(led_rgb));
    sync_feature_report_from_leds();

    WS2812BDMAInit();
    WS2812BDMAStart(LED_COUNT);

    /* Clean disconnect interval after reset / bootloader exit. */
    Delay_Ms(100);
    usb_setup();

    for (;;) {
        if (report_ready) {
            report_ready = 0;
            apply_feature_report();
        }
    }
}

void usb_handle_user_in_request(struct usb_endpoint *e,
                                uint8_t *scratchpad,
                                int endp,
                                uint32_t sendtok,
                                struct rv003usb_internal *ist)
{
    (void)e;
    (void)scratchpad;
    (void)ist;

    /* Endpoint 1 is declared for HID but unused; Feature Reports use EP0. */
    if (endp) {
        usb_send_empty(sendtok);
    }
}

/* macOS IOHIDFamily may query HID idle state while attaching the device. */
void usb_handle_other_control_message(struct usb_endpoint *e,
                                      struct usb_urb *s,
                                      struct rv003usb_internal *ist)
{
    uint16_t request = s->wRequestTypeLSBRequestMSB;
    uint16_t value = (uint16_t)(s->lValueLSBIndexMSB & 0xffffu);
    uint16_t length = s->wLength;
    (void)ist;

    switch (request) {
    case HID_REQ_GET_IDLE:
        e->opaque = &idle_rate;
        e->max_len = (length < 1u) ? length : 1u;
        break;
    case HID_REQ_SET_IDLE:
        idle_rate = (uint8_t)(value >> 8);
        break;
    default:
        break;
    }
}

void usb_handle_user_data(struct usb_endpoint *e,
                          int current_endpoint,
                          uint8_t *data,
                          int len,
                          struct rv003usb_internal *ist)
{
    int offset;
    int to_copy;

    (void)current_endpoint;
    (void)ist;

    offset = e->count << 3;
    to_copy = e->max_len - offset;
    if (to_copy > len) {
        to_copy = len;
    }

    if (to_copy > 0 && offset < (int)sizeof(feature_report)) {
        if (to_copy > (int)sizeof(feature_report) - offset) {
            to_copy = (int)sizeof(feature_report) - offset;
        }
        memcpy(feature_report + offset, data, (size_t)to_copy);
    }

    e->count++;
    if ((e->count << 3) >= e->max_len) {
        if (e->max_len == (int)sizeof(feature_report) &&
            feature_report[0] == LED_REPORT_ID) {
            report_ready = 1;
        }
    }
}

void usb_handle_hid_get_report_start(struct usb_endpoint *e,
                                     int reqLen,
                                     uint32_t lValueLSBIndexMSB)
{
    (void)lValueLSBIndexMSB;

    sync_feature_report_from_leds();
    if (reqLen > (int)sizeof(feature_report)) {
        reqLen = sizeof(feature_report);
    }
    e->opaque = feature_report;
    e->max_len = reqLen;
}

void usb_handle_hid_set_report_start(struct usb_endpoint *e,
                                     int reqLen,
                                     uint32_t lValueLSBIndexMSB)
{
    (void)lValueLSBIndexMSB;

    if (reqLen > (int)sizeof(feature_report)) {
        reqLen = sizeof(feature_report);
    }

    memset(feature_report, 0, sizeof(feature_report));
    e->max_len = reqLen;
}
