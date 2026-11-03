# Project SPARK: Phase 1 Progress Review Prompt

Copy and use this prompt when you want a fresh, evidence-based progress report. It asks for a review only; it does not authorize Phase 2 or further code changes.

---

Review the current Project SPARK repository against `docs/PROJECT_SPARK_PHASE_1_PROMPT.md`, especially its Phase 1 deliverables and acceptance criteria.

Do not modify files, run a live Gemini request, read or print any API key, write to Windows Credential Manager, start Phase 2, or create another commit. Inspect the repository, its tests, Git status/history, and available command output. If you need to verify behavior, use only offline tests and non-secret checks.

Report each claim as **VERIFIED**, **ASSUMED**, or **UNKNOWN**, and include the file, test, command, or observed output that supports it. Do not claim success for behavior you did not observe.

Organize the report as follows:

1. **How much is complete:** summarize the Phase 1 deliverables that are implemented and give a completion estimate only if you can explain its basis.
2. **Verified checks:** list exact commands and outputs, plus observed app behavior.
3. **Unverified acceptance criteria:** name each item and state exactly what evidence or manual action is still needed.
4. **Known issues:** include any current failures or limitations, including the observed Gemini `400 INVALID_ARGUMENT` about an unexpected model name format, if it is still relevant.
5. **Files and commit state:** report changed files, uncommitted changes, and the latest local commit.
6. **What remains to finish Phase 1:** give a numbered, ordered checklist that stays within Phase 1.
7. **Phase 2:** state that it has not been started and wait for explicit written approval before beginning it.

Do not repeat secrets or sensitive values in the report. End by stating whether Phase 1 is complete or not complete, based only on evidence.
