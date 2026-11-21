# NiceGUI local browser smoke — 2026-11-20

**Result:** PASS for the synthetic local app's basic interaction flow.

**Environment:** macOS 25.6.0 arm64, Python 3.11.7, NiceGUI 3.15.0. The app was served on loopback at `http://127.0.0.1:8080/` and inspected in the in-app browser. Inputs and status/error/result elements were exposed with accessible labels or roles.

## Observed interactions

1. Submitting an empty Sample ID displayed `Sample ID is required.` while keeping the status at `No measurement submitted.`
2. Submitting `S-ACCEPT` at value `0` with limits `0`–`10` produced `ACCEPT` and updated the count to Accepted 1, Review 0.
3. Submitting `S-REVIEW` at value `11` with limits `0`–`10` produced `REVIEW` and updated the count to Accepted 1, Review 1.
4. Reusing `S-ACCEPT` displayed `Sample ID has already been evaluated.` and left the counts unchanged.
5. Clear results emptied the result list, reset counts to zero, cleared the alert, and restored `No measurement submitted.`

This was a manual in-app browser smoke check, not a Playwright run or formal accessibility audit. It does not qualify the fixture on other OS versions or company-managed environments. The separate browserless `user_simulation` test is run with `pytest -q tests/test_ui.py` from `examples/nicegui-app`.
