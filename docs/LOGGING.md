# Diagnostic Logs — N95 OMAP2420 iOS

Status date: 2026-10-07

This branch restores the four-file device-test log set used in earlier iOS debugging builds.

## Files

All files are written under the app's user-visible `Documents/data/` directory:

- `EKA2L1.log` — current launch. Existing upstream behavior.
- `EKA2L1_TakeThis.log` — previous launch's normal log. Existing upstream rotation.
- `EKA2L1_Persistent.log` — cumulative diagnostic log across launches. It appends instead of truncating and remains bounded by EKA2L1's normal log line cap.
- `EKA2L1_Persistent-prev.log` — snapshot of the persistent log taken immediately before the current launch starts writing.

The persistent pair is added by `patches/code/apply-ios-diagnostic-logs.py` and is iOS-only.

## Why four files

A crash or forced termination can make the final visible session ambiguous. Keeping both the current/previous normal logs and the cumulative/snapshot persistent logs gives enough overlap to recover:
- the last lines before a crash;
- the prior launch when the app restarts;
- repeated boot attempts across multiple launches;
- N95 OMAP2420 probe markers such as `N95OMAP-PROBE1`.

## Retention

The persistent log uses the same capped-file mechanism and line budget as the ordinary EKA2L1 log. It therefore does not grow without bound.

## Device-test request

For a failed N95 RM-159 test, prefer sending all four files when they exist. On the first launch, `EKA2L1_Persistent-prev.log` may not exist yet.
