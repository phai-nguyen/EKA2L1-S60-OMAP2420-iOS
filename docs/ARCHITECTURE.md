# Architecture

## Principle

EKA2L1 remains the emulator. The project adds a device-aware hardware compatibility layer only for low-level behavior that S60/OMAP2420 firmware actually requires.

```
EKA2L1
├── Symbian kernel/HLE
├── services / filesystem / graphics / audio / input
├── ARM backends
│   ├── Dynarmic
│   ├── Dyncom
│   └── R12L1 where applicable
└── hardware compatibility
    ├── common OMAP2420 behavior
    └── device profile
        └── Nokia N95 RM-159
```

## Initial compatibility surfaces

The first implementation work should focus on evidence-backed behavior in:
- memory map and aliases;
- interrupt delivery / IRQ-FIQ routing;
- timers and clocks;
- essential MMIO register reads/writes;
- boot-critical flash/storage behavior.

Camera, WLAN, GPS, modem, multimedia acceleration, and other non-boot-critical devices are deferred.

## QEMU relationship

Historical QEMU OMAP2/Nokia N8x0 implementations are reference/donor material. They can clarify register models and timing/interrupt structure, but N800/N810 are not N95 boards. Every reused idea must be validated against N95 firmware behavior or device documentation.

## iOS

Keep the minimum deployment target at 15.0. Existing compatibility shims provide iOS 15 fallbacks for newer SwiftUI APIs. CPU execution strategy stays with EKA2L1 until evidence shows a CPU-backend defect that requires a different backend.
