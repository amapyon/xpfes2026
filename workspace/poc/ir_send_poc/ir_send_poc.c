#include "ch32fun.h"
#include "rv003usb.h"
#include "usb_config.h"

#include <stdint.h>
#include <string.h>

/* UIAPduino D6/A2 = CH32V003 PC4 = TIM1_CH4. */
#define IR_GPIO_BIT          4u
#define IR_TIMER_PERIOD      1263u /* 48MHz / 1263 = 38.005kHz */
#define IR_TIMER_DUTY        632u  /* 50% duty, matching Toshiba reference */

#define CMD_NONE             0u
#define CMD_SEND_TOSHIBA     1u
#define STATUS_IDLE          0u
#define STATUS_OK            1u
#define STATUS_BAD_COMMAND   2u
#define STATUS_BAD_FRAME     3u

#define TOSHIBA_HEADER_MARK  4400u
#define TOSHIBA_HEADER_SPACE 4300u
#define TOSHIBA_BIT_MARK      580u
#define TOSHIBA_ONE_SPACE    1600u
#define TOSHIBA_ZERO_SPACE    490u
#define TOSHIBA_GAP          7400u

#define HID_REQ_GET_IDLE     0x02A1u
#define HID_REQ_SET_IDLE     0x0A21u

static volatile uint8_t report_ready;
static volatile uint8_t pending_command;
static volatile uint8_t pending_length;
static volatile uint8_t pending_count;
static volatile uint8_t pending_data[IR_SEND_DATA_SIZE];
static uint8_t idle_rate;
static uint8_t last_status = STATUS_IDLE;
static uint8_t last_length;
static uint8_t last_count;
static uint8_t feature_report[IR_SEND_REPORT_TOTAL_SIZE] = {
    IR_SEND_REPORT_ID, CMD_NONE, 0, 0
};

static void ir_carrier_init(void)
{
    RCC->APB2PCENR |= RCC_APB2Periph_GPIOC | RCC_APB2Periph_TIM1;

    /* Fail-safe: the external low-side switch is initially OFF. */
    GPIOC->BCR = 1u << IR_GPIO_BIT;
    GPIOC->CFGLR &= ~(0x0fu << (IR_GPIO_BIT * 4u));
    GPIOC->CFGLR |=
        (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP) << (IR_GPIO_BIT * 4u);

    RCC->APB2PRSTR |= RCC_APB2Periph_TIM1;
    RCC->APB2PRSTR &= ~RCC_APB2Periph_TIM1;

    TIM1->PSC = 0u;
    TIM1->ATRLR = IR_TIMER_PERIOD - 1u;
    TIM1->CNT = 0u;
    TIM1->CH4CVR = IR_TIMER_DUTY;
    TIM1->CHCTLR2 &= ~0xff00u;
    TIM1->CHCTLR2 |= 0x6800u; /* CH4 PWM mode 1 + preload. */
    TIM1->CCER &= ~0x3000u;   /* CH4 disabled, non-inverted. */
    TIM1->BDTR |= TIM_MOE;
    TIM1->SWEVGR = TIM_UG;
    TIM1->CTLR1 |= TIM_CEN;
}

static void carrier_on(void)
{
    TIM1->CNT = 0u;
    GPIOC->CFGLR &= ~(0x0fu << (IR_GPIO_BIT * 4u));
    GPIOC->CFGLR |=
        (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP_AF) << (IR_GPIO_BIT * 4u);
    TIM1->CCER |= 1u << 12;
}

static void carrier_off(void)
{
    TIM1->CCER &= ~(1u << 12);
    GPIOC->BCR = 1u << IR_GPIO_BIT;
    GPIOC->CFGLR &= ~(0x0fu << (IR_GPIO_BIT * 4u));
    GPIOC->CFGLR |=
        (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP) << (IR_GPIO_BIT * 4u);
}

static void mark(uint16_t duration_us)
{
    carrier_on();
    Delay_Us(duration_us);
    carrier_off();
}

static uint8_t toshiba_frame_valid(const uint8_t *data, uint8_t length)
{
    uint8_t checksum = 0u;
    uint8_t i;

    if (length != 7u && length != 9u && length != 10u) return 0u;
    if ((uint8_t)(data[0] ^ data[1]) != 0xffu) return 0u;
    if ((uint8_t)(data[2] ^ data[3]) != 0xffu) return 0u;
    if ((uint8_t)((data[2] & 0x0fu) + 6u) != length) return 0u;
    for (i = 0u; i < (uint8_t)(length - 1u); ++i) checksum ^= data[i];
    return checksum == data[length - 1u];
}

