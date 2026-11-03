# Project SPARK

SPARK is a text-first Windows desktop assistant foundation. Phase 1 provides a Qt desktop shell, local slash commands, settings, secure Gemini key storage, rotating logs, and a Gemini connection test. AI chat and desktop actions are not implemented yet.

## Phase 1 status

The Phase 1 implementation and follow-up hardening are committed and pushed to GitHub. **VERIFIED:** the latest full test run reported `33 passed in 2.89s`; Ruff reported `All checks passed!`. The available interpreter is Python 3.13.4, so exact Python 3.12 runtime verification remains outstanding.

**VERIFIED:** the app window started on Windows and displayed the first-run welcome. The `/status` command displayed the version, local data paths, key status and model status. A current supported model returned a successful Gemini connection test, and the request log contained no API-key text.

**Still to verify on a visible desktop:** rendered tray/menu interaction, visible second-process window activation, and the rendered corrupt-settings recovery dialog. Credential Manager CRUD, secret-file absence, live Gemini success, invalid-key/offline provider outcomes, settings recovery behavior, and clean shutdown have been exercised and recorded in [How Much Is Done/README.md](How%20Much%20Is%20Done/README.md).

The latest progress evidence, including the provider fix and exact verification state, is maintained in [How Much Is Done/README.md](How%20Much%20Is%20Done/README.md).

See the [How Much Is Done folder](How%20Much%20Is%20Done/README.md) for the detailed completion state and manual checklist. The full approved prompt is in the [Project Prompt folder](Project%20Prompt/PROJECT_SPARK_PHASE_1_PROMPT.md).

## Requirements

- Windows 10 or 11
- Python 3.12 (64-bit)

## Dependencies

- `PySide6==6.12.0` — Qt windows, tray, local socket, and worker threads.
- `google-genai==2.34.0` — official Gemini SDK for the connection test only.
- `keyring==25.7.0` — Windows Credential Manager integration.
- `setuptools==80.9.0` — pinned editable build backend.
- `pytest==9.2.0` and `pytest-qt==4.5.0` — core and Qt tests (development extra).
- `ruff==0.17.3` — linting and formatting (development extra).

## Setup and run

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m spark
```

To run the test suite: `python -m pytest`. Ruff is available as `ruff check .`.

## First run

Open Settings, enter a Gemini API key obtained from Google AI Studio, choose a model name supported by your Google account, and select Save. SPARK does not assume a model remains available; use Google's current documentation to check supported models and policy. Test connection sends one minimal request.

## Local data and security

Settings and logs are stored in `%LOCALAPPDATA%\SPARK\` (`settings.json` and `logs\spark.log`). The API key is stored through keyring in Windows Credential Manager and is not written into settings or logs. Log messages redact a stored key and common API-key patterns. Do not paste secrets into ordinary chat messages.

## Current limitations

Phase 1 does not answer ordinary messages with AI. It does not execute tools, control apps, inspect the screen, browse the web, retain chat history, or support voice/audio. Gemini access depends on the user's key, model availability, account, region and network. Check Google's current policy.

See [Architecture](docs/ARCHITECTURE.md), [Roadmap](docs/ROADMAP.md), and [Phase 1 specification](docs/PHASE_1_SPEC.md).

## Saved prompts

- [Full Phase 1 implementation prompt](Project%20Prompt/PROJECT_SPARK_PHASE_1_PROMPT.md)
- [Progress review prompt](How%20Much%20Is%20Done/PROGRESS_REVIEW_PROMPT.md)
