# How Much Is Done: Project SPARK Phase 1

## Current assessment

**Phase 1 is fully verified and complete.** All implementation, provider, runtime, and visible-desktop acceptance checks have been completed within Phase 1.

All Phase 1 acceptance checks are recorded individually below rather than summarized as a percentage.

## Verified

- **VERIFIED — Project and implementation:** the Phase 1 source tree, pinned package configuration, settings, logging, keyring wrapper, channel interfaces, local commands, Qt window, tray code, Gemini connection test, and Phase 1 docs exist in the repository.
- **VERIFIED — Automated tests:** the latest full result is recorded below with an external pytest base and cache directory.
- **VERIFIED — Lint:** Ruff reported `All checks passed!`.
- **VERIFIED — GUI observation:** the app window opened on Windows, showed the first-run welcome, and `/status` displayed the version, data paths, key status, and model status.
- **VERIFIED — Gemini connection behavior:** the prior model-format failure was resolved by configuring a currently supported model; the live success and categorized failure outcomes are recorded in the 2026-11-04 update.
- **VERIFIED — Scope:** the source and test directories contain no speech/audio implementation. Phase 2 has not started.
- **VERIFIED — Git history:** Phase 1 implementation and follow-up hardening are committed and pushed to `origin/master`.

## Verification update — 2026-11-03

- **VERIFIED — Provider fix:** `src/spark/providers/gemini.py` now maps the common Gemini HTTP 400 message `API key not valid` to the distinct invalid-key response. `tests/test_provider.py` covers this case.
- **VERIFIED — Automated tests after the fix:** the earlier post-fix command used an external temporary base and cache directory and reported `32 passed in 2.48s`.
- **VERIFIED — Lint after the fix:** command `.\.venv\Scripts\ruff.exe check .`; output: `All checks passed!`
- **VERIFIED — Runtime process check:** starting `python -m spark` in an isolated `%LOCALAPPDATA%` folder and starting it a second time resulted in the second process exiting with code `0` while the first remained alive. The first window being visibly raised was not observable in this non-interactive session.
- **VERIFIED — Qt shell inspection:** offscreen inspection found the `Show`, `Settings`, and `Quit` tray actions and non-null generated window/tray icons. This does not replace a visible tray test.
- **VERIFIED — Settings recovery in app startup:** an actual offline `spark.app.run()` lifecycle against an isolated invalid `settings.json` returned exit code `0`, emitted the recovery warning, created `settings.json.bad`, and persisted default settings. The warning was captured rather than visibly displayed, so the visible dialog remains unverified.
- **VERIFIED — Installed runtime/backend:** Python `3.12.10` passed the full suite in `.venv312`; the installed keyring backend is `WinVaultKeyring`.

## Verification update — 2026-11-04

- **VERIFIED — Real Credential Manager CRUD:** the existing SPARK credential was held only in memory, temporarily replaced with two non-secret sentinels, read back after set and replace, deleted, and restored in a `finally` block. Set, replace, delete, restore, and final configured-state checks all passed. The original key was not printed.
- **VERIFIED — Secret absence after real credential exercise:** the restored key text was absent from the actual SPARK settings and log files. No key value was written to the repository or progress notes.
- **VERIFIED — Live Gemini success:** the authenticated SDK model list was queried without printing credentials; `gemini-3.5-flash-lite` was tested through `GeminiProvider.test_connection` and returned `Gemini connection succeeded.` The model was saved to the user's SPARK settings.
- **VERIFIED — Invalid-key outcome:** `GeminiProvider.test_connection` with a non-secret dummy key returned `Google rejected the API key. Check it in Settings.`
- **VERIFIED — Offline outcome:** routing the provider through an unreachable local proxy returned `Network unavailable. Check your connection and try again.` A separate forced-proxy run returned the timeout message.
- **VERIFIED — Transient service classification:** HTTP 503 high-demand responses now return `Gemini is temporarily unavailable. Try again later.`
- **VERIFIED — Tray action behavior:** Qt regression coverage now triggers Show, Settings, and Quit actions and verifies their callbacks; tray activation now raises and activates the window for both single-click and double-click activation reasons.
- **VERIFIED — Clean shutdown path:** an actual offline `spark.app.run()` lifecycle exited with code `0` after invoking the application quit callback and wrote `SPARK shutting down` to the log.
- **VERIFIED — Final automated checks:** targeted provider/UI command reported `14 passed in 2.30s`; the latest full command with external temporary directories reported `33 passed in 2.89s`; Ruff reported `All checks passed!`.
- **VERIFIED — Python 3.12 checks:** `.venv312\Scripts\python.exe -m pytest -q` reported `33 passed in 6.87s`; `.venv312\Scripts\ruff.exe check .` reported `All checks passed!`.

