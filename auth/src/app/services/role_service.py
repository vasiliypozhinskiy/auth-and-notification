from app.services.storage.storage import roles_table
from app.utils.exceptions import AlreadyExistsError
from app.utils.exceptions import NotFoundError


class RoleService:
    @staticmethod
    def create_role(role: str) -> None:
        roles_table.create(data={}, new_id=role)

    def delete_role(self, role_title) -> None:
        roles_table.delete(filter={'title': role_title})

    @staticmethod
    def get_list_role():
        roles = roles_table.read(filter={})
        roles = [r['title'] for r in roles]
        return {"role_list": roles}

    def update_role(self, role_title, new_role):
        role = roles_table.read(filter={"title": role_title})
        if not role:
            raise NotFoundError("Role not found")

        roles = self.get_list_role()
        if new_role in roles["role_list"]:
            raise AlreadyExistsError("Role already exists")
        roles_table.update(data={"title": new_role}, filter={"title": role_title})


role_service = RoleService()
