"""Authentication check functions."""

from logging import getLogger

from mdb import Customer
from terminallib import Deployment, System, Type

from termacls.orm import TypeAdmin, ManufacturerAdmin


__all__ = [
    'can_administer_deployment',
    'can_administer_system',
    'can_deploy',
    'can_setup_system',
    'get_administerable_deployments',
    'get_administerable_systems',
    'get_setupable_systems'
]


LOGGER = getLogger('termacls')


def can_administer_deployment(account, deployment):
    """Checks whether the respective account
    may administer the given deployment.
    """

    return deployment in get_administerable_deployments(account)


def can_administer_system(account, system):
    """Checks whether the respective account
    may administer the given system.
    """

    return system in get_administerable_systems(account)


def can_deploy(account, system, deployment):
    """Checks whether the account can deployment
    the respective system at the given deployment.
    """

    if not can_administer_system(account, system):
        return False

    if deployment is not None:
        if not can_administer_deployment(account, deployment):
            return False

    if system.deployment is not None:
        if not can_administer_deployment(account, system.deployment):
            return False

    return True


def can_setup_system(account, system):
    """Checks whether the respective account may setup the given system."""

    if account.root:
        return True

    if account.customer == system.manufacturer:
        return True

    return system in get_setupable_systems(account)


def get_admin_types(account):
    """Returns a set of administrerable types for the given account."""

    if account.root:
        return Type

    return {
        type_admin.type for type_admin in TypeAdmin.select().where(
            TypeAdmin.account == account.id)
    }


def get_administerable_deployments(account):
    """Yields deployments that the given account can administer."""

    if account.root:
        return Deployment

    types = get_admin_types(account)
    return Deployment.select().where(Deployment.type << types)


def get_admin_manufacturers(account):
    """Yields manufacturers, which the given account can administer."""

    if account.root:
        return Customer

    return {
        manufacturer_admin.manufacturer for manufacturer_admin in
        ManufacturerAdmin.select().where(
            ManufacturerAdmin.account == account.id)
    }


def get_administerable_systems(account):
    """Yields systems that the given account can administer."""

    if account.root:
        return System

    select = System.select().join(Deployment)
    condition = System.manufacturer << get_admin_manufacturers(account)
    condition |= Deployment.type << get_admin_types(account)
    return select.where(condition)


def get_setupable_systems(account):
    """Yields systems that the account may setup."""

    if account.root:
        return System

    return System.select().where(System.manufacturer == account.customer)
