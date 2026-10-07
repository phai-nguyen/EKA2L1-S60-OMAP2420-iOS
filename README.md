# EKA2L1 S60 OMAP2420 iOS

Dedicated repository for the S60/OMAP2420 hardware-compatibility work on EKA2L1 for iOS.

## Active target

- Nokia N95 RM-159
- S60 3rd Edition FP1
- OMAP2420-class hardware compatibility
- Minimum iOS target: 15.0
- Base iOS compatibility lineage: `phai-nguyen/-EKA2L1-iOS-fixed@vi-localization-official`
- Baseline commit: `b3840c877cd4eb2f0fd71316a14949b2f6743ce6`
- Official EKA2L1 source pinned by the build workflow: `3afd85d249f4eef16071f6fdbbbf44e49e4072f7`

## Scope boundary

This repository is intentionally separate from:

- RH-29 / N-Gage QD MACHINE1
- Nokia 5800 RM-356 / CompatBoot / DirectHome / HybridHome
- Nokia N8 RM-596 Phone Mode
- WP7 XAP Runner

Do not import assumptions, checkpoints, patches, or handoff state from those projects unless a document in this repository explicitly requests a comparison.

## Repository layout

- `patches/` — iOS 15 compatibility and localization patches
- `.github/workflows/` — iOS 15 build/repack workflows
- `docs/PROJECT_SCOPE.md` — authoritative project boundary
- `docs/ARCHITECTURE.md` — planned EKA2L1 + OMAP2420 compatibility architecture
- `docs/hardware/` — hardware research notes
- `docs/handoff/CURRENT.md` — canonical current state for a new chat
- `docs/checkpoints/LAST_STATE.md` — last verified implementation checkpoint

## Branch policy

- `main` — common iOS 15+ baseline and shared documentation
- `n95-rm159` — first active implementation branch
- Future device branches are created only after N95 evidence justifies reuse.

Always read `docs/handoff/CURRENT.md` on the branch named by the user before continuing implementation.
