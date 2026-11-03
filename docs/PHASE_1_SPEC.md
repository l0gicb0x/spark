# Phase 1 Specification: Desktop Application Foundation

## Deliverables

1. Project skeleton: pinned dependencies, dev extras, entry point, `src/` layout, `.gitignore`, Ruff/pytest configuration, virtual environment, editable install.
2. `%LOCALAPPDATA%\SPARK\` storage with `logs\` and `settings.json`; create on demand and report unwritable paths.
3. Size-capped rotating log with backups, configurable level, and API-key redaction. Do not log secrets or full prompts.
4. Validated JSON settings (`gemini_model`, `log_level`, `start_minimized`), atomic writes, corrupt-file backup to `settings.json.bad`, defaults, and notice.
5. Gemini key set/get/delete/configured helpers through Credential Manager only; masked display.
6. Qt-native single-instance behavior that activates the first window.
7. Runtime-generated original tray/window icon and Show, Settings, Quit actions; clean shutdown.
8. Text transcript and multiline input (Enter sends, Shift+Enter newline), with messages routed through channel interfaces. Ordinary messages explain AI chat is Phase 2.
9. Local commands: `/help`, `/status`, `/settings`, `/clear`, `/version`, `/quit`.
10. Settings dialog for key, model, log level, start minimized, and test connection.
11. One minimal Gemini request on a worker thread with a timeout and distinct user-facing outcomes.
12. Global exception handling; worker errors are surfaced.
13. First-run welcome directs users to Google AI Studio and current Google policy.
14. Tests for settings, paths, logging, secrets, commands, single instance, provider outcomes, and UI.
15. README, changelog, architecture, roadmap, and this specification.

## Non-goals

No AI conversation/history/streaming, tool execution, UI automation, screen capture, clipboard, app launching, memory, routines, web search/browser control, speech/audio/microphone/global hotkeys, or installer/exe packaging.

## Acceptance criteria

`python -m spark` opens a window and tray icon; a second launch activates the first. Closing hides to tray when configured, and Quit exits cleanly. Settings persist and corrupt settings recover with notice. Keys remain only in Credential Manager. Connection outcomes distinguish missing key, invalid key, offline, and success. Commands work, tests pass, and no later-phase or audio code is present.
