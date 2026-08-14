#include "ch32fun.h"
#include "rv003usb.h"
#include "usb_config.h"

#include <stdint.h>
#include <string.h>

#define OLED_WIDTH 128u
#define OLED_HEIGHT 64u
#define OLED_BUFFER_SIZE (OLED_WIDTH * OLED_HEIGHT / 8u)

/* PART-09 SCK is I2C SCL, not SPI clock. */
#define I2C_SDA_PIN 1u /* UIAPduino D3 / PC1 */
#define I2C_SCL_PIN 2u /* UIAPduino D4 / PC2 */
#define I2C_DELAY_US 3u

#define CMD_OUTPUT 1u
#define CMD_CLEAR 2u
#define CMD_FILL 3u
#define CMD_TEXT 4u
#define CMD_LINE 5u
#define CMD_RECT 6u
#define CMD_CIRCLE 7u
#define CMD_DEMO 8u
#define CMD_PROBE 9u

#define STATUS_IDLE 0u
#define STATUS_OK 1u
#define STATUS_BAD_COMMAND 2u
#define STATUS_BAD_ARGUMENT 3u
#define STATUS_OLED_NOT_FOUND 4u
#define STATUS_I2C_ERROR 5u

#define HID_REQ_GET_IDLE 0x02A1u
#define HID_REQ_SET_IDLE 0x0A21u

static uint8_t framebuffer[OLED_BUFFER_SIZE];
static uint8_t feature_report[OLED_REPORT_TOTAL_SIZE] = {OLED_REPORT_ID};
static uint8_t status_report[OLED_REPORT_TOTAL_SIZE] = {OLED_REPORT_ID};
static volatile uint8_t report_ready;
static uint8_t idle_rate;
static uint8_t last_status = STATUS_IDLE;
static uint8_t last_command;
static uint8_t last_sequence;
static uint8_t oled_address;

/*
 * Classic fixed 5x7 ASCII font, columns left-to-right, bit 0 at the top.
 * Derived from the Adafruit GFX classic font (BSD-licensed); only 0x20..0x7e
 * is retained. Bit 7 is masked when drawing so every glyph is exactly 7 high.
 */
