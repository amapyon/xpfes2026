#!/bin/sh
set -eu

cat <<'EOF2'
============================================================
 UIAP Devkit macarm64 0.2.2-test13
 Organizer validation build — not participant-release ready
============================================================
EOF2
printf '\nInitial directory: %s\n\n' "$UIAP_WORKSPACE"
cat <<'EOF2'
Devkit commands:
  setup              Download pinned build tools, Python/hidapi, and sources
  build-minichlink   Build macOS arm64 minichlink locally (organizer only)
  doctor             Check architecture, Python/hidapi, tools, exercises, and blockers
  versions           Show component versions
  report             Write a sanitized diagnostic report under logs/

Required exercises:
  00_onboard_led_blink
  01_macro_keyboard
  02_rotary_cursor_size
  03_vibration_motor_console
  04_rotary_cursor_haptic

Exercise 02 uses one cross-platform host/cursor_size_host.py.
Exercise 03 controls the wired vibration module from make commands.
Exercise 04 combines the cursor host with haptic feedback.
Use cd to enter an exercise, then run its make targets.
Do not use this test package for participants until validation is complete.
EOF2
