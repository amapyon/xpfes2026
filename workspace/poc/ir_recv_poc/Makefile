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
ifndef UIAP_PYTHON
$(error UIAP_PYTHON is not set. Start the UIAP development environment first)
endif

TARGET := ir_recv_poc
TARGET_MCU := CH32V003
MCU_PACKAGE := 1
PREFIX := riscv-none-elf

UIAP_WORKSPACE_POSIX := $(subst \,/,$(UIAP_WORKSPACE))
UIAP_RUNTIME_POSIX := $(subst \,/,$(UIAP_RUNTIME))
UIAP_PYTHON_POSIX := $(subst \,/,$(UIAP_PYTHON))
CH32FUN_ROOT ?= $(UIAP_WORKSPACE_POSIX)/deps/ch32fun
CH32FUN ?= $(CH32FUN_ROOT)/ch32fun
RV003USB_ROOT ?= $(UIAP_WORKSPACE_POSIX)/deps/rv003usb
RV003USB ?= $(RV003USB_ROOT)/rv003usb

ADDITIONAL_C_FILES += $(RV003USB)/rv003usb.S $(RV003USB)/rv003usb.c
EXTRA_CFLAGS += -I$(RV003USB_ROOT)/lib -I$(RV003USB)

MINICHLINK_EXE ?= $(UIAP_RUNTIME_POSIX)/bin/minichlink
FLASH_COMMAND = "$(MINICHLINK_EXE)" -c 0x1209b803 -w "$<" flash -b

.PHONY: all
all: build

include $(CH32FUN)/ch32fun.mk

.PHONY: flash clean size app list doctor check-deps help
flash: $(TARGET).bin
	$(FLASH_COMMAND)
clean: cv_clean
size: $(TARGET).elf
	$(PREFIX)-size $<
app:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/ir_recv_host.py"
list:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/ir_recv_host.py" --list
doctor: check-deps
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/ir_recv_host.py" --doctor
check-deps:
	@test -f "$(RV003USB)/rv003usb.c" || (echo "Missing rv003usb.c"; exit 2)
	@test -f "$(RV003USB)/rv003usb.S" || (echo "Missing rv003usb.S"; exit 2)
	@echo "PoC dependencies: PASS"
help:
	@echo "make          Build firmware"
	@echo "make flash    Flash through the UIAPduino USB bootloader"
	@echo "make app      Display received IR codes"
	@echo "make list     List matching HID devices"
	@echo "make doctor   Check dependencies and host environment"
	@echo "make clean    Remove build outputs"
