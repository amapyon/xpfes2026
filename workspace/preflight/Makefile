# UIAPduino Pro Micro CH32V003 V1.4
# Vendor-defined HID preflight self-test
#
# Participant commands:
#   make
#   make flash
#   make preflight
#   make clean

ifndef UIAP_WORKSPACE
$(error UIAP_WORKSPACE is not set. Start the UIAP development environment first)
endif

TARGET := preflight_hid
TARGET_MCU := CH32V003
PREFIX ?= riscv-none-elf

# Normalize Windows paths before passing them to POSIX-compatible build tools.
UIAP_WORKSPACE_POSIX := $(subst \,/,$(UIAP_WORKSPACE))
UIAP_RUNTIME_POSIX := $(subst \,/,$(UIAP_RUNTIME))
UIAP_PYTHON_POSIX := $(subst \,/,$(UIAP_PYTHON))

CH32FUN_ROOT ?= $(UIAP_WORKSPACE_POSIX)/deps/ch32fun
CH32FUN ?= $(CH32FUN_ROOT)/ch32fun
RV003USB_ROOT ?= $(UIAP_WORKSPACE_POSIX)/deps/rv003usb
RV003USB ?= $(RV003USB_ROOT)

RV003USB_CORE := $(RV003USB)/rv003usb
ADDITIONAL_C_FILES := \
	$(RV003USB_CORE)/rv003usb.S \
	$(RV003USB_CORE)/rv003usb.c

EXTRA_CFLAGS += -I$(RV003USB_CORE)
EXTRA_ELF_DEPENDENCIES := funconfig.h

# Prefer the Devkit runtime binary. Fall back to the ch32fun-built binary.
ifeq ($(OS),Windows_NT)
MINICHLINK_EXE := $(firstword \
	$(wildcard $(UIAP_RUNTIME_POSIX)/bin/minichlink.exe) \
	$(wildcard $(UIAP_RUNTIME_POSIX)/bin/minichlink) \
	$(wildcard $(CH32FUN_ROOT)/minichlink/minichlink.exe) \
	$(wildcard $(CH32FUN_ROOT)/minichlink/minichlink))
else
MINICHLINK_EXE := $(firstword \
	$(wildcard $(UIAP_RUNTIME_POSIX)/bin/minichlink) \
	$(wildcard $(CH32FUN_ROOT)/minichlink/minichlink))
endif

# Prefer the explicitly configured Devkit Python.
ifeq ($(strip $(UIAP_PYTHON_POSIX)),)
ifeq ($(OS),Windows_NT)
PYTHON := $(UIAP_RUNTIME_POSIX)/python/python.exe
else
PYTHON := $(UIAP_RUNTIME_POSIX)/python/bin/python3
endif
else
PYTHON := $(UIAP_PYTHON_POSIX)
endif

include $(CH32FUN)/ch32fun.mk

.PHONY: all flash preflight clean size help

all: build

# ch32fun.h always includes funconfig.h. Keep the distributed source tree
# exactly as requested by generating this small build configuration locally.
funconfig.h:
	@printf '%s\n' \
		'#ifndef _FUNCONFIG_H' \
		'#define _FUNCONFIG_H' \
		'#define FUNCONF_USE_HSI 1' \
		'#define FUNCONF_USE_HSE 0' \
		'#define FUNCONF_USE_PLL 1' \
		'#define FUNCONF_SYSTEM_CORE_CLOCK 48000000' \
		'#define FUNCONF_SYSTICK_USE_HCLK 1' \
		'#define FUNCONF_USE_DEBUGPRINTF 0' \
		'#define FUNCONF_USE_UARTPRINTF 0' \
		'#define FUNCONF_NULL_PRINTF 1' \
		'#endif' > "$@"

flash: build
ifeq ($(strip $(MINICHLINK_EXE)),)
	$(error minichlink was not found in the Devkit. Run setup/doctor first)
else
	"$(MINICHLINK_EXE)" -c 0x1209b803 -w "$(TARGET).bin" flash -b
endif

preflight:
	"$(PYTHON)" "host/preflight_hid.py"

size: build
	$(PREFIX)-size "$(TARGET).elf"

clean: cv_clean
	-rm -f funconfig.h

help:
	@printf '%s\n' \
		'make           Build the preflight HID firmware' \
		'make flash     Flash it through the UIAPduino USB bootloader' \
		'make preflight Run the HID ping/pong self-test' \
		'make size      Show firmware size' \
		'make clean     Remove generated files'
