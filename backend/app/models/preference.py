from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Preference(Base):
    __tablename__ = "preferences"
    __table_args__ = (UniqueConstraint("user_id", name="uq_preference_user"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    grinder_id: Mapped[int | None] = mapped_column(ForeignKey("grinders.id"), default=None)
    machine_id: Mapped[int | None] = mapped_column(ForeignKey("machines.id"), default=None)
