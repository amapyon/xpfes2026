.DEFAULT_GOAL := all

ifndef UIAP_WORKSPACE
$(error UIAP_WORKSPACE is not set. Start the UIAP development environment with start-uiap.command)
endif
ifndef UIAP_DEVKIT_ROOT
$(error UIAP_DEVKIT_ROOT is not set. Start the UIAP development environment with start-uiap.command)
endif

TARGET := macro_keyboard
TARGET_MCU ?= CH32V003
PREFIX ?= riscv-none-elf
CH32FUN_ROOT ?= $(UIAP_WORKSPACE)/deps/ch32fun
CH32FUN ?= $(CH32FUN_ROOT)/ch32fun
RV003USB_ROOT ?= $(UIAP_WORKSPACE)/deps/rv003usb
RV003USB ?= $(RV003USB_ROOT)
MINICHLINK ?= $(UIAP_RUNTIME)/bin

ADDITIONAL_C_FILES += $(RV003USB)/rv003usb/rv003usb.S $(RV003USB)/rv003usb/rv003usb.c
EXTRA_CFLAGS += -I$(RV003USB)/lib -I$(RV003USB)/rv003usb
FLASH_COMMAND = "$(MINICHLINK)/minichlink" -c 0x1209b803 -w "$<" flash -b

.PHONY: all flash clean size help hidcheck app doctor report
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
hidcheck:
	"$(UIAP_PYTHON)" "$(CURDIR)/host/hidcheck.py"
app: hidcheck

help:
	@printf '%s\n' \
	  'make         Build the USB HID keyboard firmware' \
	  'make flash   Flash through the 1209:B803 USB bootloader' \
	  'make clean   Remove normal build outputs' \
	  'make size    Show ELF memory-section sizes' \
	  'make doctor  Run Devkit diagnostics' \
	  'make report  Create a sanitized diagnostic report'
