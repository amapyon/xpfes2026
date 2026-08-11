#ifndef UIAP_HAPTIC_PATTERN_H
#define UIAP_HAPTIC_PATTERN_H

#include "haptic_pattern_protocol.h"

#define HAPTIC_PWM_PERIOD 256u
#define HAPTIC_PWM_PRESCALER 374u

enum haptic_pattern_phase {
    HAPTIC_PATTERN_IDLE,
    HAPTIC_PATTERN_ON,
    HAPTIC_PATTERN_OFF,
    HAPTIC_PATTERN_CONTINUOUS
};

static enum haptic_pattern_phase haptic_pattern_phase;
static uint8_t haptic_pattern_level;
static uint8_t haptic_pattern_requested_level;
static uint8_t haptic_pattern_pulses_remaining;
static uint16_t haptic_pattern_on_ms;
static uint16_t haptic_pattern_off_ms;
static uint16_t haptic_pattern_ms_remaining;

static void haptic_pattern_set_level(uint8_t level)
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
        GPIOC->CFGLR |= (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP) << (4u * 4u);
    } else if (level == 100u) {
        TIM1->CCER &= ~(1u << 12);
        GPIOC->BSHR = 1u << 4;
        GPIOC->CFGLR &= ~(0x0fu << (4u * 4u));
        GPIOC->CFGLR |= (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP) << (4u * 4u);
    } else {
        pulse = (uint16_t)(((uint32_t)level * HAPTIC_PWM_PERIOD + 50u) / 100u);
        TIM1->CH4CVR = pulse;
        TIM1->SWEVGR = TIM_UG;
        GPIOC->CFGLR &= ~(0x0fu << (4u * 4u));
        GPIOC->CFGLR |= (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP_AF) << (4u * 4u);
        TIM1->CCER &= ~(1u << 13);
        TIM1->CCER |= 1u << 12;
    }
    haptic_pattern_level = level;
}

static void haptic_pattern_stop(void)
{
    haptic_pattern_set_level(0u);
    haptic_pattern_phase = HAPTIC_PATTERN_IDLE;
    haptic_pattern_pulses_remaining = 0u;
    haptic_pattern_ms_remaining = 0u;
    haptic_pattern_requested_level = 0u;
}

static void haptic_pattern_init(void)
{
    RCC->APB2PCENR |= RCC_APB2Periph_GPIOC | RCC_APB2Periph_TIM1;
    GPIOC->CFGLR &= ~(0x0fu << (4u * 4u));
    GPIOC->CFGLR |= (GPIO_Speed_10MHz | GPIO_CNF_OUT_PP) << (4u * 4u);
    GPIOC->BCR = 1u << 4;

    RCC->APB2PRSTR |= RCC_APB2Periph_TIM1;
    RCC->APB2PRSTR &= ~RCC_APB2Periph_TIM1;
    TIM1->PSC = HAPTIC_PWM_PRESCALER;
    TIM1->ATRLR = HAPTIC_PWM_PERIOD - 1u;
    TIM1->CNT = 0;
    TIM1->CH4CVR = 0;
    TIM1->CHCTLR2 &= ~0xff00u;
    TIM1->CHCTLR2 |= 0x6800u;
    TIM1->CCER &= ~0x3000u;
    TIM1->BDTR |= TIM_MOE;
    TIM1->SWEVGR = TIM_UG;
    TIM1->CTLR1 |= TIM_CEN;
    haptic_pattern_stop();
}

static void haptic_pattern_start(uint8_t level, uint16_t on_ms,
                                 uint16_t off_ms, uint8_t count)
{
    haptic_pattern_stop();
    if (level == 0u) {
        return;
    }
    if (level > 100u) {
        level = 100u;
    }
    haptic_pattern_requested_level = level;
    if (count == 0u) {
        haptic_pattern_phase = HAPTIC_PATTERN_CONTINUOUS;
        haptic_pattern_set_level(level);
        return;
    }
    if (on_ms == 0u) {
        return;
    }
    if (on_ms > HAPTIC_PATTERN_MAX_MS) {
        on_ms = HAPTIC_PATTERN_MAX_MS;
    }
    if (off_ms > HAPTIC_PATTERN_MAX_MS) {
        off_ms = HAPTIC_PATTERN_MAX_MS;
    }
    haptic_pattern_on_ms = on_ms;
    haptic_pattern_off_ms = off_ms;
    haptic_pattern_pulses_remaining = count;
    haptic_pattern_phase = HAPTIC_PATTERN_ON;
    haptic_pattern_ms_remaining = on_ms;
    haptic_pattern_set_level(level);
}

static void haptic_pattern_tick_1ms(void)
{
    if (haptic_pattern_phase == HAPTIC_PATTERN_IDLE ||
        haptic_pattern_phase == HAPTIC_PATTERN_CONTINUOUS ||
        haptic_pattern_ms_remaining == 0u) {
        return;
    }
    haptic_pattern_ms_remaining--;
    if (haptic_pattern_ms_remaining != 0u) {
        return;
    }
    if (haptic_pattern_phase == HAPTIC_PATTERN_ON) {
        haptic_pattern_pulses_remaining--;
        if (haptic_pattern_pulses_remaining == 0u) {
            haptic_pattern_stop();
        } else if (haptic_pattern_off_ms == 0u) {
            haptic_pattern_ms_remaining = haptic_pattern_on_ms;
        } else {
            haptic_pattern_set_level(0u);
            haptic_pattern_phase = HAPTIC_PATTERN_OFF;
            haptic_pattern_ms_remaining = haptic_pattern_off_ms;
        }
        return;
    }
    haptic_pattern_phase = HAPTIC_PATTERN_ON;
    haptic_pattern_ms_remaining = haptic_pattern_on_ms;
    haptic_pattern_set_level(haptic_pattern_requested_level);
}

static uint8_t haptic_pattern_current_level(void)
{
    return haptic_pattern_level;
}

#endif
