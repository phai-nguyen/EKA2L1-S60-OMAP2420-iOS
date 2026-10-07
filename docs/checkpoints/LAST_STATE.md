# LAST STATE — N95 RM-159

Status: PROBE1 IOS BUILD PASSED — DEVICE EVIDENCE PENDING

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
- Added EKA2 `N95OMAP-PROBE1` logging with read/write, address, PC, LR, CPSR and thread. The current patch relies on testing RM-159 on this branch; it does not check the firmware identity at runtime.
- Updated the iOS build workflow to apply and statically verify PROBE1.

## Build investigation — 2026-10-07
- Run [37625926247](https://github.com/phai-nguyen/EKA2L1-S60-OMAP2420-iOS/actions/runs/37625926247), commit `85a5089af76217d8ff5503a13b7b7b22ea3ead49`, failed during Swift compilation with Xcode 26.6.
- iOS 15, LOGPACK1 and PROBE1 patch stages all passed. No IPA was packaged.
- Compiler error: `IOS15Compat.swift:170`: `CompatAnyShape` conforms to `Sendable` through `Shape`, but stored closure `makePath` has non-Sendable type `(CGRect) -> Path`.
- Updated the generated closure type to `@Sendable (CGRect) -> Path`; run 37632331108 verified successful app compilation.
- All three patches apply successfully to pinned upstream `3afd85d249f4eef16071f6fdbbbf44e49e4072f7`; generated-source whitespace checks pass. These checks do not establish iOS build success.
- Run [37632331108](https://github.com/phai-nguyen/EKA2L1-S60-OMAP2420-iOS/actions/runs/37632331108), commit `fa9c81f079722b6f5d04956c7f6f8a4cf7d91fb5`, reported `BUILD SUCCEEDED` but failed deployment verification: `MinimumOSVersion=15` did not match the required string `15.0`. Resource verification and IPA packaging were skipped.
- Both build/repack workflows now quote deployment target as `"15.0"`, preserving the version string instead of YAML numeric coercion. Local YAML parsing verified the string type and exact value; subsequent full builds passed deployment verification.
- Run [37663349331](https://github.com/phai-nguyen/EKA2L1-S60-OMAP2420-iOS/actions/runs/37663349331), commit `b5a4833644462fd1cdc4d9b79ce8555153e0eae2`, passed every build, verification and packaging step and published both unsigned IPA variants.
- That run took about 31 minutes. Its ccache restore missed and the post-job save reported that the cache directory did not exist. CMake's compiler launcher only applies to Make/Ninja generators; the iOS script uses Xcode. Removed the unused ccache installation/cache steps, kept the Xcode/FFmpeg/base-app caches, and switched upstream retrieval to a pinned shallow fetch plus eight parallel shallow submodule jobs. A clean local checkout verified the exact upstream SHA and all 47 recursive submodules; run 37670989308 measured the checkout speedup.
- Run [37670989308](https://github.com/phai-nguyen/EKA2L1-S60-OMAP2420-iOS/actions/runs/37670989308), commit `6af1b7c`, passed; source checkout took 2m21s versus about 3m30s before the optimization.
- Added an iOS VPL/FPSX import path on top of the existing EKA2L1 firmware installer. It lets users choose a security-scoped firmware folder and a VPL within it, using the first VPL variant. Local patch composition against the pinned upstream passed. [Run 37673462081](https://github.com/phai-nguyen/EKA2L1-S60-OMAP2420-iOS/actions/runs/37673462081), commit `741ffc5`, passed the VPL patch stage, app build, iOS 15/Vietnamese verification and both IPA packaging stages. An RM-159 on-device install/run is pending.
- Compared the VPL picker in `phai-nguyen/-EKA2L1-iOS-fixed` `main@2d17242`: iOS Files may not let the user select the folder currently open, so that repo offers multi-file selection and stages the chosen VPL/FPSX files in the app sandbox. Added the same fallback to this branch without importing its unrelated phone/runtime code. Selected files are staged temporarily with their original names, installed via EKA2L1, and removed afterward. [Run 37680419814](https://github.com/phai-nguyen/EKA2L1-S60-OMAP2420-iOS/actions/runs/37680419814), commit `819f9b6`, passed app build, iOS 15 and Vietnamese verification, and both IPA uploads. RM-159 device validation remains pending.
- User reported that both folder and multi-file selection display the VPL name, but tapping Install gives no visible response while Cancel still works. The selected VPL row confirms picker recognition, but the install result is unknown. Commit `85359e5` surfaces invalid selection and firmware installation failures in an alert. [Run 37699382879](https://github.com/phai-nguyen/EKA2L1-S60-OMAP2420-iOS/actions/runs/37699382879) passed build, deployment/resource checks and both IPA uploads. Await the alert text or device `EKA2L1.log` before attributing the failure to a specific installer stage.

## Not done
- No RM-159 on-device VPL install or PROBE1 runtime log yet.
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
