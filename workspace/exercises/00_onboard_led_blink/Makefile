.DEFAULT_GOAL := all

ifndef UIAP_PLATFORM
$(error UIAP_PLATFORM is not set. Start with start-uiap.cmd or start-uiap.command)
endif
ifeq ($(filter $(UIAP_PLATFORM),win mac),)
$(error UIAP_PLATFORM must be win or mac)
endif
ifndef UIAP_WORKSPACE
$(error UIAP_WORKSPACE is not set. Start the UIAP development environment first)
endif
ifndef UIAP_RUNTIME
$(error UIAP_RUNTIME is not set. Start the UIAP development environment first)
endif

UIAP_WORKSPACE_POSIX := $(subst \,/,$(UIAP_WORKSPACE))
UIAP_RUNTIME_POSIX := $(subst \,/,$(UIAP_RUNTIME))
CH32FUN_ROOT := $(UIAP_WORKSPACE_POSIX)/deps/ch32fun
CH32FUN := $(CH32FUN_ROOT)/ch32fun
MINICHLINK := $(UIAP_RUNTIME_POSIX)/bin

TARGET := onboard_led_blink
TARGET_MCU := CH32V003
MCU_PACKAGE := 1
PREFIX := riscv-none-elf
# Use recursive assignment: $< is defined only while the cv_flash recipe runs.
FLASH_COMMAND = "$(MINICHLINK)/minichlink" -c 0x1209b803 -w "$<" $(WRITE_SECTION) -b

include $(CH32FUN)/ch32fun.mk

all: build
flash: cv_flash
clean: cv_clean
size: build
	$(PREFIX)-size $(TARGET).elf
doctor:
	@doctor
report:
	@report
app:
	@echo This exercise has no host-side application.
help:
	@echo make
	@echo make flash
	@echo make clean
	@echo make size
	@echo make doctor
	@echo make report

.PHONY: all flash clean size doctor report app help
