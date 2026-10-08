#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
kernel = root / "src/emu/kernel/src/kernel.cpp"

text = kernel.read_text(encoding="utf-8")

if "N95OMAP-PROBE1" in text:
    print("N95 OMAP2420 PROBE1 already applied")
    raise SystemExit(0)

old = """    bool kernel_system::cpu_handle_access_violation(arm::core *core, const address occurred, const bool read) {
        if (is_eka1()) {
"""
new = """    bool kernel_system::cpu_handle_access_violation(arm::core *core, const address occurred, const bool read) {
        // This branch is dedicated to N95 RM-159. Keep PROBE1 inside the kernel target
        // without importing the system module (epockern does not expose system/devices.h
        // in its include path). Restrict it to EKA2 and use the branch/device-test
        // contract to identify RM-159 evidence.
        if (!is_eka1()) {
            kernel::thread *thr = crr_thread();
            LOG_ERROR(KERNEL,
                "N95OMAP-PROBE1 access={} addr=0x{:08X} pc=0x{:08X} lr=0x{:08X} cpsr=0x{:08X} thread={}",
                read ? "read" : "write",
                occurred,
                core ? core->get_pc() : 0,
                core ? core->get_lr() : 0,
                core ? core->get_cpsr() : 0,
                thr ? thr->name() : std::string("<none>"));
        }

        if (is_eka1()) {
"""
if old not in text:
    raise SystemExit("PROBE1: cpu_handle_access_violation anchor not found")
text = text.replace(old, new, 1)

kernel.write_text(text, encoding="utf-8")
print("Applied N95 OMAP2420 PROBE1")
