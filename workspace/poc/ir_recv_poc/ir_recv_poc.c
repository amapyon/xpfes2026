#include "ch32fun.h"
#include "rv003usb.h"
#include "usb_config.h"

#include <stdint.h>

/* PART-08 OUT -> UIAPduino D12/A3 / CH32V003 PD2 / TIM1_CH1. */
#define IR_PIN PD2

#define PROTOCOL_NONE         0u
#define PROTOCOL_NEC          1u
#define PROTOCOL_NEC_EXTENDED 2u
#define PROTOCOL_NEC_REPEAT   3u
#define PROTOCOL_TOSHIBA_AC   0x20u
#define TOSHIBA_MAX_BYTES     10u

enum decode_state {
    WAIT_LEADER_MARK = 0,
    WAIT_LEADER_SPACE,
    WAIT_BIT_MARK,
    WAIT_BIT_SPACE,
    WAIT_FINAL_MARK,
    WAIT_REPEAT_MARK,
    WAIT_TOSHIBA_LEADER_SPACE,
    WAIT_TOSHIBA_BIT_MARK,
    WAIT_TOSHIBA_BIT_SPACE,
    WAIT_TOSHIBA_FINAL_MARK
};

static volatile enum decode_state state = WAIT_LEADER_MARK;
static volatile uint32_t nec_data;
static volatile uint32_t last_nec_data;
static volatile uint8_t toshiba_data[TOSHIBA_MAX_BYTES];
static volatile uint8_t toshiba_expected_bytes;
static volatile uint8_t event_protocol;
static volatile uint8_t event_length;
static volatile uint8_t event_data[TOSHIBA_MAX_BYTES];
static volatile uint16_t last_mark_us;
static volatile uint16_t last_space_us;
static volatile uint16_t max_mark_us;
static volatile uint16_t max_space_us;
static volatile uint16_t last_capture_us;
static volatile uint8_t capture_initialized;
static volatile uint16_t edge_count;
static volatile uint8_t decode_errors;
static volatile uint8_t reject_reason;
static volatile uint8_t reject_state;
static volatile uint16_t reject_duration_us;
static volatile uint8_t bit_index;
static volatile uint8_t max_bit_index;
static volatile uint8_t sequence;
static volatile uint8_t hid_report[IR_REPORT_SIZE];

static int duration_in_range(uint16_t duration_us, uint16_t min_us, uint16_t max_us)
{
    return duration_us >= min_us && duration_us <= max_us;
}

static void reset_decoder(void)
{
    state = WAIT_LEADER_MARK;
    bit_index = 0;
    nec_data = 0;
}

static void start_toshiba_frame(void)
{
    uint8_t i;
    for (i = 0; i < TOSHIBA_MAX_BYTES; ++i) toshiba_data[i] = 0u;
    toshiba_expected_bytes = 0u;
    bit_index = 0u;
    state = WAIT_TOSHIBA_LEADER_SPACE;
}

static void reject_frame(uint8_t reason, uint16_t duration_us)
{
    reject_reason = reason;
    reject_state = (uint8_t)state;
    reject_duration_us = duration_us;
    if (decode_errors != 0xffu) decode_errors++;
    reset_decoder();
}

static void publish_code(uint8_t protocol, uint32_t data)
{
    uint8_t next_sequence = (uint8_t)(sequence + 1u);
    uint8_t b0 = (uint8_t)data;
    uint8_t b1 = (uint8_t)(data >> 8);
    uint8_t b2 = (uint8_t)(data >> 16);
    uint8_t b3 = (uint8_t)(data >> 24);

    hid_report[0] = next_sequence;
    hid_report[1] = protocol;
    /* Bytes 2..5 preserve the NEC transmission byte order. */
    hid_report[2] = b0;
    hid_report[3] = b1;
    hid_report[4] = b2;
    hid_report[5] = b3;
    hid_report[6] = (uint8_t)(((uint8_t)(b0 ^ b1) == 0xffu ? 1u : 0u) |
                              ((uint8_t)(b2 ^ b3) == 0xffu ? 2u : 0u));
    hid_report[7] = 32u;
    event_protocol = protocol;
    event_length = 4u;
    sequence = next_sequence;
}

static uint8_t toshiba_frame_is_valid(uint8_t length)
{
    uint8_t i;
    uint8_t checksum = 0u;

    if (length != 7u && length != 9u && length != 10u) return 0u;
    if ((uint8_t)(toshiba_data[0] ^ toshiba_data[1]) != 0xffu) return 0u;
    if ((uint8_t)(toshiba_data[2] ^ toshiba_data[3]) != 0xffu) return 0u;
    for (i = 0; i < (uint8_t)(length - 1u); ++i) checksum ^= toshiba_data[i];
    return checksum == toshiba_data[length - 1u];
}

