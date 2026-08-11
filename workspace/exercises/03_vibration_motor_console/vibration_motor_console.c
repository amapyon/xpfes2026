#include "ch32fun.h"
#include "rv003usb.h"
#include "usb_config.h"

#include <stdint.h>
#include <string.h>

/* UIAPduino D6/A2 = CH32V003 PC4。モジュールのIN端子だけを駆動する。 */
#define MOTOR_PIN PC4
#define MOTOR_PWM_PERIOD 256u
#define MOTOR_PWM_PRESCALER 374u

/* macOSが接続時に送るHIDクラス要求。 */
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

    /* 起動時はPC4を通常GPIOのLowにして誤振動を防ぐ。 */
    GPIOC->CFGLR &= ~(0x0fu << (4u * 4u));
    GPIOC->CFGLR |= (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP) << (4u * 4u);
    GPIOC->BCR = 1u << 4;

    RCC->APB2PRSTR |= RCC_APB2Periph_TIM1;
    RCC->APB2PRSTR &= ~RCC_APB2Periph_TIM1;

    /* 48MHz / (375 * 256) = 500Hz。 */
    TIM1->PSC = MOTOR_PWM_PRESCALER;
    TIM1->ATRLR = MOTOR_PWM_PERIOD - 1u;
    TIM1->CNT = 0;
    TIM1->CH4CVR = 0;

    /* TIM1_CH4をPWM mode 1、preload有効で準備する。 */
    TIM1->CHCTLR2 &= ~0xff00u;
    TIM1->CHCTLR2 |= 0x6800u;
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
        /* OFFではPWM出力を切り、PC4をLowへ戻す。 */
        TIM1->CCER &= ~(1u << 12);
        TIM1->CH4CVR = 0u;
        GPIOC->BCR = 1u << 4;
        GPIOC->CFGLR &= ~(0x0fu << (4u * 4u));
        GPIOC->CFGLR |= (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP) << (4u * 4u);
    } else if (level == 100u) {
        /* 最大レベルはPWM境界値を使わず、PC4を連続Highにする。 */
        TIM1->CCER &= ~(1u << 12);
        GPIOC->BSHR = 1u << 4;
        GPIOC->CFGLR &= ~(0x0fu << (4u * 4u));
        GPIOC->CFGLR |= (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP) << (4u * 4u);
    } else {
        pulse = (uint16_t)(((uint32_t)level * MOTOR_PWM_PERIOD + 50u) / 100u);
        TIM1->CH4CVR = pulse;
        TIM1->SWEVGR = TIM_UG;
        GPIOC->CFGLR &= ~(0x0fu << (4u * 4u));
        GPIOC->CFGLR |= (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP_AF) << (4u * 4u);
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

    /* USB初期化より前に必ずLowへ固定し、起動時の誤振動を防ぐ。 */
    motor_pwm_init();
    motor_set_level(0);

    Delay_Ms(100);
    usb_setup();

    for (;;) {
        if (report_ready) {
            report_ready = 0;
            motor_set_level(feature_report[1]);
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
    if ((e->count << 3) >= e->max_len &&
        e->max_len == (int)sizeof(feature_report) &&
        feature_report[0] == MOTOR_REPORT_ID) {
        report_ready = 1;
    }
}

void usb_handle_hid_get_report_start(struct usb_endpoint *e,
                                     int req_len,
                                     uint32_t value)
{
    (void)value;
    feature_report[0] = MOTOR_REPORT_ID;
    feature_report[1] = motor_level;
    if (req_len > (int)sizeof(feature_report)) {
        req_len = sizeof(feature_report);
    }
    e->opaque = feature_report;
    e->max_len = req_len;
}

void usb_handle_hid_set_report_start(struct usb_endpoint *e,
                                     int req_len,
                                     uint32_t value)
{
    uint8_t report_id = (uint8_t)(value & 0xffu);

    if (report_id != MOTOR_REPORT_ID) {
        e->max_len = 0;
        return;
    }
    if (req_len > (int)sizeof(feature_report)) {
        req_len = sizeof(feature_report);
    }
    feature_report[0] = 0;
    feature_report[1] = 0;
    e->max_len = req_len;
}
