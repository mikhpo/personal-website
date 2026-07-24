"""Схемы для генерации и валидации данных."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ExifData(BaseModel):
    """Модель данных EXIF."""

    model_config = ConfigDict(populate_by_name=True)

    make: str | None = Field(default=None, alias="Make", description="Производитель камеры")
    model: str | None = Field(default=None, alias="Model", description="Модель камеры")
    lens_model: str | None = Field(default=None, alias="LensModel", description="Модель объектива")
    f_number: float | None = Field(default=None, alias="FNumber", description="Диафрагменное число")
    exposure_time: float | None = Field(default=None, alias="ExposureTime", description="Время выдержки")
    iso_speed: int | None = Field(default=None, alias="ISOSpeedRatings", description="Светочувствительность")
    focal_length: int | None = Field(default=None, alias="FocalLength", description="Фокусное расстояние")
    datetime_original: datetime | None = Field(
        default=None,
        alias="DateTimeOriginal",
        description="Дата и время съемки",
    )
