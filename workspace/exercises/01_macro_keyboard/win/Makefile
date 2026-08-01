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

TARGET_MCU := CH32V003
MCU_PACKAGE := 1
PREFIX := riscv-none-elf
ADDITIONAL_C_FILES += $(RV003USB)/rv003usb/rv003usb.S $(RV003USB)/rv003usb/rv003usb.c
EXTRA_CFLAGS += -I$(RV003USB)/rv003usb -I$(CURDIR_POSIX)
# Use recursive assignment: $< is defined only while the cv_flash recipe runs.
FLASH_COMMAND = "$(MINICHLINK)/minichlink" -c 0x1209b803 -w $< $(WRITE_SECTION) -b

TARGET := macro_keyboard

include $(CH32FUN)/ch32fun.mk

all: build
flash: cv_flash
clean: cv_clean
size: build
	$(PREFIX)-size $(TARGET).elf
hidcheck:
	"$(UIAP_PYTHON)" "$(CURDIR_POSIX)/host/hidcheck.py"
app: hidcheck
doctor:
	"$(UIAP_PYTHON)" "$(CURDIR_POSIX)/host/hidcheck.py" --self-test
help:
	@echo make
	@echo make flash
	@echo make clean
	@echo make size
	@echo make hidcheck
	@echo make doctor

.PHONY: all flash clean size hidcheck app doctor help
