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
Project bootstrap and first source survey are complete.

Confirmed in pinned upstream:
- RM-159 is already recognized as Nokia N95.
- CPU memory accesses are routed through the EKA2L1 MMU callbacks.
- Failed accesses reach `kernel_system::cpu_handle_access_violation`.
- The existing EKA2 handler does not repair unknown hardware accesses.
- `kernel_system` can reach the current device, so diagnostics can be gated to RM-159.

Committed:
- research note: `docs/research/EKA2L1-INSERTION-POINTS-2026-10-07.md`
- first diagnostic patch: `patches/code/apply-n95-omap2420-probe1.py`
- build workflow now applies and verifies marker `N95OMAP-PROBE1`.

PROBE1 only records the first unsupported RM-159 access with direction, address, PC, LR, CPSR and thread. It deliberately does not fabricate MMIO values or broad-map memory.

No RM-159 device log has been collected from this repository yet.

## Next engineering task
1. Verify the iOS build containing `N95OMAP-PROBE1`.
2. Install an RM-159 firmware on that build.
3. Capture the first exact `N95OMAP-PROBE1` line and surrounding log.
4. Classify that address using RM-159/OMAP2420 evidence and QEMU donor code.
5. Only then design the first real MMIO/register behavior.

## New-chat starter prompt
Continue the dedicated N95 OMAP2420 project from `docs/handoff/CURRENT.md` in repo `phai-nguyen/EKA2L1-S60-OMAP2420-iOS`, branch `n95-rm159`. This project targets Nokia N95 RM-159 / S60v3 FP1 on iOS 15+. It is separate from RH-29/N-Gage, RM-356/5800, RM-596/N8 and WP7. Read `AGENTS.md`, `docs/checkpoints/LAST_STATE.md`, and the hardware notes before changing code.
