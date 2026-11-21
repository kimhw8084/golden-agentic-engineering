# React dependency license supplements

This directory holds three root license files from the exact upstream commits corresponding to installed package versions in the macOS arm64 dependency audit. Words and punctuation are preserved; trailing whitespace and extra final blank lines were removed. Manifest hashes normalize CRLF to LF so Windows and Linux validate the same text. The source and copied-file SHA-256 values are recorded in [the supplement manifest](../react-license-supplements.json).

These are **supplemental upstream notices**, not files recovered from the npm tarballs. The package tarballs still lack their own license files: the audit count remains four. The Rollup source notice also includes notices for bundled dependencies; it is preserved in full.

The fourth package is `stackback@0.0.2`. Its pinned archived upstream `package.json` and the official npm record declare MIT; the exact upstream source-file blob hashes match the installed package files. The package has no root `LICENSE` file. Its `formatstack.js` also preserves a full BSD-3-Clause notice for V8-derived code. No MIT text was invented or copied. The standalone MIT notice gap remains open; see [`stackback source audit`](../stackback-0.0.2-source-audit.md) and the manifest for the exact pins and company action.

This evidence does not complete transitive/platform dependency review, prove an offline Windows/Linux package, or grant company OSS/legal approval. Company clearance remains pending.
