#include "ch32fun.h"
#include "rv003usb.h"
#include "usb_config.h"

#include <stdint.h>
#include <string.h>

/* UIAPduino D6/A2 = CH32V003 PC4 = TIM1_CH4. */
#define MOTOR_PWM_PERIOD     256u
#define MOTOR_PWM_PRESCALER  374u

/* HID class requests used by macOS while attaching the device. */
#define HID_REQ_GET_IDLE 0x02A1u
#define HID_REQ_SET_IDLE 0x0A21u

static volatile uint8_t motor_level;
static volatile uint8_t report_ready;
static uint8_t idle_rate;
static uint8_t feature_report[MOTOR_REPORT_TOTAL_SIZE] = {
    MOTOR_REPORT_ID,
    0
};

static void motor_pwm_init(void)
{
    RCC->APB2PCENR |= RCC_APB2Periph_GPIOC | RCC_APB2Periph_TIM1;

    /* Fail-safe initial state: PC4 GPIO LOW. */
    GPIOC->CFGLR &= ~(0x0fu << (4u * 4u));
    GPIOC->CFGLR |=
        (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP) << (4u * 4u);
    GPIOC->BCR = 1u << 4;

    RCC->APB2PRSTR |= RCC_APB2Periph_TIM1;
    RCC->APB2PRSTR &= ~RCC_APB2Periph_TIM1;

    /* 48 MHz / (375 * 256) = 500 Hz. */
    TIM1->PSC = MOTOR_PWM_PRESCALER;
    TIM1->ATRLR = MOTOR_PWM_PERIOD - 1u;
    TIM1->CNT = 0;
    TIM1->CH4CVR = 0;

    /* CH4 output, preload enabled, PWM mode 1. */
    TIM1->CHCTLR2 &= ~0xff00u;
    TIM1->CHCTLR2 |= 0x6800u;

    /* CH4 initially disabled, non-inverted. */
    TIM1->CCER &= ~0x3000u;

    TIM1->BDTR |= TIM_MOE;
    TIM1->SWEVGR = TIM_UG;
    TIM1->CTLR1 |= TIM_CEN;
}

static void motor_set_level(uint8_t level)
{
    uint16_t pulse;

    if (level > 100u) {
        level = 100u;
    }

    if (level == 0u) {
        TIM1->CCER &= ~(1u << 12);
        TIM1->CH4CVR = 0u;

        GPIOC->BCR = 1u << 4;
        GPIOC->CFGLR &= ~(0x0fu << (4u * 4u));
        GPIOC->CFGLR |=
            (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP) << (4u * 4u);
    } else if (level == 100u) {
        /*
         * Maximum output: reproduce the original ON/OFF PoC by driving
         * PC4 continuously HIGH instead of using the PWM boundary value.
         */
        TIM1->CCER &= ~(1u << 12);

        GPIOC->BSHR = 1u << 4;
        GPIOC->CFGLR &= ~(0x0fu << (4u * 4u));
        GPIOC->CFGLR |=
            (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP) << (4u * 4u);
    } else {
        pulse = (uint16_t)(
            ((uint32_t)level * MOTOR_PWM_PERIOD + 50u) / 100u);

        TIM1->CH4CVR = pulse;
        TIM1->SWEVGR = TIM_UG;

        GPIOC->CFGLR &= ~(0x0fu << (4u * 4u));
        GPIOC->CFGLR |=
            (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP_AF) << (4u * 4u);

        TIM1->CCER &= ~(1u << 13);
        TIM1->CCER |= 1u << 12;
    }

    motor_level = level;
    feature_report[0] = MOTOR_REPORT_ID;
    feature_report[1] = motor_level;
}

int main(void)
{
    SystemInit();
    funGpioInitAll();

    motor_pwm_init();
    motor_set_level(0);

    Delay_Ms(100);
    usb_setup();

    for (;;) {
        if (report_ready) {
            uint8_t command;

            report_ready = 0;
            command = feature_report[1];
            motor_set_level(command);
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

    if (endp) {
        usb_send_empty(sendtok);
    }
}

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
            feature_report[0] == MOTOR_REPORT_ID) {
            report_ready = 1;
        }
    }
}

void usb_handle_hid_get_report_start(struct usb_endpoint *e,
                                     int reqLen,
                                     uint32_t lValueLSBIndexMSB)
{
    (void)lValueLSBIndexMSB;

    feature_report[0] = MOTOR_REPORT_ID;
    feature_report[1] = motor_level;

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

    feature_report[0] = 0;
    feature_report[1] = 0;
    e->max_len = reqLen;
}
