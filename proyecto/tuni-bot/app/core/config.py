from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""

    # LLM — Gemini for dev/test, Ollama for production VM
    llm_provider: str = "gemini"  # "gemini" or "ollama"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"

    # Telegram
    telegram_bot_token: str = ""

    # Professor
    professor_password: str = ""

    # Bot behavior
    bot_session_timeout_minutes: int = 30
    bot_max_history_messages: int = 40
    bot_edit_interval_seconds: float = 1.5

    # App
    app_env: str = "development"
    data_dir: str = "data/students"

    class Config:
        env_file = ".env"


settings = Settings()