static const uint8_t font5x7[] = {
    0x00,0x00,0x00,0x00,0x00, 0x00,0x00,0x5f,0x00,0x00,
    0x00,0x07,0x00,0x07,0x00, 0x14,0x7f,0x14,0x7f,0x14,
    0x24,0x2a,0x7f,0x2a,0x12, 0x23,0x13,0x08,0x64,0x62,
    0x36,0x49,0x56,0x20,0x50, 0x00,0x08,0x07,0x03,0x00,
    0x00,0x1c,0x22,0x41,0x00, 0x00,0x41,0x22,0x1c,0x00,
    0x2a,0x1c,0x7f,0x1c,0x2a, 0x08,0x08,0x3e,0x08,0x08,
    0x00,0x80,0x70,0x30,0x00, 0x08,0x08,0x08,0x08,0x08,
    0x00,0x00,0x60,0x60,0x00, 0x20,0x10,0x08,0x04,0x02,
    0x3e,0x51,0x49,0x45,0x3e, 0x00,0x42,0x7f,0x40,0x00,
    0x72,0x49,0x49,0x49,0x46, 0x21,0x41,0x49,0x4d,0x33,
    0x18,0x14,0x12,0x7f,0x10, 0x27,0x45,0x45,0x45,0x39,
    0x3c,0x4a,0x49,0x49,0x31, 0x41,0x21,0x11,0x09,0x07,
    0x36,0x49,0x49,0x49,0x36, 0x46,0x49,0x49,0x29,0x1e,
    0x00,0x00,0x14,0x00,0x00, 0x00,0x40,0x34,0x00,0x00,
    0x00,0x08,0x14,0x22,0x41, 0x14,0x14,0x14,0x14,0x14,
    0x00,0x41,0x22,0x14,0x08, 0x02,0x01,0x59,0x09,0x06,
    0x3e,0x41,0x5d,0x59,0x4e, 0x7c,0x12,0x11,0x12,0x7c,
    0x7f,0x49,0x49,0x49,0x36, 0x3e,0x41,0x41,0x41,0x22,
    0x7f,0x41,0x41,0x41,0x3e, 0x7f,0x49,0x49,0x49,0x41,
    0x7f,0x09,0x09,0x09,0x01, 0x3e,0x41,0x41,0x51,0x73,
    0x7f,0x08,0x08,0x08,0x7f, 0x00,0x41,0x7f,0x41,0x00,
    0x20,0x40,0x41,0x3f,0x01, 0x7f,0x08,0x14,0x22,0x41,
    0x7f,0x40,0x40,0x40,0x40, 0x7f,0x02,0x1c,0x02,0x7f,
    0x7f,0x04,0x08,0x10,0x7f, 0x3e,0x41,0x41,0x41,0x3e,
    0x7f,0x09,0x09,0x09,0x06, 0x3e,0x41,0x51,0x21,0x5e,
    0x7f,0x09,0x19,0x29,0x46, 0x26,0x49,0x49,0x49,0x32,
    0x03,0x01,0x7f,0x01,0x03, 0x3f,0x40,0x40,0x40,0x3f,
    0x1f,0x20,0x40,0x20,0x1f, 0x3f,0x40,0x38,0x40,0x3f,
    0x63,0x14,0x08,0x14,0x63, 0x03,0x04,0x78,0x04,0x03,
    0x61,0x59,0x49,0x4d,0x43, 0x00,0x7f,0x41,0x41,0x41,
    0x02,0x04,0x08,0x10,0x20, 0x00,0x41,0x41,0x41,0x7f,
    0x04,0x02,0x01,0x02,0x04, 0x40,0x40,0x40,0x40,0x40,
    0x00,0x03,0x07,0x08,0x00, 0x20,0x54,0x54,0x78,0x40,
    0x7f,0x28,0x44,0x44,0x38, 0x38,0x44,0x44,0x44,0x28,
    0x38,0x44,0x44,0x28,0x7f, 0x38,0x54,0x54,0x54,0x18,
    0x00,0x08,0x7e,0x09,0x02, 0x18,0xa4,0xa4,0x9c,0x78,
    0x7f,0x08,0x04,0x04,0x78, 0x00,0x44,0x7d,0x40,0x00,
    0x20,0x40,0x40,0x3d,0x00, 0x7f,0x10,0x28,0x44,0x00,
    0x00,0x41,0x7f,0x40,0x00, 0x7c,0x04,0x78,0x04,0x78,
    0x7c,0x08,0x04,0x04,0x78, 0x38,0x44,0x44,0x44,0x38,
    0xfc,0x18,0x24,0x24,0x18, 0x18,0x24,0x24,0x18,0xfc,
    0x7c,0x08,0x04,0x04,0x08, 0x48,0x54,0x54,0x54,0x24,
    0x04,0x04,0x3f,0x44,0x24, 0x3c,0x40,0x40,0x20,0x7c,
    0x1c,0x20,0x40,0x20,0x1c, 0x3c,0x40,0x30,0x40,0x3c,
    0x44,0x28,0x10,0x28,0x44, 0x4c,0x90,0x90,0x90,0x7c,
    0x44,0x64,0x54,0x4c,0x44, 0x00,0x08,0x36,0x41,0x00,
    0x00,0x00,0x77,0x00,0x00, 0x00,0x41,0x36,0x08,0x00,
    0x02,0x01,0x02,0x04,0x02
};

static void i2c_delay(void) { Delay_Us(I2C_DELAY_US); }
static void sda_high(void) { GPIOC->BSHR = 1u << I2C_SDA_PIN; }
static void sda_low(void) { GPIOC->BCR = 1u << I2C_SDA_PIN; }
static void scl_high(void) { GPIOC->BSHR = 1u << I2C_SCL_PIN; }
static void scl_low(void) { GPIOC->BCR = 1u << I2C_SCL_PIN; }

static void i2c_init(void)
{
    uint32_t mask = (0x0fu << (I2C_SDA_PIN * 4u)) |
                    (0x0fu << (I2C_SCL_PIN * 4u));
    RCC->APB2PCENR |= RCC_APB2Periph_GPIOC;
    GPIOC->CFGLR &= ~mask;
    GPIOC->CFGLR |= (GPIO_Speed_10MHz | GPIO_CNF_OUT_OD) << (I2C_SDA_PIN * 4u);
    GPIOC->CFGLR |= (GPIO_Speed_10MHz | GPIO_CNF_OUT_OD) << (I2C_SCL_PIN * 4u);
    sda_high();
    scl_high();
}

static void i2c_start(void)
{
    sda_high(); scl_high(); i2c_delay();
    sda_low(); i2c_delay(); scl_low();
}

