from DataBase.models import Users, Devices
from ..routs import pydantic_models as pd_md


class FunctionsAPI:

    @staticmethod
    def convert_list_users(lst: list[Users]) -> list[pd_md.User]:
        """
        Func what convert DataBase ORM to PyDantic models
        :param lst: List of Users ORM models from DataBase
        :return: List of PyDantic models of Users
        """
        new_list = []
        for elem in lst:
            new_list.append(pd_md.User(**elem.__dict__))

        return new_list

    @staticmethod
    def convert_list_devices(lst: list[Devices]) -> list[pd_md.Device]:
        """
        Func what convert DataBase ORM to PyDantic models
        :param lst: List of Devices ORM models from DataBase
        :return: List of PyDantic models of Devices
        """
        new_list = []
        for elem in lst:
            new_list.append(pd_md.Device(**elem.__dict__))

        return new_list