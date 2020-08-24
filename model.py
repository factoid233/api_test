import datetime
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Integer, Column, String, Text, Float, DateTime, SmallInteger, DECIMAL)

from config import db_url

engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class api_test_result(Base):
    __tablename__ = 'api_test_result'
    id = Column(Integer, primary_key=True, comment='记录id')
    desc = Column(String(200), comment='用例描述')
    api = Column(String(200), comment='接口地址')
    old_res = Column(Text, comment='测试结果 旧数据json')
    new_res = Column(Text, comment='测试结果 改过的json')
    created_time = Column(DateTime, default=datetime.datetime.today().isoformat(), comment='创建时间')

    def __repr__(self):
        return "<Record (id='%r')>" % self.id


Base.metadata.create_all(engine)


@contextmanager
def session_maker():
    """
    :param engine: 可选cdas数据库,默认118公网测试库
    :return:
    """
    s = Session()
    try:
        yield s
        s.commit()
    except Exception as e:
        s.rollback()
        raise e
    finally:
        s.close()


def add_all(data: list):
    with session_maker() as s:
        data1 = [api_test_result(**i) for i in data]
        s.add_all(data1)

