import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Bean, Grinder, Machine
from app.models.grinder import ScaleType

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def _enable_fk(dbapi_conn, _connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def create_bean(db):
    def _create(brand: str = "Onyx", product: str = "Monarch", **kwargs) -> Bean:
        bean = Bean(brand=brand, product=product, **kwargs)
        db.add(bean)
        db.commit()
        db.refresh(bean)
        return bean

    return _create


@pytest.fixture
def create_grinder(db):
    def _create(
        brand: str = "Eureka",
        model: str = "Mignon Specialita",
        scale_type: ScaleType = ScaleType.STEPLESS,
        step_native: float = 0.1,
        finer_is_lower: bool = True,
        snap: float = 0.1,
        unit_label: str = "numbers",
        **kwargs,
    ) -> Grinder:
        grinder = Grinder(
            brand=brand,
            model=model,
            scale_type=scale_type,
            step_native=step_native,
            finer_is_lower=finer_is_lower,
            snap=snap,
            unit_label=unit_label,
            **kwargs,
        )
        db.add(grinder)
        db.commit()
        db.refresh(grinder)
        return grinder

    return _create


@pytest.fixture
def create_machine(db):
    def _create(brand: str = "Breville", model: str = "Bambino Plus", **kwargs) -> Machine:
        machine = Machine(brand=brand, model=model, **kwargs)
        db.add(machine)
        db.commit()
        db.refresh(machine)
        return machine

    return _create
