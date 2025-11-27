from typing import Optional, Type
import datetime

from sqlalchemy.orm import Session
from loguru import logger as devices_logger

from DataBase.models import Devices


class DevicesRepo:
    def __init__(self, db: Session):
        self.db = db

    def create_device(self, title: str, description: str, address: str, create_time: datetime.datetime) -> Devices:
        try:
            device = Devices(title=title, description=description, address=address, create_time=create_time)
            self.db.add(device)
            self.db.commit()
            self.db.refresh(device)
            devices_logger.info(f'Successful creation of a device [{repr(device)}] in the database')
            return device
        except Exception:
            self.db.rollback()
            devices_logger.error('Error when creating a new device in the database', exc_info=True)
            raise

    def get_device_by_id(self, device_id: int) -> Optional[Devices] | None:
        try:
            device = self.db.query(Devices).filter(Devices.device_id == device_id).first()
            devices_logger.info(f'Successfully retrieving the device [{repr(device)}] from the database')
            return device
        except Exception:
            devices_logger.error(f'Error when getting device [{device_id}] from DataBase', exc_info=True)
            raise

    def get_all_devices(self) -> list[Type[Devices]] | None:
        try:
            device = self.db.query(Devices).all()
            devices_logger.info('Successfully retrieving list of all devices from the database')
            return device
        except Exception:
            devices_logger.error('Error when getting all devices from DataBase', exc_info=True)
            raise

    def update_device(self, device_id: int, **new_values) -> Optional[Devices]:
        device = self.get_device_by_id(device_id)
        try:
            if device:
                for key, value in new_values.items():
                    if hasattr(device, key) and value is not None:
                        setattr(device, key, value)
                self.db.commit()
                self.db.refresh(device)
                devices_logger.info(f'Successfully updated device [{repr(device)}] in DataBase')
            return device
        except Exception:
            self.db.rollback()
            devices_logger.error(f'Error when updating device [{device_id}] in DataBase', exc_info=True)
            raise

    def delete_device(self, device_id: int) -> Optional[Devices]:
        device = self.get_device_by_id(device_id)
        try:
            if device:
                self.db.delete(device)
                self.db.commit()
                devices_logger.info(f'Successfully deleted device [{repr(device)}] from DataBase')
            return device
        except Exception:
            self.db.rollback()
            devices_logger.error(f'Error when deleting device [{device_id}] from Database', exc_info=True)
            raise
