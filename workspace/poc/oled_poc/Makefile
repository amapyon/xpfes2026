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

TARGET := oled_poc
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
EXTRA_CFLAGS += -I$(RV003USB_ROOT)/lib -I$(RV003USB) -I$(CURDIR)

MINICHLINK_EXE ?= $(UIAP_RUNTIME_POSIX)/bin/minichlink
FLASH_COMMAND = "$(MINICHLINK_EXE)" -c 0x1209b803 -w "$<" flash -b

.PHONY: all
all: build

include $(CH32FUN)/ch32fun.mk

.PHONY: flash clean size demo output clear fill text line rect circle probe status list doctor self-test check-deps help
flash: $(TARGET).bin
	$(FLASH_COMMAND)
clean: cv_clean
size: $(TARGET).elf
	$(PREFIX)-size $<
demo:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/oled_host.py" demo
output:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/oled_host.py" output
clear:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/oled_host.py" clear
fill:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/oled_host.py" fill
text:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/oled_host.py" text "$(COL)" "$(ROW)" "$(TEXT)"
line:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/oled_host.py" line "$(X0)" "$(Y0)" "$(X1)" "$(Y1)"
rect:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/oled_host.py" rect "$(X0)" "$(Y0)" "$(X1)" "$(Y1)" $(if $(filter 1 yes true,$(FILL)),--fill,)
circle:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/oled_host.py" circle "$(X)" "$(Y)" "$(R)" $(if $(filter 1 yes true,$(FILL)),--fill,)
probe:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/oled_host.py" probe
status:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/oled_host.py" status
list:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/oled_host.py" --list
doctor: check-deps
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/oled_host.py" --doctor
self-test:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/oled_host.py" --self-test
check-deps:
	@test -f "$(RV003USB)/rv003usb.c" || (echo "Missing rv003usb.c"; exit 2)
	@test -f "$(RV003USB)/rv003usb.S" || (echo "Missing rv003usb.S"; exit 2)
	@echo "PoC dependencies: PASS"
help:
	@echo "make             Build firmware"
	@echo "make flash       Flash through the UIAPduino USB bootloader"
	@echo "make demo        Draw and immediately display the demo"
	@echo "make clear       Clear the RAM buffer (use make output afterwards)"
	@echo "make fill        Fill the RAM buffer (use make output afterwards)"
	@echo 'make text COL=1 ROW=1 TEXT="Hello"'
	@echo "make line X0=0 Y0=0 X1=127 Y1=63"
	@echo "make rect X0=0 Y0=0 X1=127 Y1=63"
	@echo "make rect X0=4 Y0=4 X1=40 Y1=30 FILL=1"
	@echo "make circle X=64 Y=32 R=20"
	@echo "make circle X=64 Y=32 R=20 FILL=1"
	@echo "make output      Copy the RAM buffer to OLED"
	@echo "make probe       Probe 0x3C and 0x3D, then initialize SSD1306"
	@echo "make status      Read the last command result"
