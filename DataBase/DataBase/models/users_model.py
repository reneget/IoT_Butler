from sqlalchemy import Column, Integer, String, Boolean, DateTime, ARRAY
import logging
from DataBase.core.db_connection import Base

user_model_logger = logging.getLogger(__name__)


class Users(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, unique=True, nullable=False)
    tag = Column(String, unique=False, nullable=True)
    devices = Column(ARRAY(Integer), unique=False, nullable=True, default=list())
    device_counter = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    create_time = Column(DateTime, unique=False, nullable=False)

    def __repr__(self):
        try:
            return f'Users(id={self.id}, user_id={self.user_id}, tag={self.tag}, devices={self.devices}, device_counter={self.device_counter}, create_time={self.create_time}, active={self.active})'
        except Exception as e:
            user_model_logger.error(f'Error from returning of string format User model', exc_info=True)
