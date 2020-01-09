"""Authentication check functions."""

from logging import getLogger

from terminallib import Deployment, System

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

    if account.root:
        return True

    try:
        TypeAdmin.get(
            (TypeAdmin.account == account.id)
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
            (ManufacturerAdmin.account == account.id)
            & (ManufacturerAdmin.manufacturer == system.manufacturer))
    except ManufacturerAdmin.DoesNotExist:
        LOGGER.debug(
            'Account "%s" can not administer system "%s".', account, system)
        return False

    return True


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

    for manufacturer_admin in ManufacturerAdmin.select(
            ManufacturerAdmin.account == account.id):
        if manufacturer_admin.manufacturer == system.manufacturer:
            return True

    return False


def get_administerable_deployments(account):
    """Yields deployments that the given account can administer."""

    if account.root:
        return Deployment

    types = {type_admin.type for type_admin in TypeAdmin.select().where(
        TypeAdmin.account == account.id)}
    return Deployment.select().where(Deployment.type << types)


def get_administerable_systems(account):
    """Yields systems that the given account can administer."""

    if account.root:
        return System

    manufacturers = {
        manufacturer_admin.manufacturer for manufacturer_admin in
        ManufacturerAdmin.select().where(
            ManufacturerAdmin.account == account.id)}
    return System.select().where(System.manufacturer << manufacturers)


def get_setupable_systems(account):
    """Yields systems that the account may setup."""

    if account.root:
        return System

    return System.select().where(System.manufacturer == account.customer)