static void publish_toshiba_frame(uint8_t length)
{
    uint8_t i;
    for (i = 0; i < length; ++i) event_data[i] = toshiba_data[i];
    event_protocol = PROTOCOL_TOSHIBA_AC;
    event_length = length;
    sequence++;
}

static void process_rising_edge(uint16_t duration_us)
{
    last_mark_us = duration_us;
    if (duration_us > max_mark_us) max_mark_us = duration_us;

    /* A leader mark always resynchronizes an incomplete or damaged frame. */
    if (duration_in_range(duration_us, 8000, 10000)) {
        nec_data = 0u;
        bit_index = 0u;
        state = WAIT_LEADER_SPACE;
        return;
    }

    /* Toshiba A/C leader mark. The payload length is encoded in byte 2. */
    if (duration_in_range(duration_us, 3800, 5000)) {
        start_toshiba_frame();
        return;
    }

    /* A rising edge completes an active-Low mark. */
    if (state == WAIT_LEADER_MARK) {
        return;
    } else if (state == WAIT_BIT_MARK) {
        if (duration_in_range(duration_us, 350, 800)) {
            state = WAIT_BIT_SPACE;
        } else {
            reject_frame(1u, duration_us);
        }
    } else if (state == WAIT_FINAL_MARK) {
        if (duration_in_range(duration_us, 350, 800)) {
            uint8_t a = (uint8_t)nec_data;
            uint8_t ai = (uint8_t)(nec_data >> 8);
            uint8_t c = (uint8_t)(nec_data >> 16);
            uint8_t ci = (uint8_t)(nec_data >> 24);
            if ((uint8_t)(c ^ ci) == 0xffu) {
                uint8_t p = ((uint8_t)(a ^ ai) == 0xffu) ?
                            PROTOCOL_NEC : PROTOCOL_NEC_EXTENDED;
                last_nec_data = nec_data;
                publish_code(p, nec_data);
            } else {
                reject_frame(5u, duration_us);
                return;
            }
        }
        reset_decoder();
    } else if (state == WAIT_REPEAT_MARK) {
        if (duration_in_range(duration_us, 350, 800) && last_nec_data != 0u) {
            publish_code(PROTOCOL_NEC_REPEAT, last_nec_data);
        }
        reset_decoder();
    } else if (state == WAIT_TOSHIBA_BIT_MARK) {
        if (duration_in_range(duration_us, 350, 850)) {
            state = WAIT_TOSHIBA_BIT_SPACE;
        } else {
            reject_frame(7u, duration_us);
        }
    } else if (state == WAIT_TOSHIBA_FINAL_MARK) {
        if (duration_in_range(duration_us, 350, 850) &&
            toshiba_frame_is_valid(toshiba_expected_bytes)) {
            publish_toshiba_frame(toshiba_expected_bytes);
            reset_decoder();
        } else {
            reject_frame(10u, duration_us);
        }
    } else {
        reject_frame(4u, duration_us);
    }
}

