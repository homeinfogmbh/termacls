"""Authentication check functions."""

from logging import getLogger
from typing import Generator, Iterable, Iterator

from peewee import Expression

from his import Account
from hwdb import Deployment, DeploymentType, Group, System

from termacls.orm import GroupAdmin, TypeAdmin


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


def can_administer_deployment(
        account: Account,
        deployment: Deployment
) -> bool:
    """Checks whether the respective account
    may administer the given deployment.
    """

    deployments = get_administerable_deployments(account)

    try:
        return deployments.where(Deployment.id == deployment).get()
    except Deployment.DoesNotExist:
        return False


def can_administer_system(account: Account, system: System) -> bool:
    """Checks whether the respective account
    may administer the given system.
    """

    systems = get_administerable_systems(account)

    try:
        return systems.where(System.id == system).get()
    except System.DoesNotExist:
        return False


def can_deploy(
        account: Account,
        system: System,
        deployment: Deployment
) -> bool:
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


def get_admin_types(account: Account) -> Generator[DeploymentType, None, None]:
    """Returns a set of types for the given
    account that they can administer.
    """

    for record in TypeAdmin.select().where(TypeAdmin.account == account.id):
        yield record.type


def get_deployment_admin_condition(account: Account) -> Expression:
    """Returns the condition to administer deployments."""

    if account.root:
        return True

    return Deployment.type << set(get_admin_types(account))


def get_administerable_deployments(account: Account) -> Iterable[Deployment]:
    """Yields deployments that the given account can administer."""

    return Deployment.select().where(get_deployment_admin_condition(account))


def get_admin_groups(account: Account) -> Iterator[Group]:
    """Yields groups the account is a member of."""

    for record in GroupAdmin.select().where(GroupAdmin.account == account):
        yield record.group


def get_system_admin_condition(account: Account) -> Expression | bool:
    """Returns the condition to administer systems."""

    if account.root:
        return True

    return System.group << set(get_admin_groups(account))


def get_administerable_systems(account: Account) -> Iterable[System]:
    """Yields systems with deployments that
    the given account can administer.
    """

    return System.select().where(get_system_admin_condition(account))
