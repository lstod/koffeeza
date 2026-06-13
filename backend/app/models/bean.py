from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Bean(Base):
    __tablename__ = "beans"
    __table_args__ = (UniqueConstraint("brand", "product", name="uq_bean_identity"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(120))
    product: Mapped[str] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(String(500), default=None)
