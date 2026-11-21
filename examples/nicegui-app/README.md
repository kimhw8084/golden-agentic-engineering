# Synthetic NiceGUI measurement review

This local-only example accepts synthetic sample values and displays state, validation errors, and an accessible live status. It contains no company data, database, telemetry, external service, or production write.

With NiceGUI staged locally:

```sh
python -m unittest discover -s tests -v
python -m app.main
```

Run `python -m unittest discover -s tests -v` for the standard-library logic tests. With NiceGUI and pytest installed, run `pytest -q tests/test_ui.py` for an in-process `user_simulation` UI test; no browser is needed. Golden Proof's full check runs `ui_contracts` through its pytest allowlist and marks it `NOT_RUN` when pytest or NiceGUI is unavailable. Start the app with `python -m app.main` from this directory and open `http://127.0.0.1:8080`. A formal accessibility audit remains unrun because no per-platform browser bundle is staged.