static void i2c_stop(void)
{
    sda_low(); i2c_delay(); scl_high(); i2c_delay(); sda_high(); i2c_delay();
}

static uint8_t i2c_write(uint8_t value)
{
    uint8_t mask;
    uint8_t ack;
    for (mask = 0x80u; mask; mask >>= 1u) {
        if (value & mask) sda_high(); else sda_low();
        i2c_delay(); scl_high(); i2c_delay(); scl_low();
    }
    sda_high(); i2c_delay(); scl_high(); i2c_delay();
    ack = (GPIOC->INDR & (1u << I2C_SDA_PIN)) ? 0u : 1u;
    scl_low();
    return ack;
}

static uint8_t i2c_begin(uint8_t address, uint8_t control)
{
    i2c_start();
    if (!i2c_write((uint8_t)(address << 1)) || !i2c_write(control)) {
        i2c_stop();
        return 0u;
    }
    return 1u;
}

static uint8_t oled_command(uint8_t command)
{
    if (!i2c_begin(oled_address, 0x00u)) return 0u;
    if (!i2c_write(command)) { i2c_stop(); return 0u; }
    i2c_stop();
    return 1u;
}

static uint8_t oled_probe(void)
{
    static const uint8_t candidates[] = {0x3cu, 0x3du, 0x78u, 0x7au};
    uint8_t i;
    for (i = 0u; i < sizeof(candidates); ++i) {
        i2c_start();
        if (i2c_write((uint8_t)(candidates[i] << 1))) {
            i2c_stop();
            oled_address = candidates[i];
            return 1u;
        }
        i2c_stop();
    }
    oled_address = 0u;
    return 0u;
}

static uint8_t oled_init(void)
{
    static const uint8_t commands[] = {
        0xae, 0xd5, 0x80, 0xa8, 0x3f, 0xd3, 0x00, 0x40,
        0x8d, 0x14, 0x20, 0x00, 0xa1, 0xc8, 0xda, 0x12,
        0x81, 0x7f, 0xd9, 0xf1, 0xdb, 0x40, 0xa4, 0xa6,
        0xaf
    };
    uint8_t i;
    if (!oled_probe()) return 0u;
    for (i = 0u; i < sizeof(commands); ++i)
        if (!oled_command(commands[i])) return 0u;
    return 1u;
}

static uint8_t oled_output(void)
{
    uint16_t i;
    if (!oled_address && !oled_init()) return 0u;
    if (!oled_command(0x21u) || !oled_command(0x00u) ||
        !oled_command(0x7fu) || !oled_command(0x22u) ||
        !oled_command(0x00u) || !oled_command(0x07u)) return 0u;
    if (!i2c_begin(oled_address, 0x40u)) return 0u;
    for (i = 0u; i < OLED_BUFFER_SIZE; ++i) {
        if (!i2c_write(framebuffer[i])) { i2c_stop(); return 0u; }
    }
    i2c_stop();
    return 1u;
}

static void pixel(int16_t x, int16_t y, uint8_t on)
{
    uint16_t index;
    uint8_t mask;
    if (x < 0 || x >= (int16_t)OLED_WIDTH || y < 0 || y >= (int16_t)OLED_HEIGHT)
        return;
    index = (uint16_t)x + ((uint16_t)y >> 3) * OLED_WIDTH;
    mask = (uint8_t)(1u << ((uint8_t)y & 7u));
    if (on) framebuffer[index] |= mask;
    else framebuffer[index] &= (uint8_t)~mask;
}

static void line(int16_t x0, int16_t y0, int16_t x1, int16_t y1)
{
    int16_t dx = x1 > x0 ? x1 - x0 : x0 - x1;
    int16_t sx = x0 < x1 ? 1 : -1;
    int16_t dy_abs = y1 > y0 ? y1 - y0 : y0 - y1;
    int16_t dy = (int16_t)-dy_abs;
    int16_t sy = y0 < y1 ? 1 : -1;
    int16_t err = dx + dy;
    for (;;) {
        pixel(x0, y0, 1u);
        if (x0 == x1 && y0 == y1) break;
        if ((int16_t)(2 * err) >= dy) { err += dy; x0 += sx; }
        if ((int16_t)(2 * err) <= dx) { err += dx; y0 += sy; }
    }
}

static void horizontal_line(int16_t x0, int16_t x1, int16_t y)
{
    int16_t x;
    if (x0 > x1) {
        int16_t swap = x0;
        x0 = x1;
        x1 = swap;
    }
    for (x = x0; x <= x1; ++x) pixel(x, y, 1u);
}

