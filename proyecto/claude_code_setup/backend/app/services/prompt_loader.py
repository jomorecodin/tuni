from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts"


def load_template(mode: str) -> str:
    path = PROMPTS_DIR / f"modo_{mode}.md"
    return path.read_text(encoding="utf-8")


def build_system_prompt(mode: str, materia_nombre: str = "General") -> str:
    template = load_template(mode)
    return template.replace("{materia_nombre}", materia_nombre)
