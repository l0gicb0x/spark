# PROJECT SPARK: PHASE 1 IMPLEMENTATION PROMPT

You are a senior software engineer building Project SPARK with me. This prompt is self-contained: the architecture, roadmap and Phase 1 specification are all below. There is no pre-existing `docs/` folder. This prompt is the source of truth.

---

## 1. Project context

SPARK is a reliable, text-first AI desktop agent for Windows 10/11. The user types a request; SPARK answers it or performs a task on their PC through a small set of bounded, permission-gated tools. It uses the user's OWN Google Gemini API key.

**Version 1 is TEXT ONLY.** Voice (speech-to-text and text-to-speech) is planned for a later version. Do NOT implement, import, install or stub any audio or speech functionality now. Keep the design voice-ready: user input and agent output go through small interfaces (`InputChannel`, `OutputChannel`) so a voice channel can be added later without rewriting the core.

**Long-term target (north star, NOT the scope of Phase 1).** SPARK should eventually offer the practical capabilities of existing voice-first Windows AI companions, through text first: open and switch apps, navigate the desktop via Windows UI Automation, read what is on screen, research the web with sources, remember user facts across sessions, run saved routines, provide an app launcher and clipboard history, and control browsers through Windows accessibility. Every risky capability is disabled or approval-gated by default.

**Originality rule.** Implement everything independently. Do not copy code, assets, names, hotkeys or branding from any existing product or repository. If you consult an open-source project, check and respect its license and tell me which one.

**Design principles**
- Reliability over spectacle: a few tools that always work beat many that sometimes fail.
- Safe by default: anything that can change the system is disabled or approval-gated.
- Local and transparent: settings, logs and data live in user-owned locations; secrets are never stored in plain text.
- Honest limits: Windows blocks synthetic input on UAC prompts, the lock screen and some protected apps. Handle this gracefully; never claim success that was not achieved.
- Swappable AI provider behind an interface; the first implementation targets Gemini.

---

## 2. Technology (fixed unless I approve a change)

- Python 3.12 (64-bit), `src/` layout, packaged with `pyproject.toml`
- UI: PySide6 (Qt)
- Tests: pytest, pytest-qt
- Secrets: `keyring` (Windows Credential Manager)
- AI: Google Gemini via the current official Google SDK for the Gemini API
- Lint/format: ruff (optional but preferred)

**Do not rely on memory for any of the following. Verify first** (see section 4): the official Gemini SDK package name and version, its call signatures, valid model names, and any PySide6/keyring/pytest-qt API you are not certain about.

---

## 3. Architecture (approved)

Layered, with dependencies pointing inward. The core never imports UI or provider code.

```
src/spark/
  __main__.py            # entry: python -m spark
  app.py                 # QApplication setup, single instance, tray, lifecycle
  core/
    channels.py          # InputChannel / OutputChannel interfaces + TextChannel
    commands.py          # local slash-command handler (no AI)
    errors.py            # typed exceptions (ConfigError, SecretError, ProviderError...)
    logging_setup.py     # rotating file logging + secret-redaction filter
    paths.py             # %LOCALAPPDATA%\SPARK locations (pathlib)
    settings.py          # load/validate/save settings (atomic write, corruption recovery)
    secrets.py           # keyring wrapper (get/set/delete Gemini key)
  providers/
    base.py              # LLMProvider interface (connection test only in Phase 1)
    gemini.py            # Gemini implementation of connection test
  ui/
    main_window.py       # chat transcript + input box
    settings_dialog.py   # key management, model name, log level, test connection
    tray.py              # system tray icon + menu
    workers.py           # background threads/tasks so the UI never blocks
tests/
docs/
  ARCHITECTURE.md  ROADMAP.md  PHASE_1_SPEC.md   (you create these in Step A)
README.md  CHANGELOG.md  pyproject.toml
```

You may adjust file names slightly if you find a real technical reason, but tell me what you changed and why.

---

## 4. Roadmap (approved)

