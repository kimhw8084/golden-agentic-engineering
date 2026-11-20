# Synthetic NiceGUI measurement review

This local-only example accepts synthetic sample values and displays state, validation errors, and an accessible live status. It contains no company data, database, telemetry, external service, or production write.

With NiceGUI staged locally:

```sh
python -m unittest discover -s tests -v
python app/main.py
```

Open `http://127.0.0.1:8080`. Browser-based UI testing is not yet configured because a per-platform Playwright browser bundle has not been staged. The pure acceptance logic is covered by standard-library tests.
