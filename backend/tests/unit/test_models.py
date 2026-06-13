import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Bean, Shot
from app.models.shot import Taste


def test_bean_unique_constraint(db, create_bean):
    create_bean(brand="Onyx", product="Monarch")
    with pytest.raises(IntegrityError):
        bean2 = Bean(brand="Onyx", product="Monarch")
        db.add(bean2)
        db.commit()


def test_shot_fk_constraint(db):
    shot = Shot(
        bean_id=9999,
        grinder_id=9999,
        machine_id=9999,
        grind_setting_native="5.0",
        dose_g=18.0,
        yield_g=36.0,
        time_s=28.0,
        taste=Taste.BALANCED,
        reason_code="dialing_in",
    )
    db.add(shot)
    with pytest.raises(IntegrityError):
        db.commit()