static void process_falling_edge(uint16_t duration_us)
{
    last_space_us = duration_us;
    /* Ignore the arbitrary idle interval before a new leader mark. */
    if (state != WAIT_LEADER_MARK && duration_us > max_space_us) {
        max_space_us = duration_us;
    }

    /* A falling edge starts a mark and completes the preceding space. */
    if (state == WAIT_LEADER_MARK) {
        nec_data = 0;
        bit_index = 0;
    } else if (state == WAIT_LEADER_SPACE) {
        if (duration_in_range(duration_us, 3800, 5200)) {
            nec_data = 0;
            bit_index = 0;
            state = WAIT_BIT_MARK;
        } else if (duration_in_range(duration_us, 1800, 2800)) {
            state = WAIT_REPEAT_MARK;
        } else {
            reject_frame(2u, duration_us);
        }
    } else if (state == WAIT_BIT_SPACE) {
        if (duration_in_range(duration_us, 350, 900)) {
            /* Zero bit: leave the bit clear. */
        } else if (duration_in_range(duration_us, 1300, 2100)) {
            nec_data |= (uint32_t)1u << bit_index;
        } else {
            reject_frame(3u, duration_us);
            return;
        }

        bit_index++;
        if (bit_index > max_bit_index) max_bit_index = bit_index;
        state = (bit_index == 32u) ? WAIT_FINAL_MARK : WAIT_BIT_MARK;
    } else if (state == WAIT_TOSHIBA_LEADER_SPACE) {
        if (duration_in_range(duration_us, 3500, 5000)) {
            state = WAIT_TOSHIBA_BIT_MARK;
        } else {
            reject_frame(6u, duration_us);
        }
    } else if (state == WAIT_TOSHIBA_BIT_SPACE) {
        if (duration_in_range(duration_us, 250, 900)) {
            /* Zero bit. */
        } else if (duration_in_range(duration_us, 1100, 2100)) {
            /* Toshiba A/C transmits the most-significant bit of each byte first. */
            toshiba_data[bit_index >> 3] |=
                (uint8_t)(1u << (7u - (bit_index & 7u)));
        } else {
            reject_frame(8u, duration_us);
            return;
        }

        bit_index++;
        if (bit_index > max_bit_index) max_bit_index = bit_index;
        if (bit_index == 32u) {
            uint8_t length = (uint8_t)((toshiba_data[2] & 0x0fu) + 6u);
            if (length != 7u && length != 9u && length != 10u) {
                reject_frame(9u, duration_us);
                return;
            }
            if ((uint8_t)(toshiba_data[0] ^ toshiba_data[1]) != 0xffu ||
                (uint8_t)(toshiba_data[2] ^ toshiba_data[3]) != 0xffu) {
                reject_frame(9u, duration_us);
                return;
            }
            toshiba_expected_bytes = length;
        }
        state = (toshiba_expected_bytes != 0u &&
                 bit_index == (uint8_t)(toshiba_expected_bytes * 8u)) ?
                WAIT_TOSHIBA_FINAL_MARK : WAIT_TOSHIBA_BIT_MARK;
    } else {
        reject_frame(4u, duration_us);
    }
}

static void process_capture(uint8_t level_high, uint16_t captured_us)
{
    uint16_t duration_us;

    edge_count++;
    if (!capture_initialized) {
        capture_initialized = 1u;
        last_capture_us = captured_us;
        if (!level_high) process_falling_edge(0u);
        return;
    }

    duration_us = (uint16_t)(captured_us - last_capture_us);
    last_capture_us = captured_us;
    if (level_high) {
        process_rising_edge(duration_us);
    } else {
        process_falling_edge(duration_us);
    }
}

void TIM1_CC_IRQHandler(void) __attribute__((interrupt));
void TIM1_CC_IRQHandler(void)
{
    uint16_t flags = (uint16_t)TIM1->INTFR;
    uint8_t have_falling = (flags & TIM_CC1IF) != 0u;
    uint8_t have_rising = (flags & TIM_CC2IF) != 0u;
    uint16_t falling_us = (uint16_t)TIM1->CH1CVR;
    uint16_t rising_us = (uint16_t)TIM1->CH2CVR;

    /* If both captures waited behind USB, replay them in chronological order. */
    if (have_falling && have_rising) {
        uint16_t to_falling = (uint16_t)(falling_us - last_capture_us);
        uint16_t to_rising = (uint16_t)(rising_us - last_capture_us);
        if (to_falling < to_rising) {
            process_capture(0u, falling_us);
            process_capture(1u, rising_us);
        } else {
            process_capture(1u, rising_us);
            process_capture(0u, falling_us);
        }
    } else {
        if (have_rising) process_capture(1u, rising_us);
        if (have_falling) process_capture(0u, falling_us);
    }

    TIM1->INTFR = ~(TIM_CC1IF | TIM_CC2IF);
}

void usb_handle_user_in_request(struct usb_endpoint *e, uint8_t *scratchpad,
                                int endp, uint32_t sendtok,
                                struct rv003usb_internal *ist)
{
    static uint8_t snapshot[IR_REPORT_SIZE];
    static uint8_t sent_sequence;
    static uint8_t diagnostic_page;
    static uint8_t diagnostic_divider;
    static uint8_t packet_sequence;
    static uint8_t fragment_index;
    uint8_t i;
    (void)e;
    (void)scratchpad;
    (void)ist;

