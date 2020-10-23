"""Authentication check functions."""

from logging import getLogger

from hwdb import Deployment, System

from termacls.orm import TypeAdmin


__all__ = [
    'can_administer_deployment',
    'can_administer_system',
    'can_deploy',
    'get_deployment_admin_condition',
    'get_administerable_deployments',
    'get_system_admin_condition',
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

    for record in TypeAdmin.select().where(TypeAdmin.account == account.id):
        yield record.type


def get_deployment_admin_condition(account):
    """Returns the condition to adminster deployments."""

    if account.root:
        return True

    return Deployment.type << set(get_admin_types(account))


def get_administerable_deployments(account):
    """Yields deployments that the given account can administer."""

    return Deployment.select().where(get_deployment_admin_condition(account))


def get_system_admin_condition(account):
    """Returns the condition to administer systems."""

    if account.root:
        return True

    return System.operator == account.customer


def get_administerable_systems(account):
    """Yields systems with deployments that
    the given account can administer.
    """

    return System.select().where(get_system_admin_condition(account))
