"""Common object-relational mappings."""

from peewee import ForeignKeyField, Model

from his import Account
from hwdb import DeploymentType, Group
from peeweeplus import EnumField, MySQLDatabaseProxy


__all__ = ["GroupAdmin", "TypeAdmin"]


DATABASE = MySQLDatabaseProxy("termacls")


class TermaclsModel(Model):
    """Base model for the termacl database."""

    class Meta:
        database = DATABASE
        schema = database.database


class GroupAdmin(TermaclsModel):
    """Administrators of certain hardware database groups."""

    class Meta:
        table_name = "group_admin"

    account = ForeignKeyField(Account, column_name="account", on_delete="CASCADE")
    group = ForeignKeyField(Group, column_name="group", on_delete="CASCADE")


class TypeAdmin(TermaclsModel):
    """Administrators of certain deployment types."""

    class Meta:
        table_name = "type_admin"

    account = ForeignKeyField(Account, column_name="account", on_delete="CASCADE")
    type = EnumField(DeploymentType)
