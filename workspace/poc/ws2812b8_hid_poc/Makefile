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

TARGET := ws2812b8_hid
TARGET_MCU := CH32V003

# Normalize Windows paths before they are handed to the POSIX-compatible shell.
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

.PHONY: flash clean size app list doctor help check-deps

flash: $(TARGET).bin
	$(FLASH_COMMAND)

clean: cv_clean

size: $(TARGET).elf
	$(PREFIX)-size $<

check-deps:
	@test -f "$(CH32FUN)/../extralibs/ws2812b_dma_spi_led_driver.h" || \
	  (echo "[UIAP-LED-E201] Missing ch32fun extralibs/ws2812b_dma_spi_led_driver.h"; exit 2)
	@test -f "$(RV003USB)/rv003usb.c" || \
	  (echo "[UIAP-LED-E202] Missing rv003usb.c under $(RV003USB)"; exit 2)
	@test -f "$(RV003USB)/rv003usb.S" || \
	  (echo "[UIAP-LED-E203] Missing rv003usb.S under $(RV003USB)"; exit 2)
	@echo "PoC dependencies: PASS"

APP_SPEC := $(strip $(filter-out app,$(MAKECMDGOALS)))

app:
	@if [ -z "$(UIAP_PYTHON_POSIX)" ]; then \
	  echo "[UIAP-LED-E210] UIAP_PYTHON is not set. Start the UIAP Devkit environment first."; \
	  exit 2; \
	fi
	@if [ -z "$(APP_SPEC)" ]; then \
	  "$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/ws2812b8_host.py"; \
	  exit $$?; \
	fi
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/ws2812b8_host.py" "$(APP_SPEC)"

list:
	@if [ -z "$(UIAP_PYTHON_POSIX)" ]; then echo "[UIAP-LED-E210] UIAP_PYTHON is not set."; exit 2; fi
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/ws2812b8_host.py" --list

doctor: check-deps
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/ws2812b8_host.py" --doctor

help:
	@echo "make                  Build firmware"
	@echo "make flash            Build and flash through 1209:B803 bootloader"
	@echo "make clean            Remove build outputs"
	@echo "make size             Show firmware size"
	@echo "make check-deps       Check PoC-specific dependencies"
	@echo "make list             List matching HID devices"
	@echo "make doctor           Dependency, host parser/report, Python/hidapi, and platform check"
	@echo "make app on           All 8 LEDs on at safe white RGB 64,64,64"
	@echo "make app off          All LEDs off"
	@echo "make app status       Read current LED state"
	@echo "make app 1:255,255,255"
	@echo "make app 1:255,255,255,8:255,128,0"

# GNU make treats the words after 'app' as additional goals. Swallow only those
# extra goals; for all other invocations an unknown goal is an error.
.DEFAULT:
	@if echo " $(MAKECMDGOALS) " | grep -q " app "; then \
	  :; \
	else \
	  echo "Unknown target: $@"; \
	  exit 2; \
	fi
