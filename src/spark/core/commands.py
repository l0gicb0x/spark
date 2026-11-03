"""Local slash command handling; no provider calls occur here."""

from collections.abc import Callable


class CommandHandler:
    def __init__(
        self,
        *,
        version: str,
        log_path: str,
        settings_path: str,
        key_configured: Callable[[], bool],
        model: Callable[[], str],
        open_settings: Callable[[], None],
        clear: Callable[[], None],
        quit_app: Callable[[], None],
    ):
        self.version = version
        self.log_path = log_path
        self.settings_path = settings_path
        self.key_configured = key_configured
        self.model = model
        self.open_settings = open_settings
        self.clear = clear
        self.quit_app = quit_app

    def handle(self, text: str) -> str | None:
        command, _, argument = text.strip().partition(" ")
        command = command.lower()
        if command == "/help":
            return "Commands: /help, /status, /settings, /clear, /version, /quit"
        if command == "/version":
            return f"SPARK {self.version}"
        if command == "/status":
            return (
                f"SPARK {self.version}\nLog: {self.log_path}\nSettings: {self.settings_path}\n"
                f"Gemini key: {'configured' if self.key_configured() else 'not configured'}\n"
                f"Model: {self.model() or '(not configured)'}"
            )
        if command == "/settings":
            self.open_settings()
            return "Settings opened."
        if command == "/clear":
            self.clear()
            return "Transcript cleared."
        if command == "/quit":
            self.quit_app()
            return "Quitting SPARK."
        return f"Unknown command: {command}. Type /help for available commands."
