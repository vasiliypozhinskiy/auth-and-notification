import pyotp

from app.services.storage.storage import user_table
from app.utils.exceptions import AccessDenied


class TOTPService:
    @staticmethod
    def generate_provisioning_uri(user_data):
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)

        user_table.update(data={"totp_secret": secret}, filter={"id": user_data["user_id"]})
        return totp.provisioning_uri(name=str(user_data["user_id"]), issuer_name='Awesome Praktikum app')

    @staticmethod
    def verify_code(user_id, code):
        user = user_table.read(filter={"id": user_id})
        secret = user["totp_secret"]

        totp = pyotp.TOTP(secret)
        if not totp.verify(code):
            raise AccessDenied(message="Wrong code")


totp_service = TOTPService()