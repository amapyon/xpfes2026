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
CURDIR_POSIX := $(subst \,/,$(CURDIR))
CH32FUN_ROOT := $(UIAP_WORKSPACE_POSIX)/deps/ch32fun
CH32FUN := $(CH32FUN_ROOT)/ch32fun
RV003USB := $(UIAP_WORKSPACE_POSIX)/deps/rv003usb
MINICHLINK := $(UIAP_RUNTIME_POSIX)/bin
MOTOR_HOST := $(CURDIR_POSIX)/host/motorctl.py

TARGET := vibration_motor_console
TARGET_MCU := CH32V003
MCU_PACKAGE := 1
PREFIX := riscv-none-elf
ADDITIONAL_C_FILES += $(RV003USB)/rv003usb/rv003usb.S $(RV003USB)/rv003usb/rv003usb.c
EXTRA_CFLAGS += -I$(RV003USB)/rv003usb -I$(CURDIR_POSIX)
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

host-doctor:
	"$(UIAP_PYTHON)" "$(MOTOR_HOST)" self-test
hidcheck:
	"$(UIAP_PYTHON)" "$(MOTOR_HOST)" hidcheck
list:
	"$(UIAP_PYTHON)" "$(MOTOR_HOST)" list
LEVEL ?= 50
on:
	"$(UIAP_PYTHON)" "$(MOTOR_HOST)" on "$(LEVEL)"
off:
	"$(UIAP_PYTHON)" "$(MOTOR_HOST)" off
status:
	"$(UIAP_PYTHON)" "$(MOTOR_HOST)" status
PULSE_SECONDS ?= 0.2
pulse:
	"$(UIAP_PYTHON)" "$(MOTOR_HOST)" pulse "$(PULSE_SECONDS)" "$(LEVEL)"
ON_MS ?= 80
OFF_MS ?= 40
COUNT ?= 2
pattern:
	"$(UIAP_PYTHON)" "$(MOTOR_HOST)" pattern "$(LEVEL)" "$(ON_MS)" "$(OFF_MS)" "$(COUNT)"

help:
	@echo make
	@echo make flash
	@echo make clean
	@echo make size
	@echo make host-doctor
	@echo make hidcheck
	@echo make list
	@echo make pulse
	@echo make pulse LEVEL=75 PULSE_SECONDS=0.5
	@echo make pattern LEVEL=95 ON_MS=80 OFF_MS=40 COUNT=2
	@echo make on
	@echo make on LEVEL=75
	@echo make status
	@echo make off
	@echo make doctor
	@echo make report

.PHONY: all flash clean size host-doctor hidcheck list on off status pulse pattern doctor report help
