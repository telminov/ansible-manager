from django.test import TestCase
from django.urls import reverse

from core.tests import factories


class TaskLogsApiView(TestCase):

    def setUp(self):
        factories.AnsibleUserFactory.create()
        group_with_test = factories.HostGroupFactory.create()
        host_with_test = factories.HostFactory.create(groups=(group_with_test,))
        tsk_tmlt_wth_tst = factories.TaskTemplateFactory.create(hosts=(host_with_test,), host_groups=(group_with_test,))
        task = factories.TaskFactory.create(
            hosts=(host_with_test,),
            host_groups=(group_with_test,),
            template=tsk_tmlt_wth_tst,
            playbook='/home/pc/ansible/playbooks/main.yml',
            status='in_progress'
        )
        factories.TaskLogFactory.create(task=task)

    def test_queryset(self):
        response = self.client.get(reverse('rest_task_logs', args=['1']))

        self.assertEqual(len(response.json()), 1)
