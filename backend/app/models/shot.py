from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums import Intensity, Taste


class Shot(Base):
    __tablename__ = "shots"

    id: Mapped[int] = mapped_column(primary_key=True)
    bean_id: Mapped[int] = mapped_column(ForeignKey("beans.id"))
    grinder_id: Mapped[int] = mapped_column(ForeignKey("grinders.id"))
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id"))
    grind_setting_native: Mapped[str] = mapped_column(String(30))
    dose_g: Mapped[float] = mapped_column(Float)
    yield_g: Mapped[float] = mapped_column(Float)
    time_s: Mapped[float] = mapped_column(Float)
    taste: Mapped[Taste] = mapped_column(String(20))
    intensity: Mapped[Intensity | None] = mapped_column(String(10), default=None)
    reason_code: Mapped[str] = mapped_column(String(50))
    roast_date: Mapped[date | None] = mapped_column(Date, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
