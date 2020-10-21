"""Authentication check functions."""

from logging import getLogger

from peewee import JOIN

from hwdb import Deployment, System

from termacls.orm import TypeAdmin


__all__ = [
    'can_administer_deployment',
    'can_administer_system',
    'can_deploy',
    'get_administerable_deployments',
    'get_administerable_systems'
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


def get_admin_types(account):
    """Returns a set of administrerable types for the given account."""

    for type_admin in TypeAdmin.select().where(
            TypeAdmin.account == account.id):
        yield type_admin.type


def get_administerable_deployments(account):
    """Yields deployments that the given account can administer."""

    if account.root:
        return Deployment.select().where(True)

    types = set(get_admin_types(account))
    return Deployment.select().where(Deployment.type << types)


def get_administerable_systems(account):
    """Yields systems with deployments that
    the given account can administer.
    """

    select = System.depjoin(join_type=JOIN.LEFT_OUTER)

    if account.root:
        return select.where(True)

    condition = Deployment.type << set(get_admin_types(account))
    return select.where(condition)
