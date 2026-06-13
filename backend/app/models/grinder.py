from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums import ScaleType


class Grinder(Base):
    __tablename__ = "grinders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    brand: Mapped[str] = mapped_column(String(120))
    model: Mapped[str] = mapped_column(String(120))
    label: Mapped[str | None] = mapped_column(String(120), default=None)
    scale_type: Mapped[ScaleType] = mapped_column(String(20))
    step_native: Mapped[float] = mapped_column(Float)
    finer_is_lower: Mapped[bool] = mapped_column(Boolean)
    snap: Mapped[float] = mapped_column(Float)
    min_native: Mapped[float | None] = mapped_column(Float, default=None)
    max_native: Mapped[float | None] = mapped_column(Float, default=None)
    unit_label: Mapped[str] = mapped_column(String(30))
