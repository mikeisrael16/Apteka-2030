#!/bin/sh
# Smoke test on an emulator: install, start, wait for the menu, start a new game, check the app is alive.
PKG=com.mikhailgamestudio.apteka2030
OUT=${1:-out}; mkdir -p "$OUT"
set -x
adb install -r app-debug.apk || exit 1
adb logcat -c
adb shell am start -W -n $PKG/.MainActivity || exit 1
sleep 30
adb exec-out screencap -p > "$OUT/1_menu.png"
SIZE=$(adb shell wm size | tr -d '\r' | sed 's/.*: //' | tail -n 1); W=${SIZE%x*}; H=${SIZE#*x}
adb shell input tap $((W/2)) $((H*675/1000))        # NEW GAME
sleep 12
adb exec-out screencap -p > "$OUT/2_game.png"
adb shell input keyevent KEYCODE_HOME; sleep 3      # background → foreground
adb shell am start -W -n $PKG/.MainActivity; sleep 5
adb shell input keyevent KEYCODE_BACK; sleep 2      # exit dialog
adb exec-out screencap -p > "$OUT/3_back.png"
adb logcat -d > "$OUT/logcat.txt"
PID=$(adb shell pidof $PKG | tr -d '\r')
grep -E "Apteka2030|FATAL EXCEPTION|AndroidRuntime" "$OUT/logcat.txt" | tail -n 60 > "$OUT/summary.txt"
echo "pid=$PID size=$SIZE" >> "$OUT/summary.txt"
RES=OK
[ -z "$PID" ] && RES="FAIL: app is not running"
grep -q "FATAL EXCEPTION" "$OUT/logcat.txt" && grep -A3 "FATAL EXCEPTION" "$OUT/logcat.txt" | grep -q "$PKG" && RES="FAIL: crash"
grep -q "game boot check: \"object\"" "$OUT/logcat.txt" || RES="FAIL: game script did not start"
grep -q "Apteka2030: JS:" "$OUT/logcat.txt" && RES="$RES (JS errors logged)"
echo "RESULT $RES" >> "$OUT/summary.txt"; cat "$OUT/summary.txt"
case "$RES" in OK*) exit 0;; *) exit 1;; esac