| Phase | Name | Summary |
|---|---|---|
| 1 | Desktop Application Foundation | **(current)** App shell, tray, settings, secure key storage, logging, Gemini connection test, local commands, tests, docs |
| 2 | Gemini Chat | Real conversation with Gemini: history, streaming, model setting, error and quota handling |
| 3 | Tool Framework and Safety | Tool registry, JSON schemas, approval prompts, audit log, risk levels |
| 4 | System Tools | Open/switch apps, system info, app launcher, clipboard history |
| 5 | Desktop Automation | Windows UI Automation navigation and control |
| 6 | Screen Understanding | Screenshot and UI-tree reading, vision with Gemini |
| 7 | Memory and Routines | Local user-controllable memory, saved multi-step routines |
| 8 | Web Research and Browser | Search with cited sources, browser control via accessibility |
| 9 | Packaging and Hardening | `.exe` build, installer, crash reporting, security review |
| 10 | Voice (later version) | Speech-to-text and text-to-speech through the existing channel interfaces |

Do NOT work on any phase except Phase 1.

---

## 5. PHASE 1 SPECIFICATION: Desktop Application Foundation

### 5.1 Deliverables

1. **Project skeleton**: `pyproject.toml` (pinned dependencies, dev extras, entry point), `src/` layout, `.gitignore`, ruff and pytest config, `git init` if no repo exists. Create a virtual environment and install via `pip install -e ".[dev]"`.
2. **Paths and storage**: all user data under `%LOCALAPPDATA%\SPARK\` (`logs\`, `settings.json`). Use `pathlib`. Create folders on demand. Fail with a clear message if the location is not writable.
3. **Logging**: rotating file log at `%LOCALAPPDATA%\SPARK\logs\spark.log` (size-capped, a few backups), configurable level, plus a redaction filter that strips anything that looks like an API key or the stored key itself. Never log secrets or full prompts.
4. **Settings**: JSON file with validated schema and defaults. Fields: `gemini_model` (string, user-editable, no hard-coded assumption it stays valid), `log_level`, `start_minimized` (bool). Atomic writes (temp file then replace). If the file is corrupt, back it up as `settings.json.bad`, reset to defaults and tell the user.
5. **Secure key storage**: Gemini API key stored ONLY in Windows Credential Manager via `keyring` (service `SPARK`, username `gemini_api_key`). Provide set, get, delete, and "is configured" helpers. The key never appears in files, logs, tracebacks or UI text after entry (show masked, e.g. last 4 characters at most).
6. **Single instance**: a second launch must not start a second app; it signals the first to show its window, then exits. Use a Qt-native mechanism (for example `QLocalServer`/`QLocalSocket` or `QLockFile`; verify the API).
7. **System tray**: icon with menu (Show, Settings, Quit). Closing the window hides to tray (unless it is the first run with no key; then tell the user). Quit exits cleanly with no orphan threads or processes. Generate a simple tray/window icon in code or include an original asset; do not use third-party branding.
8. **Main window (text chat shell)**: scrolling transcript, multi-line input (Enter sends, Shift+Enter newline), Send button. Messages go through `InputChannel`/`OutputChannel` to a command handler. In Phase 1 there is NO AI chat. Plain (non-slash) messages get a clear, honest reply such as "AI chat arrives in Phase 2. Type /help for available commands."
9. **Local slash commands** (real, working, no AI): `/help`, `/status` (version, log path, settings path, whether a key is configured, configured model), `/settings` (opens settings dialog), `/clear` (clears transcript), `/version`, `/quit`. Unknown commands give a helpful error.
10. **Settings dialog**: enter or replace the Gemini API key (masked input), delete the key (with confirmation), edit model name, choose log level, toggle start-minimized, and a **Test connection** button.
11. **Test connection**: makes ONE minimal request to Gemini using the stored key and configured model, runs in a background worker with a timeout, and never blocks the UI. It reports distinct, human-readable outcomes: success, no key set, invalid key, network unavailable, timeout, quota/rate limit, region/unsupported, unknown model, unexpected error (logged, with a short message to the user). Map real SDK exceptions to these, and verify the exception types in the installed SDK; do not guess them.
12. **Global error handling**: install an exception hook that logs the traceback and shows a friendly dialog. Worker exceptions are caught and surfaced, never silently lost.
13. **First-run experience**: if no key is configured, show a short welcome message in the transcript explaining how to create a Gemini API key in Google AI Studio and where to paste it (Settings). Do not hard-code claims about free-tier limits or regional availability; tell the user to check Google's current policy.
14. **Tests** (written alongside each feature):
    - settings: defaults, validation, atomic write, corrupt-file recovery
    - paths: correct locations, creation, not-writable handling
    - logging: rotation config, redaction filter hides keys
    - secrets: set/get/delete using a mocked keyring backend (never touch the real credential store in tests)
    - commands: every slash command and unknown-command behavior
    - single instance: second instance detection (as far as testable)
    - Gemini connection test: each outcome mapped from simulated SDK exceptions and success (mock the network; no real API calls in automated tests)
    - UI: with pytest-qt and `QT_QPA_PLATFORM=offscreen`, window creation, send message, `/help`, settings dialog opens, key field is masked
15. **Documentation**: create `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/PHASE_1_SPEC.md` from sections 1 to 5 of this prompt (keep them accurate, don't embellish), plus `README.md` (what SPARK is, requirements, setup, run, test, where data lives, how to create a Gemini key, security notes, current limitations) and `CHANGELOG.md` (Phase 1 entry).

### 5.2 Explicit non-goals for Phase 1 (do NOT build)

- Any real AI conversation, streaming or chat history (Phase 2)
- Any tool execution, UI Automation, screen capture, clipboard history, app launching (Phases 3 to 6)
- Memory, routines, web search or browser control (Phases 7 and 8)
- Any speech, audio, microphone or global hotkey code (Phase 10 / later)
- Installers or `.exe` packaging (Phase 9)

### 5.3 Acceptance criteria

- `python -m spark` starts the app; window and tray icon appear
- A second `python -m spark` does not open a second instance and brings up the first
- Closing the window hides it to tray; Quit exits cleanly
- Settings persist across restarts; a corrupted settings file is recovered with a notice
- The API key can be saved, replaced and deleted; it is visible only in Windows Credential Manager, never in any file or log (check by searching the log and settings files after use)
- Test connection reports the correct, distinct message for at least: no key, invalid key, offline, and success (use a real key for the manual run, mocks for automated tests)
- All slash commands work
- Full test suite passes; no test was weakened to get there
- No audio or speech code, and no code from later phases

---

## 6. Truthfulness and verification rules (critical)

These rules exist to prevent fabricated information. They override any urge to appear complete or confident.

1. **Ground everything.** Base decisions on this prompt, the actual repository files, real command output and official documentation. Anything else is an assumption and must be labeled.
2. **Never invent.** No made-up function names, class names, library APIs, CLI flags, config keys, package names, version numbers, model names, file paths or Windows behaviors.
3. **Verify before using.**
   - Before calling a third-party API, confirm it exists in the installed version (`pip show`, `help()`, `inspect`, package source, official docs).
   - Before adding a dependency, confirm the exact package name and version exist (`pip index versions <pkg>` or a successful install).
   - Before editing a file, read it. Before referencing a file, confirm it exists.
   - Before using a Gemini model name as a default, confirm it from official Google documentation or a live model-list call; if you cannot confirm, say so and let the user set it.
4. **No fabricated results.** Never say tests passed, the app launched or a feature works unless you ran it and saw the output. Paste the real command and real output. If something fails, show the failure.
5. **Label certainty.** In your plan and report, mark claims as **VERIFIED** (observed directly), **ASSUMED** (reasonable but unconfirmed; say what would confirm it) or **UNKNOWN** (could not determine; say what you need from me).
6. **Say "I don't know" when true.** Asking me or flagging a gap is always better than guessing.
7. **Environment honesty.** If you cannot run a GUI, a Windows-only API, the Credential Manager or a live Gemini call in your environment, say so plainly. Do not claim those parts were verified. Provide exact manual steps instead.
8. **No silent test weakening.** Do not delete, skip or loosen tests to make them pass. If a test is wrong, explain why and get my approval.
9. **Complete change reporting.** List every file you changed, including incidental ones.
10. **Self-check before the final report.** Re-read your report and confirm every factual claim against actual output or files. Remove or relabel anything you cannot back up.

---

## 7. Rules of engagement

1. **Follow this architecture.** Any deviation (different library, structure or pattern) needs my approval first, with a short reason.
2. **Preserve existing code.** First check what already exists in the repository. If it has working code, keep it, and make no unrelated refactors, renames or reformatting.
3. **Real code only.** No placeholders, `TODO` stubs or fake data standing in for working functionality. If something cannot be built in this phase, say so.
4. **Error handling and logging** everywhere an operation can fail (files, OS, keyring, network, SDK). Never swallow exceptions silently.
5. **Windows-first.** Use `pathlib`, no hard-coded separators, no POSIX-only assumptions.
6. **Dependencies.** Only what Phase 1 needs, pinned, each justified in one line.
7. **Security.** No secrets in code, logs, the repo or tests. No `shell=True` with user input. No unsafe execution of anything.
8. **UI never blocks.** Network and slow work run off the UI thread.
9. **Ask when blocked.** If something in this prompt is ambiguous or contradicts reality, STOP and ask instead of inventing a requirement.

---

## 8. Workflow (follow in this order)

**Step A: Inspect and plan.**
Inspect the repository (it may be empty). Then present a short plan: what you will build, files to create or modify with a one-line reason each, new dependencies (already verified to exist), assumptions and open questions (labeled VERIFIED/ASSUMED/UNKNOWN), and any risk. Explain intended changes BEFORE modifying files. Continue without waiting unless there is a risk, an ambiguity or a deviation. Then create the three `docs/` files from sections 1 to 5.

**Step B: Implement.**
Build incrementally, one feature at a time, writing its tests alongside it. Create a task list and keep it updated.

**Step C: Test.**
Run the full test suite, show the real command and output, and fix every failure properly. Report anything you could not test automatically and why.

**Step D: Verify actual behavior.**
Passing tests are not enough. Run the app and check each acceptance criterion in 5.3. Describe exactly what you observed. For anything you cannot run in your environment (GUI, Credential Manager, live Gemini), give me numbered manual verification steps and mark them UNVERIFIED rather than claiming success.

**Step E: Documentation.**
Finalize `README.md`, `CHANGELOG.md` and `docs/`, so they describe what was actually built (including any approved deviations).

**Step F: Commit.**
Make a clean local git commit for Phase 1. Do not push anywhere.

---

## 9. Definition of done

Phase 1 is complete only when ALL are true:
- Every deliverable in 5.1 is implemented
- Every acceptance criterion in 5.3 is met, or explicitly marked UNVERIFIED with manual steps
- No speech, audio or later-phase code exists
- Tests pass and real output is shown
- Documentation is updated and accurate
- The report contains no unverified claim presented as fact

If any item is unmet, say the phase is NOT complete and state exactly what is missing.

---

## 10. Final report format

1. **Summary**: what was built, 3 to 5 sentences
2. **Files**: created and modified, one-line purpose each
3. **Dependencies**: added, with versions
4. **Tests**: command, real output, behaviors covered
5. **Verified behavior**: what you observed running the app, and what you could not verify
6. **Manual verification steps** for anything unverified
7. **Docs updated**: which files
8. **Deviations from this prompt**: none, or each with reason
9. **Assumptions and unknowns** still open
10. **Remaining limitations and known issues**
11. **Proposed scope for Phase 2**: for information only, not started

---

## 11. Stop condition

After the report, STOP. Do not begin Phase 2 or any other phase. Wait for my explicit written approval, such as "Phase 1 approved, proceed to Phase 2".