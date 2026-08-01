.DEFAULT_GOAL := all

ifndef UIAP_WORKSPACE
$(error UIAP_WORKSPACE is not set. Start the UIAP development environment with start-uiap.command)
endif
ifndef UIAP_DEVKIT_ROOT
$(error UIAP_DEVKIT_ROOT is not set. Start the UIAP development environment with start-uiap.command)
endif

TARGET := onboard_led_blink
TARGET_MCU ?= CH32V003
PREFIX ?= riscv-none-elf

CH32FUN_ROOT ?= $(UIAP_WORKSPACE)/deps/ch32fun
CH32FUN ?= $(CH32FUN_ROOT)/ch32fun
RV003USB_ROOT ?= $(UIAP_WORKSPACE)/deps/rv003usb
RV003USB ?= $(RV003USB_ROOT)
MINICHLINK ?= $(UIAP_RUNTIME)/bin

# UIAPduino V1.4 USB bootloader: 1209:B803
FLASH_COMMAND = "$(MINICHLINK)/minichlink" -c 0x1209b803 -w "$<" flash -b

.PHONY: all flash clean size help doctor report

all: build

include $(CH32FUN)/ch32fun.mk

flash: cv_flash
clean: cv_clean

size: build
	$(PREFIX)-size $(TARGET).elf

doctor:
	/bin/sh "$(UIAP_DEVKIT_ROOT)/scripts/doctor.sh"

report:
	/bin/sh "$(UIAP_DEVKIT_ROOT)/scripts/report.sh"

help:
	@printf '%s\n' \
	  'make         Build firmware' \
	  'make flash   Flash through the 1209:B803 USB bootloader' \
	  'make clean   Remove normal build outputs' \
	  'make size    Show ELF memory-section sizes' \
	  'make doctor  Run Devkit diagnostics' \
	  'make report  Create a sanitized diagnostic report'
