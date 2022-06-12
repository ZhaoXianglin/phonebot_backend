from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, validator


# request body

class Record(BaseModel):
    uuid: str


class IdRecord(Record):
    condition: int
    id: int


# class PhoneBase(BaseModel):
#     id: int
#     battery: int
#     brand: str
#     id: str
#     cam1: int
#     cam2: 8
#     cpu: str
#     d1: float
#     d2: float
#     d3: float
#     displayratio: str
#     displaysize: float
#     gps: str
#     img: str
#     modelname: str
#     nettech: str
#     nfc: str
#     os1: str
#     popularity: int
#     price: float
#     ram: str
#     resolution1: int
#     resolution2: int
#     storage: str
#     url: str
#     weight: int
#     year: str

class BaseLogMogel(BaseModel):
    agent: str
    action: str
    timestamp: datetime

    @validator("timestamp", pre=True)
    def dt_validate(cls, timestamp):
        return datetime.fromtimestamp(timestamp / 1000)


class LoggerModel(Record):
    logger: list
    lTime: datetime

    @validator("lTime", pre=True)
    def dt_validate(cls, lTime):
        return datetime.fromtimestamp(lTime / 1000)


class UserModel(BaseModel):
    preferenceData: dict
    _id: str
    user_preference_model: dict
    user_critique_preference: list
    user_constraints: list


class UserProfile(BaseModel):
    user: UserModel
    topRecommendedItem: int
    logger: dict
    pool: list
    new_pool: list


class Accept(BaseModel):
    device: str
    accT: datetime

    @validator("accT", pre=True)
    def dt_validate(cls, accT):
        return datetime.fromtimestamp(accT / 1000)


class CommonRes(BaseModel):
    status: int
    msg: str


class PhoneRes(CommonRes):
    phone: str


class startPage(Record):
    startT: datetime
    condition: int

    @validator("startT", pre=True)
    def dt_validate(cls, startT):
        return datetime.fromtimestamp(startT / 1000)


class tutorPage(Record):
    tutorT: datetime

    @validator("tutorT", pre=True)
    def dt_validate(cls, tutorT):
        return datetime.fromtimestamp(tutorT / 1000)


class Page1(Record):
    gender: str
    age: str
    nationality: str
    page1T: datetime

    @validator("page1T", pre=True)
    def dt_validate(cls, page1T):
        return datetime.fromtimestamp(page1T / 1000)


class userMsg(Record):
    message: str
    logger: list
    msgT: datetime


class Preference(Record):
    brands: str
    budget: int
    cameras: str
    preferT: datetime

    @validator("preferT", pre=True)
    def dt_validate(cls, preferT):
        return datetime.fromtimestamp(preferT / 1000)

    @validator("brands", pre=True)
    def brands_validate(cls, brands):
        return ",".join(brands)


class Page2(Record):
    page2T: datetime
    phonelist: list

    @validator("page2T", pre=True)
    def dt_validate(cls, page2T):
        return datetime.fromtimestamp(page2T / 1000)


class Page3(Record):
    page3T: datetime
    accuracy1: int
    accuracy2: int
    accuracy3: int

    explain1: int
    explain2: int
    explain3: int

    cui_attentive2: int
    cui_attentive5: int
    cui_attentive6: int

    cui_unders1: int
    cui_unders2: int
    cui_unders3: int

    cui_response: int
    cui_resQuali1: int
    cui_resQuali3: int
    cui_interPace: int

    social_presence1: int
    social_presence2: int
    social_presence3: int
    social_presence4: int

    trans1: int
    trans2: int
    trans3: int

    control1: int
    control4: int
    control5: int

    cui_positive1: int
    cui_positive2: int
    cui_positive3: int
    cui_rapport1: int
    cui_rapport2: int

    cui_human1: int
    cui_human2: int
    cui_human3: int

    chk1: int

    @validator("page3T", pre=True)
    def dt_validate(cls, page3T):
        return datetime.fromtimestamp(page3T / 1000)


class Page4(Record):
    useful1: int
    useful2: int
    useful3: int

    ease1: int
    ease4: int
    ease5: int

    trust1: int
    trust2: int
    trust3: int
    trust4: int

    confidence1: int
    confidence2: int
    confidence4: int

    satis1: int
    satis2: int
    satis3: int

    intent1: int
    intent2: int
    intent3: int

    intent2purchase1: int
    intent2purchase2: int
    intent2purchase3: int

    chk2: int
    page4T: datetime

    @validator("page4T", pre=True)
    def dt_validate(cls, page4T):
        return datetime.fromtimestamp(page4T / 1000)
