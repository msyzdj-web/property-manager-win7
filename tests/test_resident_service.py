
import pytest
from datetime import date
from services.resident_service import ResidentService
from models.resident import Resident

def test_create_resident(db_session):
    resident = ResidentService.create_resident(
        room_no="101",
        name="张三",
        phone="12345678901",
        area=100.0,
        move_in_date=date(2023, 1, 1),
        db=db_session
    )
    assert resident.id is not None
    assert resident.name == "张三"
    assert resident.room_no == "101"

def test_get_resident(db_session):
    ResidentService.create_resident(room_no="102", name="李四", db=db_session)
    resident = ResidentService.get_resident_by_room_no("102", db=db_session)
    assert resident is not None
    assert resident.name == "李四"

def test_duplicate_room_no(db_session):
    ResidentService.create_resident(room_no="103", name="王五", db=db_session)
    with pytest.raises(ValueError):
        ResidentService.create_resident(room_no="103", name="赵六", db=db_session)
