from datetime import datetime
from decimal import Decimal
from sqlalchemy import Boolean, DateTime, func, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from bases.base_alchemy_model import Base


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="jobs")

    title: Mapped[str]

    description: Mapped[str]

    salary_from: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=True)

    salary_to: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    responses: Mapped["Response"] = relationship(back_populates="job")


