# LAST STATE — N95 RM-159

Status: PROBE1 COMMITTED — BUILD/DEVICE EVIDENCE PENDING

## Completed
- Created dedicated repository `phai-nguyen/EKA2L1-S60-OMAP2420-iOS`.
- Established `main` as the common iOS 15+ baseline.
- Created active branch `n95-rm159`.
- Imported the iOS 15 compatibility patch and Vietnamese localization catalogs.
- Added dedicated build/repack workflows targeting iOS 15.0.
- Added hard project-boundary documentation and `AGENTS.md`.
- Added OMAP2420, N95 RM-159, and QEMU donor research notes.

## Additional completed work
- Surveyed the pinned EKA2L1 memory/exception path.
- Confirmed RM-159 device recognition already exists upstream.
- Identified `kernel_system::cpu_handle_access_violation` as a clean first diagnostic interception point.
- Added RM-159-only `N95OMAP-PROBE1` logging with read/write, address, PC, LR, CPSR and thread.
- Updated the iOS build workflow to apply and statically verify PROBE1.

## Not done
- PROBE1 build result has not yet been verified in this checkpoint.
- No OMAP2420 MMIO implementation yet.
- No RM-159 firmware device log from PROBE1 yet.
- No N82/N93/E90 branches yet.

## Invariants
- Keep minimum iOS target at 15.0 unless a proven blocker requires otherwise.
- Keep N95 work isolated from N-Gage, Nokia 5800, N8, and WP7 projects.
- Do not broad-map memory/MMIO to force progress.
- Do not assume N800/N810 board behavior equals N95 behavior.
- Prefer exact PC/LR/address/value evidence before implementing hardware behavior.

## Next checkpoint condition
Advance this checkpoint after the PROBE1 iOS build passes and a real RM-159 run yields the first exact access-violation evidence.
