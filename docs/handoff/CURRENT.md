# CURRENT — N95 RM-159 / OMAP2420

Status date: 2026-10-07

## Canonical identity
- Repository: `phai-nguyen/EKA2L1-S60-OMAP2420-iOS`
- Active branch: `n95-rm159`
- Primary device: Nokia N95 RM-159
- Platform: S60 3rd Edition FP1
- Hardware focus: OMAP2420-class compatibility
- Minimum iOS target: 15.0

## Do not mix this project with
- RH-29 / N-Gage QD MACHINE1
- Nokia 5800 RM-356 / CompatBoot / DirectHome / HybridHome
- Nokia N8 RM-596 Phone Mode
- WP7 XAP Runner

Those projects have independent repositories/branches/checkpoints. Do not import their runtime conclusions into this branch unless this repository explicitly asks for a comparison.

## Baseline selected
The iOS baseline was imported from:
- `phai-nguyen/-EKA2L1-iOS-fixed`
- branch `vi-localization-official`
- head `b3840c877cd4eb2f0fd71316a14949b2f6743ce6`

The build workflow currently pins official upstream EKA2L1 commit:
`3afd85d249f4eef16071f6fdbbbf44e49e4072f7`.

Imported baseline features:
- iOS 15 compatibility shims
- Vietnamese localization
- iOS build/repack workflows
- deployment target 15.0
- interpreter-safe signed-build path

## Architecture decision
Keep EKA2L1 as the emulator and Symbian HLE core. Add a narrow OMAP2420/device compatibility layer only when RM-159 firmware evidence demonstrates a missing low-level behavior.

Historical QEMU OMAP2/N8x0 code is donor/reference material, not a drop-in Nokia N95 machine.

## Current implementation state
Project bootstrap is complete.
No OMAP2420 implementation patch has been added yet.
No RM-159 device log has been collected in this repository yet.

## Next engineering task
Survey the pinned EKA2L1 source for:
1. RM-159/N95 device recognition and S60v3 FP1 paths.
2. Current ARM memory-access and exception hooks suitable for device MMIO.
3. Existing device/machine abstraction that can host an N95 profile.
4. Timer/interrupt abstractions that can be extended without breaking HLE.
5. The smallest instrumentation patch needed to collect first RM-159 evidence.

Do not implement broad OMAP2420 MMIO before this survey is complete.

## New-chat starter prompt
Continue the dedicated N95 OMAP2420 project from `docs/handoff/CURRENT.md` in repo `phai-nguyen/EKA2L1-S60-OMAP2420-iOS`, branch `n95-rm159`. This project targets Nokia N95 RM-159 / S60v3 FP1 on iOS 15+. It is separate from RH-29/N-Gage, RM-356/5800, RM-596/N8 and WP7. Read `AGENTS.md`, `docs/checkpoints/LAST_STATE.md`, and the hardware notes before changing code.
