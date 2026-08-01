.DEFAULT_GOAL := all

ifndef UIAP_PLATFORM
$(error UIAP_PLATFORM is not set. Start with start-uiap.cmd or start-uiap.command)
endif
ifeq ($(filter $(UIAP_PLATFORM),win mac),)
$(error UIAP_PLATFORM must be win or mac)
endif

PLATFORM_DIR := $(UIAP_PLATFORM)

.PHONY: all flash clean size hidcheck list app app-dry-run cursor-test restore doctor host-doctor report help
all flash clean size hidcheck list app app-dry-run cursor-test restore help:
	@$(MAKE) -C $(PLATFORM_DIR) $@

doctor:
	@doctor

report:
	@report

host-doctor:
	@$(MAKE) -C $(PLATFORM_DIR) doctor