static void rectangle(uint8_t x0, uint8_t y0, uint8_t x1, uint8_t y1,
                      uint8_t filled)
{
    uint8_t y;
    if (filled) {
        for (y = y0; y <= y1; ++y) horizontal_line(x0, x1, y);
        return;
    }
    line(x0, y0, x1, y0); line(x1, y0, x1, y1);
    line(x1, y1, x0, y1); line(x0, y1, x0, y0);
}

static void circle(int16_t cx, int16_t cy, int16_t radius, uint8_t filled)
{
    int16_t x = radius;
    int16_t y = 0;
    int16_t err = 1 - radius;
    while (x >= y) {
        if (filled) {
            horizontal_line(cx - x, cx + x, cy + y);
            horizontal_line(cx - x, cx + x, cy - y);
            horizontal_line(cx - y, cx + y, cy + x);
            horizontal_line(cx - y, cx + y, cy - x);
        } else {
            pixel(cx + x, cy + y, 1u); pixel(cx + y, cy + x, 1u);
            pixel(cx - y, cy + x, 1u); pixel(cx - x, cy + y, 1u);
            pixel(cx - x, cy - y, 1u); pixel(cx - y, cy - x, 1u);
            pixel(cx + y, cy - x, 1u); pixel(cx + x, cy - y, 1u);
        }
        ++y;
        if (err < 0) err += (int16_t)(2 * y + 1);
        else { --x; err += (int16_t)(2 * (y - x) + 1); }
    }
}

static void character(uint8_t x, uint8_t y, uint8_t code)
{
    uint8_t col;
    uint8_t row;
    for (col = 0u; col < 5u; ++col) {
        uint8_t bits = (code >= 0x20u && code <= 0x7eu) ?
            (uint8_t)(font5x7[(uint16_t)(code - 0x20u) * 5u + col] & 0x7fu) : 0x7fu;
        for (row = 0u; row < 7u; ++row)
            pixel((int16_t)x + col, (int16_t)y + row, (uint8_t)(bits & (1u << row)));
    }
    /* The required one-pixel inter-character gap is explicitly cleared. */
    for (row = 0u; row < 7u; ++row) pixel((int16_t)x + 5, (int16_t)y + row, 0u);
    /* Keep the eighth pixel row empty so adjacent text-cell rows stay separate. */
    for (col = 0u; col < 6u; ++col) pixel((int16_t)x + col, (int16_t)y + 7, 0u);
}

static void text(uint8_t x, uint8_t y, const uint8_t *bytes, uint8_t length)
{
    uint8_t i;
    for (i = 0u; i < length; ++i) {
        /* Do not render a partial glyph at the right edge. */
        if ((uint16_t)x + (uint16_t)i * 6u + 4u >= OLED_WIDTH) break;
        character((uint8_t)(x + i * 6u), y, bytes[i]);
    }
}

static uint8_t arguments_are_points(const uint8_t *r)
{
    return r[3] < OLED_WIDTH && r[5] < OLED_WIDTH &&
           r[4] < OLED_HEIGHT && r[6] < OLED_HEIGHT;
}

