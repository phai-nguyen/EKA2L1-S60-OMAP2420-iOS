# iOS 15 Baseline

## Provenance
Imported from:
- repository: `phai-nguyen/-EKA2L1-iOS-fixed`
- branch: `vi-localization-official`
- branch head used for project creation: `b3840c877cd4eb2f0fd71316a14949b2f6743ce6`

The build workflow pins official EKA2L1 source commit:
`3afd85d249f4eef16071f6fdbbbf44e49e4072f7`.

## Imported baseline files
- `patches/code/apply-ios15-compat.py`
- `patches/Localizable.xcstrings`
- `patches/InfoPlist.xcstrings`
- `.github/workflows/build-ios15-omap2420.yml`
- `.github/workflows/repack-ios15-omap2420.yml`

## Build policy
- Minimum deployment target: iOS 15.0.
- Preserve Vietnamese localization.
- Preserve Files/VPL compatibility behavior from the selected baseline.
- For signed/archive builds, do not assume executable-memory/JIT availability.
- New OMAP2420 work should be isolated from UI compatibility changes whenever possible.
