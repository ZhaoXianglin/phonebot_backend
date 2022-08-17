from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, validator


# request body

class Record(BaseModel):
    uuid: str


class IdRecord(Record):
    id: int
    identity_cue: int
    explanation_style: int


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
    explanation_style: int
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


class Scenario(Record):
    ScenarioT: datetime

    @validator("ScenarioT", pre=True)
    def dt_validate(cls, ScenarioT):
        return datetime.fromtimestamp(ScenarioT / 1000)


class userMsg(Record):
    message: str
    logger: list
    explanation_style: int
    msgT: datetime


class Preference(Record):
    brand: Optional[str] = None
    budget: Optional[int] = None
    display_size: Optional[str] = None,
    battery: Optional[str] = None,
    weight: Optional[str] = None
    explanation_style: int
    preferT: datetime

    @validator("preferT", pre=True)
    def dt_validate(cls, preferT):
        return datetime.fromtimestamp(preferT / 1000)

    # @validator("brands", pre=True)
    # def brands_validate(cls, brands):
    #     return ",".join(brands)


class Page2(Record):
    page2T: datetime
    phonelist: list

    @validator("page2T", pre=True)
    def dt_validate(cls, page2T):
        return datetime.fromtimestamp(page2T / 1000)


class Que1(Record):
    que1T: datetime
    cui_human1: int
    cui_human2: int
    cui_human3: int

    trust_propensity1: int
    trust_propensity2: int
    trust_propensity3: int

    accuracy1: int
    accuracy2: int
    accuracy3: int

    explain1: int
    explain3: int
    explain4: int

    social_presence1: int
    social_presence2: int
    social_presence4: int

    ease4: int
    ease5: int
    ease6: int

    useful2: int
    useful3: int
    useful4: int

    check1: int
    check2: int

    @validator("que1T", pre=True)
    def dt_validate(cls, que1T):
        return datetime.fromtimestamp(que1T / 1000)


class Que2(Record):
    cui_attentive2: int
    cui_attentive5: int
    cui_attentive6: int
    cui_attentive7: int

    trust_compe1: int
    trust_compe3: int
    trust_compe4: int

    trust_integity1: int
    trust_integity2: int
    trust_integity3: int

    intent2depend1: int
    intent2depend2: int
    intent2depend3: int

    intent2follow1: int
    intent2follow2: int
    intent2follow3: int

    intent2purchase1: int
    intent2purchase2: int
    intent2purchase3: int

    que2T: datetime

    @validator("que2T", pre=True)
    def dt_validate(cls, que2T):
        return datetime.fromtimestamp(que2T / 1000)


class Que3(Record):
    accuracy4: int
    explain2: int
    social_presence3: int
    ease1: int
    useful1: int

    cui_resQuali1: int
    cui_resQuali3: int
    cui_interPace: int
    cui_response: int

    cui_unders1: int
    cui_unders2: int
    cui_unders3: int

    trans1: int
    trans2: int
    trans3: int
    trans4: int

    control1: int
    control4: int
    control5: int
    control6: int

    confidence1: int
    confidence2: int
    confidence4: int
    confidence5: int

    satis1: int
    satis2: int
    satis3: int

    cui_positive1: int
    cui_positive2: int
    cui_positive3: int
    cui_rapport2: int

    que3T: datetime

    @validator("que3T", pre=True)
    def dt_validate(cls, que3T):
        return datetime.fromtimestamp(que3T / 1000)


class Que4(Record):
    openended1: str
    openended2: str

    que4T: datetime

    @validator("que4T", pre=True)
    def dt_validate(cls, que4T):
        return datetime.fromtimestamp(que4T / 1000)
