"""Схемы для генерации и валидации данных."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ExifData(BaseModel):
    """Модель данных EXIF."""

    model_config = ConfigDict(populate_by_name=True)

    make: Optional[str] = Field(default=None, alias="Make", description="Производитель камеры")
    model: Optional[str] = Field(default=None, alias="Model", description="Модель камеры")
    lens_model: Optional[str] = Field(default=None, alias="LensModel", description="Модель объектива")
    f_number: Optional[float] = Field(default=None, alias="FNumber", description="Диафрагменное число")
    exposure_time: Optional[float] = Field(default=None, alias="ExposureTime", description="Время выдержки")
    iso_speed: Optional[int] = Field(default=None, alias="ISOSpeedRatings", description="Светочувствительность")
    focal_length: Optional[int] = Field(default=None, alias="FocalLength", description="Фокусное расстояние")
    datetime_original: Optional[datetime] = Field(
        default=None,
        alias="DateTimeOriginal",
        description="Дата и время съемки",
    )
