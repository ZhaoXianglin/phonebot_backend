import uuid
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://admin:FCbot&2022@sh-cynosdbmysql-grp-2nhnn1ea.sql.tencentcdb.com:29348/phonebot"
Base = automap_base()
engine = create_engine(DATABASE_URL)
# reflect the tables
Base.prepare(engine, reflect=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# mapped classes are now created with names by default
# matching that of the table name.
ph_records = Base.classes.ph_records


# 这个返回UUID字符函数，用来给模型默认UUID字段的
def generate_uuid():
    return uuid.uuid4().hex


# 创建数据库连接池，注意python3.7以上支持异步，如果是3.6还要安装async-exit-stack和async-generator库
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
