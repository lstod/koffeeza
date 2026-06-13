from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Preference(Base):
    __tablename__ = "preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    grinder_id: Mapped[int | None] = mapped_column(ForeignKey("grinders.id"), default=None)
    machine_id: Mapped[int | None] = mapped_column(ForeignKey("machines.id"), default=None)
