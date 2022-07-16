import uuid
from datetime import datetime

from app.core import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import UniqueConstraint




class User(db.Model):
    __tablename__ = "user"
    __table_args__ = {"schema": "auth"}

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    login = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String, nullable=False)
    is_superuser = db.Column(db.Boolean, default=False)

    oauth_type = db.Column(db.TEXT)
    oauth_id = db.Column(db.TEXT)

    totp_secret = db.Column(db.TEXT)

    email = db.Column(db.String, unique=True, index=True)

    user_data = db.relationship("UserData", backref="user")
    history_entries = db.relationship("LoginHistory", backref="user")
    roles = db.relationship(
        "Role", secondary="auth.user_role", backref=db.backref("user", lazy="dynamic")
    )

    def __repr__(self):
        return f"<User: {self.login}>"


class UserData(db.Model):
    __tablename__ = "user_data"
    __table_args__ = {"schema": "auth"}

    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id))

    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    birthdate = db.Column(db.Date)

    def __repr__(self):
        return f"<UserData: {self.user_id}>"


def create_partition(target, connection, **kwargs) -> None:
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "auth.user_login_winter_2022"
        PARTITION OF "auth.login_history"
        FOR VALUES FROM ('2021-12-01') TO ('2022-02-28'); """
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "auth.user_login_spring_2022"
        PARTITION OF "auth.login_history"
        FOR VALUES FROM ('2022-03-01') TO ('2022-05-31'); """
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "auth.user_login_summer_2022"
        PARTITION OF "auth.login_history"
        FOR VALUES FROM ('2022-06-01') TO ('2022-08-31'); """
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "auth.user_login_autumn_2022"
        PARTITION OF "auth.login_history"
        FOR VALUES FROM ('2022-09-01') TO ('2022-11-30'); """
    )


class LoginHistory(db.Model):
    __tablename__ = "login_history"
    __table_args__ = (
        UniqueConstraint('id', 'created_at'),
        {
            "schema": "auth",
            'postgresql_partition_by': 'RANGE (created_at)',
            'listeners': [('after_create', create_partition)],
        }
    )
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    user_agent = db.Column(db.String)
    refresh_token = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey(User.id))

    def __repr__(self):
        return f"<LoginHistory: {self.user_id} {self.created_at}>"


class Role(db.Model):
    __tablename__ = "role"
    __table_args__ = {"schema": "auth"}

    title = db.Column(db.String(50), primary_key=True, unique=True, nullable=False)

    def __repr__(self):
        return f"<Role: {self.title}>"


user_role = db.Table(
    "user_role",
    db.Column("user_id", UUID(as_uuid=True), db.ForeignKey(User.id)),
    db.Column("role_id", db.String, db.ForeignKey(Role.title)),
    schema="auth"
)
