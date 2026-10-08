# EKA2L1 insertion-point survey — 2026-10-07

Pinned upstream surveyed: `EKA2L1/EKA2L1@3afd85d249f4eef16071f6fdbbbf44e49e4072f7`.

## Confirmed RM-159 recognition
`src/emu/system/src/devices.cpp` already contains:
- `rm-159 -> 0x2000060B` (Nokia N95)
- related N95/N82/N93 entries are also present.

Therefore PROBE1 does not need to invent a new device identifier.

## CPU memory path
`src/emu/mem/src/mmu.cpp` installs the CPU read/write callbacks:
- `read_8bit/read_16bit/read_32bit/read_64bit`
- `write_8bit/write_16bit/write_32bit/write_64bit`

Dynarmic calls these callbacks. When a callback fails, `arm_dynarmic.cpp` raises an access-violation exception and may retry if the exception handler reports that the fault was repaired.

Dyncom/12l1r follow the same high-level contract: failed memory access can be passed to the CPU exception handler.

## Existing access-violation behavior
`src/emu/kernel/src/kernel.cpp` contains:
`kernel_system::cpu_handle_access_violation(arm::core *, address, bool)`.

At the pinned baseline it only repairs a specific EKA1 kernel-mapping case by creating a stub I/O mapping. EKA2 access violations otherwise return false.

This makes it a clean first diagnostic point for N95 because it receives:
- core pointer;
- fault address;
- read/write direction;
- current thread through the kernel;
- PC/LR/CPSR from the core.

## Important design constraint
The current access-violation callback receives the fault address but not the write payload. It is ideal for PROBE1 diagnostics, but not sufficient as the final MMIO dispatcher.

For real OMAP2420 register emulation, the likely clean architecture is a device/MMIO layer reached from the MMU read/write path so reads can return values and writes can consume values with side effects. Do not fake this by broad-mapping pages.

## Device gating
`kernel_system` owns `system *sys_`, and `system` exposes `get_device_manager()`; the current device exposes `firmware_code`. Therefore instrumentation can be restricted to RM-159 instead of polluting all devices.

## Decision
First patch: N95 OMAP2420 PROBE1.

PROBE1 only logs an RM-159 access violation with:
- read/write;
- fault address;
- PC;
- LR;
- CPSR;
- thread name.

It does not map memory, return fabricated register values, or claim any address is an OMAP2420 register.

After the first device log, the exact failing address and calling code determine the next implementation step.
