# Bootstrap package local test record

**Date:** November 19, 2026  
**Environment:** this ChatGPT Linux container, Python 3.11+, no company OpenCode attached  
**Product state:** v0.1.0-dev, NOT approved or company qualified

The following local commands were executed and their outcomes inspected:

| Validation | Result |
|---|---|
| Python standard-library unittest suite | PASS — 14 tests |
| `golden.py check --fast` on included Python fixture | PASS for applicable fast checks; full checks DEFERRED |
| `golden.py check --full` on included Python fixture | Correctly NOT RELEASE-QUALIFIED (not a Git worktree, unconfigured Python lint/security commands) |
| JSON evidence generated and standalone HTML report rendered | PASS — demonstrable local files |
| Public-repository staging command run without `--apply` | PASS — dry-run lists candidates without network or file creation |
| Installer and app bootstrap dry-run/non-overwrite tests | PASS in local tests |
| Source-file SHA verification after ZIP extraction | Included as `scripts/verify_contents.py`; separately retested during packaging |
| Internal company OpenCode actual model/agents/skills | NOT_RUN |
| Windows company device and separate Linux corporate OS | NOT_RUN |
| Public downloads, binary provenance, OSI/license and security clearance | NOT_RUN |
| Real React/NiceGUI company application benchmarks | NOT_RUN |
| Company CI / artifact repository / waiver integration | NOT_RUN |

**Known limitations:** The starter's 19 pilot rule descriptors do not implement the complete 151 proposed requirements; applicability is based on declared capability flags; it lacks company-waiver management and signed release integrity verification; most real full checks need approved qualified external tools. This document does not assert readiness for team release.
