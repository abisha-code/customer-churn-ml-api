from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    MODEL_PATH: str = "ml/saved_model/model.joblib"
    LOG_LEVEL: str = "INFO"
    MAX_BATCH_SIZE: int = 100
    API_TITLE: str = "Customer Churn Prediction API"


settings = Settings()
