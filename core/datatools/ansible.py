import os
import tempfile

from django.template.loader import render_to_string


def make_command(item, splited=False):
    inventory_file_path = create_inventory(item)

    command = ['ansible-playbook', '-i', inventory_file_path, item.playbook]
    if not splited:
        command = ' '.join(command)
    return command


def create_inventory(item) -> str:
    tempdir = tempfile.mkdtemp()
    file_path = os.path.join(tempdir, 'inventory.yml')
    with open(file_path, 'w') as file:
        content = render_to_string('core/ansible/inventory', {'object': item})
        file.write(content)

    return file_path



