"""Authentication check functions."""

from logging import getLogger

from terminallib import Deployment, System

from termacls.orm import TypeAdmin, ManufacturerAdmin


__all__ = [
    'can_administer_deployment',
    'can_administer_system',
    'can_setup_system',
    'get_administerable_deployments',
    'get_administerable_systems',
    'get_setupable_systems'
]


DEP_TYPEADM_JOIN = Deployment.type == TypeAdmin.type
SYSTEM_MANU_JOIN = System.manufacturer == ManufacturerAdmin.manufacturer
LOGGER = getLogger('termacls')


def can_administer_deployment(account, deployment):
    """Checks whether the respective account
    may administer the given deployment.
    """

    if account.root:
        return True

    try:
        TypeAdmin.get(
            (TypeAdmin.account == account)
            & (TypeAdmin.type == deployment.type))
    except TypeAdmin.DoesNotExist:
        LOGGER.debug(
            'Account "%s" can not administer deployment "%s".', account,
            deployment)
        return False

    return True


def can_administer_system(account, system):
    """Checks whether the respective account
    may administer the given system.
    """

    if account.root:
        return True

    try:
        ManufacturerAdmin.get(
            (ManufacturerAdmin.account == account)
            & (ManufacturerAdmin.manufacturer == system.manufacturer))
    except ManufacturerAdmin.DoesNotExist:
        LOGGER.debug(
            'Account "%s" can not administer system "%s".', account, system)
        return False

    return True


def can_setup_system(account, system):
    """Checks whether the respective account may setup the given system."""

    if account.root:
        return True

    return system.manufacturer == account.customer


def get_administerable_deployments(account):
    """Yields deployments that the given account can administer."""

    if account.root:
        return Deployment

    return Deployment.select().join(TypeAdmin, on=DEP_TYPEADM_JOIN).where(
        TypeAdmin.account == account)


def get_administerable_systems(account):
    """Yields systems that the given account can administer."""

    if account.root:
        return System

    return System.select().join(ManufacturerAdmin, on=SYSTEM_MANU_JOIN).where(
        ManufacturerAdmin.account == account)


def get_setupable_systems(account):
    """Yields systems that the account may setup."""

    if account.root:
        return System

    return System.select().where(System.manufacturer == account.customer)
