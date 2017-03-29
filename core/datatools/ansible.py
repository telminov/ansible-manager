import os
import tempfile

from django.template.loader import render_to_string
from django.conf import settings


def make_command(task) -> str:
    """
    :param task: core.models.Task or core.models.TaskTemplate
    :return: ansible shell command
    """
    assert hasattr(task, 'hosts')
    assert hasattr(task, 'host_groups')
    assert hasattr(task, 'vars')

    inventory_file_path = create_inventory(task)

    command = [settings.ANSIBLE_PLAYBOOK_BIN_PATH, '-i', inventory_file_path, settings.ANSIBLE_VERBOSE, task.playbook,
               '-u', task.ansible_user]
    command = ' '.join(command)
    return command


def create_inventory(task) -> str:
    assert hasattr(task, 'hosts')
    assert hasattr(task, 'host_groups')
    assert hasattr(task, 'vars')

    tempdir = tempfile.mkdtemp()
    file_path = os.path.join(tempdir, 'inventory')
    with open(file_path, 'w') as file:
        content = render_to_string('core/ansible/inventory', {'object': task})
        file.write(content)
    return file_path


def get_inventory_file_path(ansible_shell_command: str):
    return ansible_shell_command.split(' ')[2]  # TODO: replace by regexp

