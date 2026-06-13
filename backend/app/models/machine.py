from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    brand: Mapped[str] = mapped_column(String(120))
    model: Mapped[str] = mapped_column(String(120))
    label: Mapped[str | None] = mapped_column(String(120), default=None)
    notes: Mapped[str | None] = mapped_column(String(500), default=None)
