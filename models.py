from sqlalchemy.schema import Column
from sqlalchemy.types import String, Integer, Enum
from database import Base


class CarInfo(Base):
    __tablename__ = "fc_records"
    id = Column(Integer, primary_key=True, index=True)
    manufacturer = Column(String)
    modelName = Column(String)
    cc = Column(Integer)
    onRoadPrice = Column(Integer)
    seatingCapacity = Column(Integer)
    gearBox = Column(Integer)

