"""Common object-relational mappings."""

from peewee import ForeignKeyField, Model

from his import Account
from hwdb import Type
from mdb import Customer
from peeweeplus import EnumField, MySQLDatabase

from termacls.config import CONFIG


__all__ = ['TypeAdmin', 'ManufacturerAdmin']


DATABASE = MySQLDatabase.from_config(CONFIG['db'])


class TermaclsModel(Model):
    """Base model for the termacl database."""

    class Meta:     # pylint: disable=C0111,R0903
        database = DATABASE
        schema = database.database


class TypeAdmin(TermaclsModel):
    """Administrators of certain deployment types."""

    class Meta:     # pylint: disable=C0111,R0903
        table_name = 'type_admin'

    account = ForeignKeyField(
        Account, column_name='account', on_delete='CASCADE')
    type = EnumField(Type)


class ManufacturerAdmin(TermaclsModel):
    """Administrators of certain system manufacturers."""

    class Meta:     # pylint: disable=C0111,R0903
        table_name = 'manufacturer_admin'

    account = ForeignKeyField(
        Account, column_name='account', on_delete='CASCADE')
    manufacturer = ForeignKeyField(
        Customer, column_name='manufacturer', on_delete='CASCADE')
