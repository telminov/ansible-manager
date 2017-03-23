import os
import tempfile

from django.template.loader import render_to_string
from django.conf import settings


def make_command(item, splited=False) -> str:
    inventory_file_path = create_inventory(item)

    command = [settings.ANSIBLE_PLAYBOOK_BIN_PATH, '-i', inventory_file_path, settings.ANSIBLE_VERBOSE, item.playbook]

    if settings.ANSIBLE_USER:
        command.extend(['-u', settings.ANSIBLE_USER])

    if not splited:
        command = ' '.join(command)
    return command


def create_inventory(item) -> str:
    tempdir = tempfile.mkdtemp()
    file_path = os.path.join(tempdir, 'inventory')
    with open(file_path, 'w') as file:
        content = render_to_string('core/ansible/inventory', {'object': item})
        file.write(content)
    return file_path



