from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, validator


# request body

class Record(BaseModel):
    uuid: str


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

    @validator("startT", pre=True)
    def dt_validate(cls, startT):
        return datetime.fromtimestamp(startT / 1000)


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

    @validator("page2T", pre=True)
    def dt_validate(cls, page2T):
        return datetime.fromtimestamp(page2T / 1000)


class Page3(Record):
    page3T: datetime
    accuracy1: int
    accuracy2: int
    accuracy3: int
    control1: int
    control2: int
    control3: int
    cui_adapt1: int
    cui_adapt2: int
    cui_attentive1: int
    cui_attentive2: int
    cui_attentive3: int
    cui_attentive4: int
    cui_attentive5: int
    cui_coord1: int
    cui_coord2: int
    cui_coord3: int
    cui_coord4: int
    cui_engage1: int
    cui_engage2: int
    cui_human1: int
    cui_human2: int
    cui_human3: int
    cui_ia_exp: int
    cui_ia_expertise: int
    cui_ia_unders: int
    cui_interPace: int
    cui_positive1: int
    cui_positive2: int
    cui_positive3: int
    cui_positive4: int
    cui_rapport1: int
    cui_rapport2: int
    cui_rapport3: int
    cui_response: int
    cui_resQuali1: int
    cui_resQuali2: int
    cui_resQuali3: int
    cui_unders: int

    @validator("page3T", pre=True)
    def dt_validate(cls, page3T):
        return datetime.fromtimestamp(page3T / 1000)


class Page4(Record):
    ease1: int
    ease2: int
    ease3: int
    explain1: int
    explain2: int
    explain3: int
    ia1: int
    ia2: int
    ia3: int
    intent1: int
    intent2: int
    intent3: int
    intent4: int
    intent2purchase1: int
    intent2purchase2: int
    intent2purchase3: int
    novel1: int
    novel2: int
    satis1: int
    satis2: int
    satis3: int
    satis4: int
    seren1: int
    seren2: int
    seren3: int
    trans1: int
    trans2: int
    trans3: int
    trust1: int
    trust3: int
    trust4: int
    trust5: int
    useful1: int
    useful2: int
    useful3: int
    page4T: datetime

    @validator("page4T", pre=True)
    def dt_validate(cls, page4T):
        return datetime.fromtimestamp(page4T / 1000)
