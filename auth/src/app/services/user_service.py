import uuid

from pydantic import ValidationError

from app.models.db_models import User
from app.services.storage.storage import user_table, user_data_table, user_login_history_table
from app.models.service_models import (
    UserCreds,
    User as UserServiceModel,
    HistoryEntry as HistoryEntryServiceModel
)

from app.utils.exceptions import (
    FieldValidationError,
    AccessDenied,
    NotFoundError
)
from app.utils.utils import hash_password, row2dict, check_password


class UserService:
    def create_user(self, user_data: dict) -> uuid:
        self.validate_user(user_data)
        user_data["password"] = hash_password(user_data["password"]).decode()

        user_id = user_table.create(data=user_data)
        user_data.update({"user_id": user_id})
        _ = user_data_table.create(data=user_data)

        return user_id

    def get_user_grpc(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        role_list = [role.title for role in user.roles]
        return role_list

    def get_user(self, user_id) -> UserServiceModel:
        user_creds = user_table.read(filter={"id": user_id})
        user_data = user_data_table.read(filter={"user_id": user_id})
        role = user_data_table.get_role(user_id)
        if user_creds is None:
            user_creds = UserCreds(id=user_id, login='login', password='Password1!', email='email@email.com')
            user_creds = user_creds.dict()
        if user_data is None:
            user_data = {}
        if (not user_creds) or (not user_data):
            raise NotFoundError

        user_data.update(user_creds)
        user_data['roles'] = role
        out = self.validate_user(user_data=user_data)
        return out

    def update_user(self, user_id, user_data) -> None:
        if "password" in user_data:
            raise AccessDenied
        user_table.update(data=user_data, filter={"id": user_id})
        user_data_table.update(data=user_data, filter={"user_id": user_id})

    def delete_user(self, user_id) -> None:
        user_data_table.delete(filter={"user_id": user_id})
        user_login_history_table.delete(filter={"user_id": user_id})
        user_table.delete(filter={"id": user_id})
        
    def change_password(self, user_id, passwords) -> None:
        user_creds = user_table.read(filter={"id": user_id})
        if not check_password(passwords["old_password"], user_creds["password"]):
            raise AccessDenied("Wrong password")
        user_table.update(
            data={"password": hash_password(passwords["new_password"]).decode()},
            filter={"id": user_id},
        )

    def get_history(self, user_id):
        history = user_login_history_table.read(filter={"user_id": user_id})
        history = [HistoryEntryServiceModel(**row2dict(row)) for row in history]

        return history

    @staticmethod
    def validate_user(user_data) -> UserServiceModel:
        try:
            return UserServiceModel(**user_data)
        except ValidationError as e:
            raise FieldValidationError(message=e.__repr__())


user_service = UserService()
