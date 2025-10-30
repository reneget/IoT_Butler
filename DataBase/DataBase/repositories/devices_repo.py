from typing import Optional, Type
import datetime

from sqlalchemy.orm import Session
import logging

from DataBase.models import Devices

devices_logger = logging.getLogger(__name__)


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
            devices_logger.error(f'Error when creating a new device in the database', exc_info=True)

    def get_device_by_id(self, device_id: int) -> Optional[Devices] | None:
        try:
            device = self.db.query(Devices).filter(Devices.device_id == device_id).first()
            devices_logger.info(f'Successfully retrieving the device [{repr(device)}] from the database')
            return device
        except Exception:
            devices_logger.error(f'Error when getting device [{device}] from DataBase', exc_info=True)

    def get_all_devices(self) -> list[Type[Devices]] | None:
        try:
            device = self.db.query(Devices).all()
            devices_logger.info('Successfully retrieving list of all devices from the database')
            return device
        except Exception:
            devices_logger.error(f'Error when getting all devices from DataBase', exc_info=True)

    def update_device(self, position_id: int, **new_values) -> Type[Devices] | None:
        position = self.get_position_by_id(position_id)
        try:
            if position:
                for key, value in new_values.items():
                    if hasattr(position, key) and value is not None:
                        setattr(position, key, value)
                self.db.commit()
                self.db.refresh(position)
            devices_logger.info(f'Successfully update position [{repr(position)}] in DataBase')
            return position
        except Exception:
            devices_logger.error(f'Error when updating position [{repr(position)}] in DataBase')

    def delete_device(self, position_id: int) -> Type[Devices] | None:
        position = self.get_position_by_id(position_id)
        try:
            if position:
                self.db.delete(position)
                self.db.commit()
                devices_logger.info(f'Successfully delete position [{repr(position)}] from DataBase')
            return position
        except Exception:
            devices_logger.error(f'Error when deleting position [{repr(position)}] from Database')
