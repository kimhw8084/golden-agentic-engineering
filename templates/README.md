# Example profiles — commands must be adapted to REAL project scripts

These manifest templates demonstrate the intended React and NiceGUI Golden profiles. They do not install dependencies, create application code or claim qualified checks. Ensure the command arrays invoke real approved local commands whose runtime assets, browser binaries, Node/Python stores and licenses have been staged offline. A command that does not exist results in `NOT_RUN` or `FAIL`, not PASS. Set declared capabilities based on the real app and independently validate them; absence is not proof of NOT_APPLICABLE.

For a new project use `python scripts/bootstrap_project.py --target PATH --name NAME --profile react|nicegui --apply` and replace its default command/capability settings from the applicable template after inspecting the actual repository.
