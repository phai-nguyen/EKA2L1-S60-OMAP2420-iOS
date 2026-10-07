# Project Scope

## Project identity
Repository: `phai-nguyen/EKA2L1-S60-OMAP2420-iOS`

Purpose: extend EKA2L1 with a narrowly scoped hardware-compatibility layer for S60 devices built around OMAP2420-class hardware, starting with Nokia N95 RM-159.

## First milestone
Boot/install the selected N95 firmware far enough to obtain deterministic runtime evidence, then progress through required memory/MMIO/timer/IRQ behavior without replacing EKA2L1's existing Symbian HLE unnecessarily.

## Supported development order
1. Nokia N95 RM-159.
2. Nokia N82 RM-313 only after reusable OMAP2420 behavior is proven.
3. Nokia N93 RM-55 after the common layer is stable.
4. Nokia E90 only after display/input differences are explicitly modeled.

## Out of scope
- RH-29 / N-Gage QD MACHINE1.
- Nokia 5800 RM-356.
- CompatBoot / DirectHome / HybridHome.
- Nokia N8 RM-596 Phone Mode.
- WP7 XAP Runner.
- Blind import of full QEMU machine models.
- Broad MMIO/RAM mappings added without device evidence.

## Baseline
The iOS compatibility baseline is derived from `phai-nguyen/-EKA2L1-iOS-fixed`, branch `vi-localization-official`, commit `b3840c877cd4eb2f0fd71316a14949b2f6743ce6`.

Minimum deployment target: iOS 15.0.