static uint8_t process_command(void)
{
    uint8_t command = feature_report[1];
    uint8_t ok = 1u;
    last_command = command;
    last_sequence = feature_report[2];

    switch (command) {
    case CMD_OUTPUT:
        if (!oled_output()) return oled_address ? STATUS_I2C_ERROR : STATUS_OLED_NOT_FOUND;
        break;
    case CMD_CLEAR:
        memset(framebuffer, 0, sizeof(framebuffer));
        break;
    case CMD_FILL:
        memset(framebuffer, 0xff, sizeof(framebuffer));
        break;
    case CMD_TEXT:
        if (feature_report[3] > 20u || feature_report[4] > 7u ||
            feature_report[5] > 19u) ok = 0u;
        else text((uint8_t)(feature_report[3] * 6u),
                  (uint8_t)(feature_report[4] * 8u),
                  feature_report + 6, feature_report[5]);
        break;
    case CMD_LINE:
        if (!arguments_are_points(feature_report)) ok = 0u;
        else line(feature_report[3], feature_report[4], feature_report[5], feature_report[6]);
        break;
    case CMD_RECT:
        if (!arguments_are_points(feature_report) || feature_report[3] > feature_report[5] ||
            feature_report[4] > feature_report[6] || feature_report[7] > 1u) ok = 0u;
        else rectangle(feature_report[3], feature_report[4], feature_report[5],
                       feature_report[6], feature_report[7]);
        break;
    case CMD_CIRCLE:
        if (feature_report[3] >= OLED_WIDTH || feature_report[4] >= OLED_HEIGHT ||
            feature_report[5] > 127u || feature_report[6] > 1u) ok = 0u;
        else circle(feature_report[3], feature_report[4], feature_report[5],
                    feature_report[6]);
        break;
    case CMD_DEMO:
        memset(framebuffer, 0, sizeof(framebuffer));
        /* Full-screen frame also verifies every pixel on the four edges. */
        rectangle(0u, 0u, 127u, 63u, 0u);
        text(8u, 5u, (const uint8_t *)"UIAP OLED PoC", 13u);
        line(8, 18, 119, 18);
        circle(32, 40, 13, 0u);
        rectangle(55u, 27u, 78u, 53u, 0u);
        line(91, 53, 117, 27);
        if (!oled_output()) return oled_address ? STATUS_I2C_ERROR : STATUS_OLED_NOT_FOUND;
        break;
    case CMD_PROBE:
        if (!oled_init()) return STATUS_OLED_NOT_FOUND;
        break;
    default:
        return STATUS_BAD_COMMAND;
    }
    return ok ? STATUS_OK : STATUS_BAD_ARGUMENT;
}

int main(void)
{
    SystemInit();
    funGpioInitAll();
    i2c_init();
    memset(framebuffer, 0, sizeof(framebuffer));
    Delay_Ms(100);
    usb_setup();
    for (;;) {
        if (report_ready) {
            report_ready = 0u;
            last_status = process_command();
        }
    }
}

void usb_handle_user_in_request(struct usb_endpoint *e, uint8_t *scratchpad,
                                int endp, uint32_t sendtok,
                                struct rv003usb_internal *ist)
{
    (void)e; (void)scratchpad; (void)ist;
    if (endp) usb_send_empty(sendtok);
}

void usb_handle_other_control_message(struct usb_endpoint *e, struct usb_urb *s,
                                      struct rv003usb_internal *ist)
{
    uint16_t request = s->wRequestTypeLSBRequestMSB;
    uint16_t value = (uint16_t)(s->lValueLSBIndexMSB & 0xffffu);
    uint16_t length = s->wLength;
    (void)ist;
    if (request == HID_REQ_GET_IDLE) {
        e->opaque = &idle_rate;
        e->max_len = length < 1u ? length : 1u;
    } else if (request == HID_REQ_SET_IDLE) {
        idle_rate = (uint8_t)(value >> 8);
    }
}

void usb_handle_user_data(struct usb_endpoint *e, int current_endpoint,
                          uint8_t *data, int len,
                          struct rv003usb_internal *ist)
{
    int offset = e->count << 3;
    int to_copy = e->max_len - offset;
    (void)current_endpoint; (void)ist;
    if (to_copy > len) to_copy = len;
    if (to_copy > 0 && offset < (int)sizeof(feature_report)) {
        if (to_copy > (int)sizeof(feature_report) - offset)
            to_copy = (int)sizeof(feature_report) - offset;
        memcpy(feature_report + offset, data, (size_t)to_copy);
    }
    e->count++;
    if ((e->count << 3) >= e->max_len &&
        e->max_len == (int)sizeof(feature_report) &&
        feature_report[0] == OLED_REPORT_ID) report_ready = 1u;
}

void usb_handle_hid_get_report_start(struct usb_endpoint *e, int req_len,
                                     uint32_t value)
{
    (void)value;
    memset(status_report, 0, sizeof(status_report));
    status_report[0] = OLED_REPORT_ID;
    status_report[1] = last_status;
    status_report[2] = last_command;
    status_report[3] = last_sequence;
    status_report[4] = oled_address;
    status_report[5] = oled_address ? 1u : 0u;
    if (req_len > (int)sizeof(status_report)) req_len = sizeof(status_report);
    e->opaque = status_report;
    e->max_len = req_len;
}

void usb_handle_hid_set_report_start(struct usb_endpoint *e, int req_len,
                                     uint32_t value)
{
    uint8_t report_id = (uint8_t)(value & 0xffu);
    if (report_id != OLED_REPORT_ID) req_len = 0;
    if (req_len > (int)sizeof(feature_report)) req_len = sizeof(feature_report);
    memset(feature_report, 0, sizeof(feature_report));
    e->max_len = req_len;
}
