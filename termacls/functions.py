"""Authentication check functions."""

from logging import getLogger

from peewee import JOIN

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

    deployments = get_administerable_deployments(account)

    try:
        return deployments.where(Deployment.id == deployment).get()
    except Deployment.DoesNotExist:
        return False


def can_administer_system(account, system):
    """Checks whether the respective account
    may administer the given system.
    """

    systems = get_administerable_systems(account)

    try:
        return systems.where(System.id == system).get()
    except System.DoesNotExist:
        return False


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

    try:
        return get_setupable_systems(account).where(System.id == system).get()
    except System.DoesNotExist:
        return False


def get_admin_types(account):
    """Returns a set of administrerable types for the given account."""

    for type_admin in TypeAdmin.select().where(
            TypeAdmin.account == account.id):
        yield type_admin.type


def get_administerable_deployments(account):
    """Yields deployments that the given account can administer."""

    if account.root:
        return Deployment.select().where(True)

    types = get_admin_types(account)
    return Deployment.select().where(Deployment.type << types)


def get_admin_manufacturers(account):
    """Yields manufacturers, which the given account can administer."""

    for manufacturer_admin in ManufacturerAdmin.select().where(
            ManufacturerAdmin.account == account.id):
        yield manufacturer_admin.manufacturer


def get_administerable_systems(account):
    """Yields systems that the given account can administer."""

    if account.root:
        return System.select().where(True)

    select = System.select().join(Deployment, join_type=JOIN.LEFT)
    condition = System.manufacturer << set(get_admin_manufacturers(account))
    condition |= Deployment.type << set(get_admin_types(account))
    return select.where(condition)


def get_setupable_systems(account):
    """Yields systems that the account may setup."""

    if account.root:
        return System.select().where(True)

    manufacturers = set(get_admin_manufacturers(account))
    manufacturers.add(account.customer)
    return System.select().where(System.manufacturer << manufacturers)
