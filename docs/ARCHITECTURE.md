# SPARK Architecture

## Context and principles

SPARK is a reliable, text-first Windows 10/11 desktop agent. It uses the user's Google Gemini API key. Version 1 is text only; future channels will use the same small input/output interfaces. Long-term capabilities are outside Phase 1. The project prioritizes reliability, safe defaults, local transparent data, honest reporting of Windows limitations, and a swappable provider boundary.

## Technology

- Python 3.12 (64-bit), `src/` layout, packaged with `pyproject.toml`
- PySide6 (Qt)
- pytest and pytest-qt
- `keyring` for Windows Credential Manager
- Official Google Gemini SDK
- Ruff for linting/formatting

## Approved layers

Dependencies point inward. The core does not import UI or provider code.

```text
src/spark/
  __main__.py
  app.py
  core/ (channels, commands, errors, logging_setup, paths, settings, secrets)
  providers/ (base, gemini)
  ui/ (main_window, settings_dialog, tray, workers)
tests/
docs/
```

The provider interface is limited to a connection test in Phase 1. No real AI conversation is included until Phase 2. `InputChannel`, `OutputChannel`, and the minimal `TextChannel` keep channel handling replaceable.

## Data and security

Settings and rotating logs are stored under `%LOCALAPPDATA%\SPARK\`. The Gemini key is stored only through keyring in Windows Credential Manager under service `SPARK` and username `gemini_api_key`. Log filtering redacts known key text and common API-key patterns. System-changing tools are not part of Phase 1.

## Desktop lifecycle

Qt provides the application, window, system tray, and local socket used for single-instance activation. A second launch signals the first instance to show its window. Closing the window hides it while a key is configured; without a key it exits so the first-run welcome remains accessible. Tray actions are Show, Settings, and Quit.
