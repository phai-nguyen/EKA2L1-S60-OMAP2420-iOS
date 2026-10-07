# LAST STATE — N95 RM-159

Status: BOOTSTRAP COMPLETE

## Completed
- Created dedicated repository `phai-nguyen/EKA2L1-S60-OMAP2420-iOS`.
- Established `main` as the common iOS 15+ baseline.
- Created active branch `n95-rm159`.
- Imported the iOS 15 compatibility patch and Vietnamese localization catalogs.
- Added dedicated build/repack workflows targeting iOS 15.0.
- Added hard project-boundary documentation and `AGENTS.md`.
- Added OMAP2420, N95 RM-159, and QEMU donor research notes.

## Not done
- No OMAP2420 MMIO implementation yet.
- No N95-specific runtime instrumentation yet.
- No RM-159 firmware test from this repository yet.
- No N82/N93/E90 branches yet.

## Invariants
- Keep minimum iOS target at 15.0 unless a proven blocker requires otherwise.
- Keep N95 work isolated from N-Gage, Nokia 5800, N8, and WP7 projects.
- Do not broad-map memory/MMIO to force progress.
- Do not assume N800/N810 board behavior equals N95 behavior.
- Prefer exact PC/LR/address/value evidence before implementing hardware behavior.

## Next checkpoint condition
Advance this checkpoint only after the EKA2L1 source survey identifies the exact insertion points for N95 hardware compatibility and the first diagnostic patch is committed.