    if (endp == 1) {
        if (sent_sequence != sequence) {
            if (packet_sequence != sequence) {
                packet_sequence = sequence;
                fragment_index = 0u;
            }
            if (event_protocol == PROTOCOL_TOSHIBA_AC) {
                uint8_t offset = (uint8_t)(fragment_index * 4u);
                snapshot[0] = packet_sequence;
                snapshot[1] = PROTOCOL_TOSHIBA_AC;
                snapshot[2] = fragment_index;
                snapshot[3] = event_length;
                for (i = 0; i < 4u; ++i) {
                    snapshot[4u + i] = (offset + i < event_length) ?
                                       event_data[offset + i] : 0u;
                }
                fragment_index++;
                if ((uint8_t)(fragment_index * 4u) >= event_length) {
                    sent_sequence = packet_sequence;
                }
            } else {
                for (i = 0; i < IR_REPORT_SIZE; ++i) snapshot[i] = hid_report[i];
                sent_sequence = packet_sequence;
            }
        } else if (++diagnostic_divider >= 33u) {
            uint16_t edges = edge_count;
            diagnostic_divider = 0u;
            diagnostic_page++;
            snapshot[0] = (uint8_t)edges;
            if ((diagnostic_page % 4u) == 0u) {
                snapshot[1] = 0x10u;
                snapshot[2] = (GPIOD->INDR & (1u << 2)) ? 1u : 0u;
                snapshot[3] = (uint8_t)state;
                snapshot[4] = (uint8_t)edges;
                snapshot[5] = (uint8_t)(edges >> 8);
                snapshot[6] = decode_errors;
                snapshot[7] = max_bit_index;
            } else if ((diagnostic_page % 4u) == 1u) {
                uint16_t mark = last_mark_us;
                uint16_t space = last_space_us;
                snapshot[1] = 0x11u;
                snapshot[2] = (uint8_t)mark;
                snapshot[3] = (uint8_t)(mark >> 8);
                snapshot[4] = (uint8_t)space;
                snapshot[5] = (uint8_t)(space >> 8);
                snapshot[6] = 0u;
                snapshot[7] = 0u;
            } else if ((diagnostic_page % 4u) == 2u) {
                uint16_t mark = max_mark_us;
                uint16_t space = max_space_us;
                snapshot[1] = 0x12u;
                snapshot[2] = (uint8_t)mark;
                snapshot[3] = (uint8_t)(mark >> 8);
                snapshot[4] = (uint8_t)space;
                snapshot[5] = (uint8_t)(space >> 8);
                snapshot[6] = 0u;
                snapshot[7] = 0u;
            } else {
                uint16_t duration = reject_duration_us;
                snapshot[1] = 0x13u;
                snapshot[2] = reject_reason;
                snapshot[3] = reject_state;
                snapshot[4] = (uint8_t)duration;
                snapshot[5] = (uint8_t)(duration >> 8);
                snapshot[6] = max_bit_index;
                snapshot[7] = decode_errors;
            }
        } else {
            usb_send_empty(sendtok);
            return;
        }
        usb_send_data(snapshot, IR_REPORT_SIZE, 0, sendtok);
    } else {
        usb_send_empty(sendtok);
    }
}

void usb_handle_other_control_message(struct usb_endpoint *e,
                                      struct usb_urb *s,
                                      struct rv003usb_internal *ist)
{
    (void)e;
    (void)s;
    (void)ist;
}

static void setup_ir_interrupt(void)
{
    funPinMode(IR_PIN, GPIO_CFGLR_IN_PUPD);
    funDigitalWrite(IR_PIN, FUN_HIGH);

    RCC->APB2PCENR |= RCC_APB2Periph_GPIOD | RCC_APB2Periph_TIM1;
    RCC->APB2PRSTR |= RCC_APB2Periph_TIM1;
    RCC->APB2PRSTR &= ~RCC_APB2Periph_TIM1;

    /* 48 MHz / 48 = 1 us per count; free-running capture preserves both edges. */
    TIM1->PSC = 47u;
    TIM1->ATRLR = 0xffffu;
    TIM1->CNT = 0u;
    TIM1->CHCTLR1 = TIM_CC1S_0 | TIM_CC2S_1; /* CH1 direct TI1, CH2 indirect TI1 */
    TIM1->CCER = TIM_CC1E | TIM_CC1P | TIM_CC2E; /* CH1 falling, CH2 rising */
    TIM1->SMCFGR = 0u;
    TIM1->DMAINTENR = TIM_CC1IE | TIM_CC2IE;
    TIM1->SWEVGR = TIM_UG;
    TIM1->INTFR = 0u;
    NVIC_EnableIRQ(TIM1_CC_IRQn);
    TIM1->CTLR1 = TIM_CEN;
}

int main(void)
{
    SystemInit();
    funGpioInitAll();
    Delay_Ms(10);
    usb_setup();
    setup_ir_interrupt();

    for (;;) { }
}
