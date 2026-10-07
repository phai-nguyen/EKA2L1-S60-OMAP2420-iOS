# QEMU Donor Notes

## Reference source
Primary donor/reference family: UTM's QEMU fork and historical QEMU OMAP2/N8x0 support.

Useful historical files include:
- `hw/arm/omap2.c`
- `hw/arm/nseries.c`
- `include/hw/arm/omap.h`

## Usage policy
- Read behavior and register models.
- Cross-check with public chipset/device documentation.
- Validate against RM-159 firmware traces.
- Reimplement the minimum required behavior in the EKA2L1 architecture.
- Check the license header of any QEMU file before directly copying code.

## Non-goal
Do not embed a complete QEMU VM inside EKA2L1 as the first approach.
