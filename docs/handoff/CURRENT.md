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
- build workflow applies and verifies marker `N95OMAP-PROBE1`.
- iOS diagnostic log pack `N95OMAP-LOGPACK1`: `EKA2L1.log`, `EKA2L1_TakeThis.log`, `EKA2L1_Persistent.log`, `EKA2L1_Persistent-prev.log` under `Documents/data/`.

PROBE1 logs EKA2 access violations with direction, address, PC, LR, CPSR and thread. The current patch logs every such violation and relies on the RM-159 device-test contract for this branch; it does not gate by firmware identity or latch only the first fault. It deliberately does not fabricate MMIO values or broad-map memory.

Latest verified build result: [run 37699382879](https://github.com/phai-nguyen/EKA2L1-S60-OMAP2420-iOS/actions/runs/37699382879) on commit `85359e5` passed the iOS build, iOS 15 and Vietnamese resource checks, and published both unsigned IPA variants. The build workflow uses a shallow fetch of the pinned upstream commit and parallel shallow submodules; run 37670989308 measured source checkout at 2m21s versus about 3m30s before that optimization. The incremental Xcode, FFmpeg and base-app caches remain in place. See `docs/checkpoints/LAST_STATE.md` for build evidence.

No RM-159 device log has been collected from this repository yet.

## VPL firmware import
The iOS device installer has a VPL/FPSX source. Users can choose the folder containing `.vpl` and adjacent `.fpsx` files, then select the VPL in that folder. After comparing the dedicated project's implementation with `phai-nguyen/-EKA2L1-iOS-fixed` on `main` at `2d17242`, a second Files picker path was added: select the VPL and all of its firmware files together when Files will not select the current folder. That path copies the chosen files into a temporary app folder, installs, then removes the temporary copies. The folder path keeps its security scope open throughout installation. Both call the existing EKA2L1 firmware installer and select the first VPL variant as the Android frontend does. ROM/RPKG and 7z import remain available. [iOS build 37680419814](https://github.com/phai-nguyen/EKA2L1-S60-OMAP2420-iOS/actions/runs/37680419814) verified compilation and packaging of both picker paths. RM-159 device testing is pending.

An on-device report says both VPL selection methods show the chosen VPL, but tapping Install gives no visible response; Cancel still works. Commit `85359e5` makes an invalid selection or firmware install failure appear in an alert instead of silently returning or showing an easily missed inline message. [Build 37699382879](https://github.com/phai-nguyen/EKA2L1-S60-OMAP2420-iOS/actions/runs/37699382879) passed. The root cause of the on-device installation failure is not established; request the new alert text and `EKA2L1.log` from the device after retesting.

## Next engineering task
1. Verify the iOS build containing `N95OMAP-PROBE1`.
2. Install an RM-159 firmware on that build.
3. Capture the first exact `N95OMAP-PROBE1` line and surrounding log.
4. Classify that address using RM-159/OMAP2420 evidence and QEMU donor code.
5. Only then design the first real MMIO/register behavior.

## New-chat starter prompt
Continue the dedicated N95 OMAP2420 project from `docs/handoff/CURRENT.md` in repo `phai-nguyen/EKA2L1-S60-OMAP2420-iOS`, branch `n95-rm159`. This project targets Nokia N95 RM-159 / S60v3 FP1 on iOS 15+. It is separate from RH-29/N-Gage, RM-356/5800, RM-596/N8 and WP7. Read `AGENTS.md`, `docs/checkpoints/LAST_STATE.md`, and the hardware notes before changing code.


## RM-159 firmware import diagnosis — 2026-10-08
The device log from EKA2L1 iOS v26.7.0 (HEAD-3afd85d) stops after the ROFS parser warns about an untested ROFx variant and emits 1,666 short-read warnings from rofs.cpp:150. The regular and Persistent log files are byte-identical. This matches the failure signature in upstream issue #499 for an N82 VPL import.

The pinned ROFS extractor subtracts the ROFS file base from an unsigned file address and attempts to extract every entry as payload data. RM-159 ROFx has entries that point back to files supplied by the core ROM image. Those references must leave the already-extracted ROM files intact. The new N95ROFS-EXTLINK1 patch skips addresses below the ROFS data base, validates each in-image range before creating a file, and propagates short-read/write failures so malformed data stops with an error instead of appearing to finish at 100%.

The patch and its workflow regression check are committed; iOS build and on-device retest are pending. No OMAP2420 hardware behavior has been changed.