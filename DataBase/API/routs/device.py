from fastapi import APIRouter, status, HTTPException, Depends
from sqlalchemy.orm import Session

from . import pydantic_models as pd_md
from DataBase.core.db_connection import get_db
from DataBase.repositories import DevicesRepo
from ..utils import FunctionsAPI as Func_API

import logging

device_logger = logging.getLogger(__name__)

device_router = APIRouter(
    prefix='/device',
    tags=['device']
)


@device_router.post('/create/device')
async def create_device_api(device: pd_md.DeviceCreate, db: Session = Depends(get_db)):
    """
    Api router what creating new device
    """
    try:
        device_logger.info('Request to create a new device')
        created_device = DevicesRepo(db).create_device(**device.__dict__)

        if created_device is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Not unique'
            )
        device_logger.debug(f'{repr(created_device)}')
        device_logger.info('New device created')

        return pd_md.Device(**created_device.__dict__)
    except HTTPException:
        device_logger.error('An error occurred while creating the device', exc_info=True)
        raise
    except:
        device_logger.error('An error occurred while creating the device', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@device_router.get('/get/device/{device_id}')
async def get_device_by_id_api(device_id: int, db: Session = Depends(get_db)):
    try:
        device_logger.info(f'Request to get device: device_id={device_id}')
        device = DevicesRepo(db).get_device_by_id(device_id)
        device_logger.info('Device received')
        device_logger.debug(repr(device))

        if device is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Device not found'
            )

        return pd_md.Device(**device.__dict__)
    except HTTPException:
        device_logger.error('Error getting device', exc_info=True)
        raise
    except:
        device_logger.error('Error getting device', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@device_router.get('/get/all/devices')
async def get_all_devices_api(db: Session = Depends(get_db)):
    try:
        device_logger.info('Request to get all devices')
        list_devices = DevicesRepo(db).get_all_devices()
        device_logger.info('All devices received')

        new_list = Func_API.convert_list_devices(list_devices)
        device_logger.info('Devices converted to pydantic model')

        return new_list
    except:
        device_logger.error('Error getting all devices', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@device_router.put('/update/device/{device_id}')
async def update_device_api(device_id: int, device: pd_md.DeviceUpdate, db: Session = Depends(get_db)):
    try:
        device_logger.info(f'Device update request: device_id={device_id}')
        new_device = DevicesRepo(db).update_device(device_id, **device.__dict__)
        device_logger.info('Device updated')

        if new_device is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Device not found'
            )

        return pd_md.Device(**new_device.__dict__)
    except HTTPException:
        device_logger.error('Error updating device', exc_info=True)
        raise
    except:
        device_logger.error('Error updating device', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@device_router.delete('/delete/device/{device_id}')
async def delete_device_api(device_id: int, db: Session = Depends(get_db)):
    try:
        device_logger.info(f'Request to delete device: device_id={device_id}')
        device = DevicesRepo(db).delete_device(device_id)
        device_logger.info('device deleted')

        if device is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Device not found'
            )
        return pd_md.Device(**device.__dict__)
    except HTTPException:
        device_logger.error('Error deleting device', exc_info=True)
        raise
    except:
        device_logger.error('Error deleting device', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


