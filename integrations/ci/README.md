# Integrate with EXISTING company CI only

Do not create a new CI service, GitHub Actions auto-deployment or automatic source modification. Company owners configure this pipeline.

**Fast developer/commit check:** `python <GOLDEN_HOME>/scripts/golden.py check --fast --project <APP_ROOT> --out <LOCAL_EVIDENCE_JSON>`.

**Full pre-release (or app-owner-approved standards-update) check:** `python <GOLDEN_HOME>/scripts/golden.py check --full --project <APP_ROOT> --out <LOCAL_EVIDENCE_JSON>`; render report with `python <GOLDEN_HOME>/scripts/golden.py report --input <LOCAL_EVIDENCE_JSON> --out <LOCAL_REPORT_HTML>`.

The CI runner must use the **same pinned Golden release** verified by company artifact checksum and same registered rule set. Preserve nonzero exit status. Store reports in existing CI artifact store with appropriate authorization, scrubbing and retention. Route non-applicability and company-exception claims through independent company policy. A passing fast check is **never** a full release qualification.

**Warning:** this pilot does not yet implement signed manifest verification, profile auto-detection, company waiver authority or complete mandatory rule coverage. It is a test integration contract, not a ready-made corporate release gate.
