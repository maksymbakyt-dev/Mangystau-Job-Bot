from sqlalchemy import BigInteger, ForeignKey, String, Text, Integer, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    role: Mapped[str] = mapped_column(String(20), nullable=True) # 'employer' or 'seeker'
    name: Mapped[str] = mapped_column(String(100))
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="ru")

class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    age: Mapped[int] = mapped_column(Integer)
    skills: Mapped[str] = mapped_column(Text)
    experience: Mapped[str] = mapped_column(Text)
    microdistrict: Mapped[str] = mapped_column(String(100))
    expected_salary: Mapped[str] = mapped_column(String(50))
    schedule: Mapped[str] = mapped_column(String(50))
    time_available: Mapped[str] = mapped_column(String(100))
    languages: Mapped[str] = mapped_column(String(200))
    
    user = relationship("User", backref="resumes")

class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True)
    employer_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    skills_required: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(50)) # Полная/частичная
    microdistrict: Mapped[str] = mapped_column(String(100))
    schedule: Mapped[str] = mapped_column(String(50))
    salary: Mapped[str] = mapped_column(String(50))
    languages_required: Mapped[str] = mapped_column(String(200))
    
    employer = relationship("User", backref="vacancies")

class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancies.id"))
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, accepted, rejected
