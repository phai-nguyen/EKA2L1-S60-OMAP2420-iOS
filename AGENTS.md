# Project instructions

This repository is the dedicated EKA2L1 S60 OMAP2420 iOS project.

## Canonical target
Nokia N95 RM-159 first. Minimum iOS target is 15.0.

## Hard scope boundary
Do not continue or revive work from RH-29/N-Gage MACHINE1, RM-356 Nokia 5800, CompatBoot, DirectHome, HybridHome, RM-596/N8 Phone Mode, or WP7 unless the current repository documentation explicitly asks for a comparison.

## Required reading order
1. `docs/handoff/CURRENT.md` on the active branch.
2. `docs/checkpoints/LAST_STATE.md`.
3. `docs/PROJECT_SCOPE.md`.
4. Relevant files under `docs/hardware/`.

## Engineering policy
- Preserve the existing EKA2L1 Symbian HLE architecture.
- Add hardware compatibility only where device evidence requires it.
- Prefer exact trace/evidence over broad RAM/MMIO mappings or guessed stubs.
- Treat QEMU OMAP2/N8x0 code as donor/reference material, not as proof that Nokia N95 board wiring is identical.
- Do not merge device-specific behavior into common code until it is shown to be shared.
- Keep iOS 15 compatibility unless an unavoidable API dependency is demonstrated.
