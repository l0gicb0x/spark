# How Much Is Done: Project SPARK Phase 1

## Current assessment

**Phase 1 is implemented, but not fully verified and should not be called complete yet.** The code, documentation, and automated tests for the Phase 1 foundation are present. Several Windows and live-service acceptance checks still require a deliberate manual run.

I’m not assigning a percentage: the remaining items are acceptance checks that can pass or fail independently, and a percentage would imply more precision than the evidence supports.

## Verified

- **VERIFIED — Project and implementation:** the Phase 1 source tree, pinned package configuration, settings, logging, keyring wrapper, channel interfaces, local commands, Qt window, tray code, Gemini connection test, and Phase 1 docs exist in the repository.
- **VERIFIED — Automated tests (historical baseline):** the pre-follow-up run reported `32 passed in 10.81s`; the current post-fix result is recorded below with an external pytest base and cache directory.
- **VERIFIED — Lint:** Ruff reported `All checks passed!`.
- **VERIFIED — GUI observation:** the app window opened on Windows, showed the first-run welcome, and `/status` displayed the version, data paths, key status, and model status.
- **VERIFIED — Gemini error response:** one live request returned HTTP 400 `INVALID_ARGUMENT` with “unexpected model name format”. The app log did not contain API-key text. Check the configured model name before another connection test.
- **VERIFIED — Scope:** the source and test directories contain no speech/audio implementation. Phase 2 has not started.
- **VERIFIED — Git history:** implementation commit `f318bae` and documentation commit `d1ce6f6` exist locally. The provider fix, regression test, and documentation updates listed below are currently uncommitted working-tree changes.

## Verification update — 2026-11-03

- **VERIFIED — Provider fix:** `src/spark/providers/gemini.py` now maps the common Gemini HTTP 400 message `API key not valid` to the distinct invalid-key response. `tests/test_provider.py` covers this case.
- **VERIFIED — Automated tests after the fix:** final command used an external temporary base and cache directory: `$env:QT_QPA_PLATFORM='offscreen'; .\.venv\Scripts\python.exe -m pytest -q --basetemp $env:TEMP\spark-checks-final\basetemp -o "cache_dir=$env:TEMP\spark-checks-final\cache"`; output: `32 passed in 2.48s`.
- **VERIFIED — Lint after the fix:** command `.\.venv\Scripts\ruff.exe check .`; output: `All checks passed!`
- **VERIFIED — Runtime process check:** starting `python -m spark` in an isolated `%LOCALAPPDATA%` folder and starting it a second time resulted in the second process exiting with code `0` while the first remained alive. The first window being visibly raised was not observable in this non-interactive session.
- **VERIFIED — Qt shell inspection:** offscreen inspection found the `Show`, `Settings`, and `Quit` tray actions and non-null generated window/tray icons. This does not replace a visible tray test.
- **VERIFIED — Settings recovery in app startup:** an actual offline `spark.app.run()` lifecycle against an isolated invalid `settings.json` returned exit code `0`, emitted the recovery warning, created `settings.json.bad`, and persisted default settings. The warning was captured rather than visibly displayed, so the visible dialog remains unverified.
- **VERIFIED — Installed runtime/backend:** the available interpreter is Python `3.13.4`, and the installed keyring backend is `WinVaultKeyring`. No real credential was read or modified during this update.

## Not yet verified manually

1. Python 3.12 runtime. Only Python 3.13.4 was available in the implementation environment.
2. Real Windows Credential Manager create, replace, retrieve, and delete operations. Automated keyring tests use a mock backend.
3. Gemini success with a currently supported configured model. The observed live request failed on model-name format.
4. Live invalid-key and offline outcomes. Automated provider tests simulate SDK and transport errors.
5. Visible tray icon and actual Show, Settings, and Quit menu behavior; window-close-to-tray behavior and clean shutdown.
6. A second real process visibly activating/raising the first window. The second process exit and first-process survival were verified; visual activation was not observable in this session.
7. Visible corrupt-settings recovery notice in the running app. The startup path, warning emission, backup, and default persistence were verified offline; the visible dialog remains unverified.
8. Search the actual app settings and log files after the manual credential and connection checks to confirm the key is absent.

## Manual checklist to finish Phase 1 verification

1. Install/use Python 3.12 (64-bit), create the virtual environment using the README setup commands, and run the full test suite.
2. Start SPARK, inspect its tray menu, close the window with a key configured, show it again from the tray, and quit from the tray. Confirm it exits cleanly.
3. Start SPARK a second time while the first is open; confirm the first window is raised and no second window remains.
4. In Settings, save, replace, and delete a Gemini key. Do not paste or print the key in a terminal. Check the settings and log files for key leakage without echoing the key itself.
5. Configure a model name currently supported for the account and run Test connection once. Separately check invalid-key and offline messages only when safe to do so. The prior observed request returned a model-format error.
6. Back up any existing local settings file before testing corruption recovery. With SPARK closed, make a disposable invalid JSON settings file, launch SPARK, confirm the recovery notice and `settings.json.bad` backup, then restore or remove only the test data.

## Run the interface

From PowerShell in `C:\Programs\spark`:

```powershell
.\.venv\Scripts\Activate.ps1
python -m spark
```

The direct equivalent is `.\.venv\Scripts\python.exe -m spark`. Do not set `QT_QPA_PLATFORM=offscreen` for the visible interface; that setting is for automated tests. Quit from the SPARK tray menu.

Keep all follow-up work within Phase 1. Do not start Phase 2 without explicit written approval.
