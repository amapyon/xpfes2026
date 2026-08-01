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

TARGET := vibration_motor_hid
TARGET_MCU := CH32V003

# Normalize Windows paths before they are handed to the POSIX-compatible shell.
UIAP_WORKSPACE_POSIX := $(subst \,/,$(UIAP_WORKSPACE))
UIAP_RUNTIME_POSIX := $(subst \,/,$(UIAP_RUNTIME))
UIAP_PYTHON_POSIX := $(subst \,/,$(UIAP_PYTHON))

CH32FUN_ROOT ?= $(UIAP_WORKSPACE_POSIX)/deps/ch32fun
CH32FUN ?= $(CH32FUN_ROOT)/ch32fun
RV003USB_ROOT ?= $(UIAP_WORKSPACE_POSIX)/deps/rv003usb
RV003USB ?= $(RV003USB_ROOT)/rv003usb

PREFIX ?= riscv-none-elf
CC := $(PREFIX)-gcc
OBJDUMP := $(PREFIX)-objdump
OBJCOPY := $(PREFIX)-objcopy
SIZE := $(PREFIX)-size

GENERATED_LD := generated__.ld
SOURCES := \
	$(CH32FUN)/ch32fun.c \
	src/$(TARGET).c \
	$(RV003USB)/rv003usb.S \
	$(RV003USB)/rv003usb.c

CFLAGS := \
	-g -Os -flto \
	-ffunction-sections -fdata-sections -fmessage-length=0 \
	-msmall-data-limit=8 -fno-tree-loop-distribute-patterns \
	-march=rv32ec -mabi=ilp32e -DCH32V003 \
	-static-libgcc -nostdlib \
	-Isrc -I$(CH32FUN) -I$(CH32FUN_ROOT)/extralibs \
	-I$(RV003USB_ROOT)/lib -I$(RV003USB) \
	-Wall -Wextra

LDFLAGS := \
	-Wl,--print-memory-usage \
	-Wl,-Map=$(TARGET).map \
	-L$(CH32FUN_ROOT)/misc \
	-lgcc \
	-T $(GENERATED_LD) \
	-Wl,--gc-sections

MINICHLINK_EXE ?= $(UIAP_RUNTIME_POSIX)/bin/minichlink
FLASH_COMMAND = "$(MINICHLINK_EXE)" -c 0x1209b803 -w "$<" flash -b

.PHONY: all build flash clean size check-deps host doctor list on off status play help

all: build

$(GENERATED_LD): $(CH32FUN)/ch32fun.ld
	$(CC) -E -P -x c \
		-DTARGET_MCU=CH32V003 \
		-DMCU_PACKAGE=1 \
		-DTARGET_MCU_LD=0 \
		-DTARGET_MCU_MEMORY_SPLIT= \
		$< > $@

$(TARGET).elf: $(SOURCES) src/usb_config.h src/funconfig.h $(GENERATED_LD)
	$(CC) -o $@ $(SOURCES) $(CFLAGS) $(LDFLAGS)

$(TARGET).bin: $(TARGET).elf
	$(OBJDUMP) -S $< > $(TARGET).lst
	$(OBJCOPY) -R .storage -O binary $< $@
	$(OBJCOPY) -j .storage -O binary $< $(TARGET)_ext.bin
	$(OBJCOPY) -O ihex $< $(TARGET).hex

build: $(TARGET).bin

flash: $(TARGET).bin
	$(FLASH_COMMAND)

clean:
	rm -f \
		$(TARGET).elf \
		$(TARGET).bin \
		$(TARGET)_ext.bin \
		$(TARGET).hex \
		$(TARGET).lst \
		$(TARGET).map \
		$(GENERATED_LD)

size: $(TARGET).elf
	$(SIZE) $<

check-deps:
	@command -v "$(CC)" >/dev/null 2>&1 || \
	  (echo "[UIAP-MOTOR-E200] Missing $(CC). Run setup, then restart the UIAP Devkit."; exit 2)
	@test -f "$(CH32FUN)/ch32fun.mk" || \
	  (echo "[UIAP-MOTOR-E201] Missing ch32fun under $(CH32FUN)"; exit 2)
	@test -f "$(RV003USB)/rv003usb.c" || \
	  (echo "[UIAP-MOTOR-E202] Missing rv003usb.c under $(RV003USB)"; exit 2)
	@test -f "$(RV003USB)/rv003usb.S" || \
	  (echo "[UIAP-MOTOR-E203] Missing rv003usb.S under $(RV003USB)"; exit 2)
	@test -f "$(MINICHLINK_EXE)" || test -f "$(MINICHLINK_EXE).exe" || \
	  (echo "[UIAP-MOTOR-E204] Missing minichlink under $(UIAP_RUNTIME_POSIX)/bin"; exit 2)
	@echo "PoC dependencies: PASS"

host:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/motorctl.py" --self-test

doctor: check-deps
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/motorctl.py" --doctor

list:
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/motorctl.py" --list

ON_LEVEL := $(if $(word 2,$(MAKECMDGOALS)),$(word 2,$(MAKECMDGOALS)),50)
PATTERN ?= 100:0.1,0:0.4

on: host
	@case "$(ON_LEVEL)" in ''|*[!0-9]*) echo "level must be an integer from 1 to 100."; exit 2 ;; esac
	@test "$(ON_LEVEL)" -ge 1 2>/dev/null && test "$(ON_LEVEL)" -le 100 2>/dev/null || { echo "level must be an integer from 1 to 100."; exit 2; }
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/motorctl.py" on "$(ON_LEVEL)"

off: host
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/motorctl.py" off

status: host
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/motorctl.py" status

play: host
	"$(UIAP_PYTHON_POSIX)" "$(CURDIR)/host/motorctl.py" play "$(PATTERN)"

help:
	@echo "make                  Build firmware"
	@echo "make flash            Build and flash through 1209:B803 bootloader"
	@echo "make clean            Remove build outputs"
	@echo "make size             Show firmware size"
	@echo "make check-deps       Check PoC-specific dependencies"
	@echo "make host             Run host parser self-test"
	@echo "make doctor           Check dependencies, Python, hidapi, and platform"
	@echo "make list             List matching HID devices"
	@echo "make on               Set default vibration level 50"
	@echo "make on 90            Set vibration level 90"
	@echo "make off              Stop vibration"
	@echo "make status           Read current level"
	@echo "make play             Repeat the default pattern until Ctrl+C"
	@echo "make play PATTERN='100:0.1,0:0.4'"

# GNU make treats the level after 'on' as another goal. Swallow only that goal.
.DEFAULT:
	@if [ "$(firstword $(MAKECMDGOALS))" = "on" ] && [ "$@" = "$(word 2,$(MAKECMDGOALS))" ]; then \
	  :; \
	else \
	  echo "Unknown target: $@"; \
	  exit 2; \
	fi
