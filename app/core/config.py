from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")
    
    APP_NAME: str = "SeuServiço"
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/seuservico"
    REDIS_URL: str = "redis://localhost:6379/0"

    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB

    ALLOWED_ORIGINS: str = "http://localhost:3000"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    @property
    def origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()


# ─── Fixed categories & services ────────────────────────────────────────────
CATEGORIES: dict[str, list[str]] = {
    "Manutenção & Reparos": [
        "Eletricista", "Encanador", "Pedreiro", "Pintor", "Marceneiro",
        "Serralheiro", "Técnico de ar-condicionado", "Técnico de geladeira",
        "Técnico de máquina de lavar", "Chaveiro",
    ],
    "Tecnologia": [
        "Técnico de celular", "Técnico de computador", "Montador de PC",
        "Instalador de internet", "Designer gráfico", "Desenvolvedor web",
    ],
    "Casa & Limpeza": [
        "Diarista", "Passadeira", "Faxineiro pós-obra", "Jardineiro", "Dedetização",
    ],
    "Educação & Aulas": [
        "Professor de inglês", "Professor de matemática", "Reforço escolar",
        "Aulas de violão", "Aulas de informática",
    ],
    "Beleza & Estética": [
        "Barbeiro", "Cabeleireiro", "Manicure", "Maquiador", "Designer de sobrancelha",
    ],
    "Automotivo": [
        "Mecânico", "Lava jato", "Martelinho de ouro", "Auto elétrica", "Guincho",
    ],
    "Eventos & Criativos": [
        "Fotógrafo", "Videomaker", "DJ", "Decorador", "Cerimonialista",
    ],
    "Saúde & Bem-Estar": [
        "Personal trainer", "Massagista", "Nutricionista",
    ],
}