static void send_toshiba_frame(const uint8_t *data, uint8_t length)
{
    uint8_t byte_index;
    uint8_t mask;

    mark(TOSHIBA_HEADER_MARK);
    Delay_Us(TOSHIBA_HEADER_SPACE);
    for (byte_index = 0u; byte_index < length; ++byte_index) {
        for (mask = 0x80u; mask != 0u; mask >>= 1u) {
            mark(TOSHIBA_BIT_MARK);
            Delay_Us((data[byte_index] & mask) ?
                     TOSHIBA_ONE_SPACE : TOSHIBA_ZERO_SPACE);
        }
    }
    mark(TOSHIBA_BIT_MARK);
}

static void process_report(void)
{
    uint8_t command;
    uint8_t length;
    uint8_t count;
    uint8_t data[IR_SEND_DATA_SIZE];
    uint8_t i;

    __disable_irq();
    command = pending_command;
    length = pending_length;
    count = pending_count;
    for (i = 0u; i < IR_SEND_DATA_SIZE; ++i) data[i] = pending_data[i];
    report_ready = 0u;
    __enable_irq();

    if (command != CMD_SEND_TOSHIBA) {
        last_status = STATUS_BAD_COMMAND;
        return;
    }
    if (count == 0u || count > 4u || !toshiba_frame_valid(data, length)) {
        last_status = STATUS_BAD_FRAME;
        return;
    }

    /*
     * rv003usb uses the EXTI interrupt.  A USB packet arriving during a
     * software-timed mark/space stretches it enough to corrupt an IR frame.
     * The SET_REPORT transfer is already complete, so protect the complete
     * Toshiba burst and resume USB immediately afterwards.
     */
    __disable_irq();
    for (i = 0u; i < count; ++i) {
        send_toshiba_frame(data, length);
        if ((uint8_t)(i + 1u) < count) Delay_Us(TOSHIBA_GAP);
    }
    carrier_off();
    __enable_irq();
    last_length = length;
    last_count = count;
    last_status = STATUS_OK;
}

int main(void)
{
    SystemInit();
    funGpioInitAll();
    ir_carrier_init();
    carrier_off();

    Delay_Ms(100);
    usb_setup();

    for (;;) {
        if (report_ready) {
            /* Let EP0 finish the SET_REPORT status stage before masking USB. */
            Delay_Ms(5);
            process_report();
        }
    }
}

void usb_handle_user_in_request(struct usb_endpoint *e, uint8_t *scratchpad,
                                int endp, uint32_t sendtok,
                                struct rv003usb_internal *ist)
{
    (void)e;
    (void)scratchpad;
    (void)ist;
    if (endp) usb_send_empty(sendtok);
}

void usb_handle_other_control_message(struct usb_endpoint *e,
                                      struct usb_urb *s,
                                      struct rv003usb_internal *ist)
{
    uint16_t request = s->wRequestTypeLSBRequestMSB;
    uint16_t value = (uint16_t)(s->lValueLSBIndexMSB & 0xffffu);
    uint16_t length = s->wLength;
    (void)ist;

    if (request == HID_REQ_GET_IDLE) {
        e->opaque = &idle_rate;
        e->max_len = (length < 1u) ? length : 1u;
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
    (void)current_endpoint;
    (void)ist;

    if (to_copy > len) to_copy = len;
    if (to_copy > 0 && offset < (int)sizeof(feature_report)) {
        if (to_copy > (int)sizeof(feature_report) - offset)
            to_copy = (int)sizeof(feature_report) - offset;
        memcpy(feature_report + offset, data, (size_t)to_copy);
    }
    e->count++;
    if ((e->count << 3) >= e->max_len &&
        e->max_len == (int)sizeof(feature_report) &&
        feature_report[0] == IR_SEND_REPORT_ID) {
        uint8_t i;
        pending_command = feature_report[1];
        pending_length = feature_report[2];
        pending_count = feature_report[3];
        for (i = 0u; i < IR_SEND_DATA_SIZE; ++i)
            pending_data[i] = feature_report[4u + i];
        last_status = STATUS_IDLE;
        report_ready = 1u;
    }
}

void usb_handle_hid_get_report_start(struct usb_endpoint *e, int req_len,
                                     uint32_t value)
{
    (void)value;
    memset(feature_report, 0, sizeof(feature_report));
    feature_report[0] = IR_SEND_REPORT_ID;
    feature_report[1] = last_status;
    feature_report[2] = last_length;
    feature_report[3] = last_count;
    if (req_len > (int)sizeof(feature_report)) req_len = sizeof(feature_report);
    e->opaque = feature_report;
    e->max_len = req_len;
}

void usb_handle_hid_set_report_start(struct usb_endpoint *e, int req_len,
                                     uint32_t value)
{
    uint8_t report_id = (uint8_t)(value & 0xffu);
    if (report_id != IR_SEND_REPORT_ID) req_len = 0;
    if (req_len > (int)sizeof(feature_report)) req_len = sizeof(feature_report);
    memset(feature_report, 0, sizeof(feature_report));
    e->max_len = req_len;
}