## Verification update — 2026-11-04 desktop acceptance

- **VERIFIED — Visible tray interaction:** user-confirmed tray icon visibility, Show, Settings, Quit, close-to-tray behavior, restore behavior, and clean exit.
- **VERIFIED — Visible second-instance activation:** user-confirmed that starting a second SPARK process opens no second window, exits the second process, and raises/activates the existing window.
- **VERIFIED — Visible settings recovery:** user-confirmed the corrupt-settings recovery dialog appeared, identified `settings.json.bad`, and restored defaults; the original settings file was restored afterward.

## Acceptance status

1. **VERIFIED — Python 3.12 runtime:** Python `3.12.10` passed all 33 tests and Ruff checks in `.venv312`.
2. **VERIFIED — Real Windows Credential Manager create, replace, retrieve, and delete operations:** completed with temporary values and restoration of the existing credential without printing it.
3. **VERIFIED — Gemini success with a currently supported configured model:** `gemini-3.5-flash-lite` succeeded and is saved in settings.
4. **VERIFIED — Live invalid-key and offline outcomes:** dummy invalid key and unreachable local proxy checks returned distinct messages.
5. **VERIFIED — Visible tray icon and actual Show/Settings/Quit interaction:** user-confirmed on the Windows desktop.
6. **VERIFIED — A second real process visibly activating/raising the first window:** user-confirmed on the Windows desktop.
7. **VERIFIED — Visible corrupt-settings recovery notice:** user-confirmed on the Windows desktop, including backup and restoration.
8. **VERIFIED — Secret absence after real credential checks:** the restored key was absent from actual settings and log files.

## Completed desktop verification steps

1. Open PowerShell on the visible desktop and run:

   ```powershell
   Set-Location C:\Programs\spark
   Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
   .\.venv312\Scripts\python.exe -m spark
   ```

   Confirm the SPARK window and tray icon are visible. Open the tray menu and activate **Show** and **Settings**. Close the window; with the configured key present it should hide to the tray. Activate **Show** again, then use **Quit** and confirm the process exits.
2. Start SPARK again with the command above. Minimize the first window, then run the same command from a second PowerShell window. Confirm the second process exits without opening a second window and the first SPARK window is visibly raised/activated.
3. Close SPARK through the tray. Back up the settings file and create a disposable invalid file:

   ```powershell
   $sp = Join-Path $env:LOCALAPPDATA 'SPARK'
   $settings = Join-Path $sp 'settings.json'
   $backup = Join-Path $sp 'settings.json.phase1-backup'
   Copy-Item $settings $backup -Force
   [System.IO.File]::WriteAllText($settings, '{', [System.Text.UTF8Encoding]::new($false))
   .\.venv312\Scripts\python.exe -m spark
   ```

   Confirm the visible recovery dialog says the file was backed up as `settings.json.bad` and defaults were restored. Quit SPARK, then restore the original file:

   ```powershell
   Remove-Item $settings -Force
   Move-Item $backup $settings -Force
   Remove-Item (Join-Path $sp 'settings.json.bad') -Force -ErrorAction SilentlyContinue
   ```

## Run the interface

From PowerShell in `C:\Programs\spark`:

```powershell
.\.venv\Scripts\Activate.ps1
python -m spark
```

The direct equivalent is `.\.venv\Scripts\python.exe -m spark`. Do not set `QT_QPA_PLATFORM=offscreen` for the visible interface; that setting is for automated tests. Quit from the SPARK tray menu.

Keep all follow-up work within Phase 1. Do not start Phase 2 without explicit written approval.
