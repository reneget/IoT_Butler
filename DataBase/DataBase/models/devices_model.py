from sqlalchemy import Column, String, Boolean, Integer, DateTime
from loguru import logger as devices_logger
from DataBase.core.db_connection import Base


class Devices(Base):
    __tablename__ = 'Devices'

    device_id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String)
    description = Column(String)
    address = Column(String, unique=False, nullable=False)
    active = Column(Boolean, default=False)
    create_time = Column(DateTime, unique=False, nullable=False)

    def __repr__(self):
        try:
            return f'Devices(device_id={self.device_id}, title={self.title}, description={self.description}, address={self.address}, active={self.active}, create_time={self.create_time})'
        except Exception as e:
            devices_logger.error(f'Error from returning of string format Devices model', exc_info=True)
