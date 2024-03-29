from datetime import datetime
from typing import Optional

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
    try_another_count: int
    explanation_style: int
    phone: dict
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


class FirstChoice(Record):
    first_select: int


class FinalChoice(Record):
    recommended_phone: str
    reason: str
    tableT: datetime
    final_select: int


@validator("tableT", pre=True)
def dt_validate(cls, tableT):
    return datetime.fromtimestamp(tableT / 1000)


class Page1(Record):
    prolific_id: str
    gender: str
    age: str
    nationality: str
    decision1: int
    decision2: int
    decision3: int
    decision4: int
    decision5: int
    decision6: int
    decision7: int
    decision8: int
    decision9: int
    domain1: int
    domain2: int
    domain3: int
    maximizer1: int
    maximizer2: int
    maximizer3: int

    # trust_propensity1: int
    # trust_propensity2: int
    # trust_propensity3: int

    # ce1: int
    # ce2: int
    # ce3: int

    page1T: datetime

    @validator("page1T", pre=True)
    def dt_validate(cls, page1T):
        return datetime.fromtimestamp(page1T / 1000)


class Game(Record):
    highest_span_score: int
    consec_error_score: int
    gameT: datetime

    @validator("gameT", pre=True)
    def dt_validate(cls, gameT):
        return datetime.fromtimestamp(gameT / 1000)


class Scenario(Record):
    ScenarioT: datetime

    @validator("ScenarioT", pre=True)
    def dt_validate(cls, ScenarioT):
        return datetime.fromtimestamp(ScenarioT / 1000)


class userMsg(Record):
    message: str
    logger: list
    explanation_style: int
    phone: dict
    msgT: datetime


class Preference(Record):
    explanation_style: int
    battery: Optional[str] = None,
    brand: Optional[str] = None
    budget: Optional[int] = None
    displaysize: Optional[str] = None,
    preferT: datetime
    username: Optional[str] = None
    weight: Optional[str] = None

    @validator("preferT", pre=True)
    def dt_validate(cls, preferT):
        return datetime.fromtimestamp(preferT / 1000)

    # @validator("brands", pre=True)
    # def brands_validate(cls, brands):
    #     return ",".join(brands)


class Page2(Record):
    page2T: datetime
    cart: str
    log: str

    @validator("page2T", pre=True)
    def dt_validate(cls, page2T):
        return datetime.fromtimestamp(page2T / 1000)


class Que1(Record):
    que1T: datetime
    check1: int
    check2: int

    interlligence1: int
    interlligence2: int
    interlligence3: int

    design1: int
    design2: int
    design3: int

    choice1: int
    choice2: int
    choice3: int

    control1: int
    control4: int
    control5: int
    control6: int

    cui_unders1: int
    cui_unders2: int
    cui_unders3: int

    atten_chk1: int

    eva_exp1: Optional[int]
    eva_exp2: Optional[int]
    eva_exp3: Optional[int]

    # check2: int

    @validator("que1T", pre=True)
    def dt_validate(cls, que1T):
        return datetime.fromtimestamp(que1T / 1000)


class Que2(Record):
    accuracy1: int
    accuracy2: int
    accuracy3: int
    accuracy4: int
    explain1: int
    explain2: int
    explain3: int
    explain4: int
    social_presence1: int
    social_presence2: int
    social_presence3: int
    social_presence4: int
    cui_attentive2: int
    cui_attentive5: int
    cui_attentive6: int
    cui_attentive7: int
    intent2purchase1: int
    intent2purchase2: int
    intent2purchase3: int
    atten_chk2: int
    que2T: datetime

    @validator("que2T", pre=True)
    def dt_validate(cls, que2T):
        return datetime.fromtimestamp(que2T / 1000)


class Que3(Record):
    trans1: int
    trans2: int
    trans3: int
    trans4: int

    cui_human1: int
    cui_human2: int
    cui_human3: int

    ease1: int
    ease4: int
    ease5: int
    ease6: int

    confidence1: int
    confidence2: int
    confidence4: int

    satis1: int
    satis2: int
    satis3: int

    trust1: int
    trust2: int
    trust3: int
    trust4: int
    atten_chk3: int

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


class PostTable(Record):
    cognitive1: int
    cognitive2: int
    cognitive3: int
    cognitive4: int
    cognitive5: int
    cognitive6: int
    confidence1: int
    confidence2: int
    confidence3: int
    postT: datetime

    @validator("postT", pre=True)
    def dt_validate(cls, postT):
        return datetime.fromtimestamp(postT / 1000)


class RandomID(BaseModel):
    randomID: str
