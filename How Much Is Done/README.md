# How Much Is Done: Project SPARK Phase 1

## Current assessment

**Phase 1 implementation is complete and local/provider behavior is verified.** A small set of environment-dependent checks still require a visible interactive desktop or Python 3.12, so the phase remains explicitly not fully verified under the strict acceptance wording.

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
- **VERIFIED — Installed runtime/backend:** the available interpreter is Python `3.13.4`, and the installed keyring backend is `WinVaultKeyring`.

## Verification update — 2026-11-04

- **VERIFIED — Real Credential Manager CRUD:** the existing SPARK credential was held only in memory, temporarily replaced with two non-secret sentinels, read back after set and replace, deleted, and restored in a `finally` block. Set, replace, delete, restore, and final configured-state checks all passed. The original key was not printed.
- **VERIFIED — Secret absence after real credential exercise:** the restored key text was absent from the actual SPARK settings and log files. No key value was written to the repository or progress notes.
- **VERIFIED — Live Gemini success:** the authenticated SDK model list was queried without printing credentials; `gemini-3.5-flash-lite` was tested through `GeminiProvider.test_connection` and returned `Gemini connection succeeded.` The model was saved to the user's SPARK settings.
- **VERIFIED — Invalid-key outcome:** `GeminiProvider.test_connection` with a non-secret dummy key returned `Google rejected the API key. Check it in Settings.`
- **VERIFIED — Offline outcome:** routing the provider through an unreachable local proxy returned `Network unavailable. Check your connection and try again.` A separate forced-proxy run returned the timeout message.
- **VERIFIED — Transient service classification:** HTTP 503 high-demand responses now return `Gemini is temporarily unavailable. Try again later.`
- **VERIFIED — Tray action behavior:** Qt regression coverage now triggers Show, Settings, and Quit actions and verifies their callbacks; tray activation now raises and activates the window for both single-click and double-click activation reasons.
- **VERIFIED — Clean shutdown path:** an actual offline `spark.app.run()` lifecycle exited with code `0` after invoking the application quit callback and wrote `SPARK shutting down` to the log.
- **VERIFIED — Final automated checks:** targeted provider/UI command reported `14 passed in 2.30s`; the full command with external temporary directories reported `33 passed in 1.74s`; Ruff reported `All checks passed!`.

## Not yet verified manually

1. **UNVERIFIED — Python 3.12 runtime:** Python 3.12 is not installed; Python 3.13.4 is available and satisfies the package's `>=3.12` runtime constraint.
2. **VERIFIED — Real Windows Credential Manager create, replace, retrieve, and delete operations:** completed with temporary values and restoration of the existing credential without printing it.
3. **VERIFIED — Gemini success with a currently supported configured model:** `gemini-3.5-flash-lite` succeeded and is saved in settings.
4. **VERIFIED — Live invalid-key and offline outcomes:** dummy invalid key and unreachable local proxy checks returned distinct messages.
5. **PARTIALLY VERIFIED — Visible tray icon and actual Show/Settings/Quit interaction:** callbacks, generated icons, close-to-tray logic, and clean shutdown are verified; rendered interaction needs a visible desktop.
6. **PARTIALLY VERIFIED — A second real process visibly activating/raising the first window:** the second process exited `0` and the first survived; visual activation needs a visible desktop.
7. **PARTIALLY VERIFIED — Visible corrupt-settings recovery notice:** startup warning emission, backup, and default persistence are verified offline; the rendered dialog needs a visible desktop.
8. **VERIFIED — Secret absence after real credential checks:** the restored key was absent from actual settings and log files.

## Manual checklist to finish Phase 1 verification

1. Install/use Python 3.12 (64-bit), create the virtual environment using the README setup commands, and run the full test suite. This remains unavailable in the current environment.
2. On a visible desktop, start SPARK, inspect its tray menu, close the window with a key configured, show it again from the tray, and quit from the tray.
3. On a visible desktop, start SPARK a second time while the first is open; confirm the first window is visibly raised and no second window remains.
4. On a visible desktop, launch against a disposable corrupt settings file and confirm the recovery dialog is visibly rendered. The file backup/default behavior is already verified.

## Run the interface

From PowerShell in `C:\Programs\spark`:

```powershell
.\.venv\Scripts\Activate.ps1
python -m spark
```

The direct equivalent is `.\.venv\Scripts\python.exe -m spark`. Do not set `QT_QPA_PLATFORM=offscreen` for the visible interface; that setting is for automated tests. Quit from the SPARK tray menu.

Keep all follow-up work within Phase 1. Do not start Phase 2 without explicit written approval.
