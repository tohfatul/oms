from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    aws_region: str = "us-east-1"
    bedrock_model_id: str = "us.amazon.nova-2-lite-v1:0"

    llm_provider: str = "mock"

    openai_api_key: str = ""
    openai_model: str = "gpt-5.6"

    oms_api_base_url: str = "https://api.digizerones.com"

    entra_api_client_id: str = ""
    entra_required_scope: str = "access_as_user"

    database_host: str = ""
    database_port: int = 5432
    database_name: str = "orderdb"
    database_username: str = ""
    database_password: str = ""

    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()