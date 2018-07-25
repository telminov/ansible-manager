import os
import tempfile

from django.template.loader import render_to_string
from django.conf import settings


os.environ['ANSIBLE_NOCOWS'] = '1'


def make_command(task) -> str:
    """
    :param task: core.models.Task or core.models.TaskTemplate
    :return: ansible shell command
    """
    assert hasattr(task, 'hosts')
    assert hasattr(task, 'host_groups')
    assert hasattr(task, 'vars')

    if hasattr(task, 'inventory') and task.inventory:
        inventory_file_path = task.inventory.path
    else:
        inventory_file_path = create_inventory(task)

    verbose = ''
    if task.verbose:
        verbose = '-%s' % task.verbose

    # add task vars as extra variable argument
    extra_vars = ''
    for var in task.vars.all():
        extra_vars += '%s=%s ' % (var.name, var.value)
    extra_vars = '"%s"' % extra_vars

    command = [settings.ANSIBLE_PLAYBOOK_BIN_PATH, '-i', inventory_file_path, '-u', task.ansible_user.name,
               '-e', extra_vars, verbose, task.playbook]

    command = ' '.join(command)
    return command


def create_inventory(task) -> str:
    assert hasattr(task, 'hosts')
    assert hasattr(task, 'host_groups')
    # assert hasattr(task, 'vars')

    hosts = set(task.hosts.all())
    for group in task.host_groups.all():
        hosts.update(group.hosts.all())

    hosts_vars = {}
    # base - host vars
    for host in hosts:
        hosts_vars[host] = {var.name: var for var in host.get_vars()}

    # # higher priority - task vars
    # for var in task.vars.all():
    #     for host in hosts_vars.keys():
    #         hosts_vars[host][var.name] = var

    # sort vars by name
    for host, host_vars in hosts_vars.items():
        hosts_vars[host] = sorted(host_vars.values(), key=lambda v: v.name)

    tempdir = tempfile.mkdtemp()
    file_path = os.path.join(tempdir, 'inventory')
    with open(file_path, 'w') as file:
        content = render_to_string('core/ansible/inventory', {'hosts_vars': hosts_vars})
        file.write(content)
    return file_path


def get_inventory_file_path(ansible_shell_command: str):
    return ansible_shell_command.split(' ')[2]  # TODO: replace by regexp

