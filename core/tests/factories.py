import factory

from django.contrib.auth.models import User
from django.contrib.auth import settings

from core import models


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: '%s user' % n)


class VariableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Variable

    name = 'Test name'
    value = 'Test value'

    @factory.post_generation
    def vars(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for var in extracted:
                self.vars.add(var)


class HostGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.HostGroup

    name = 'Test host group name'


class HostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Host

    name = 'test name host'
    address = '192.168.19.19'

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.groups.add(group)

    @factory.post_generation
    def vars(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for var in extracted:
                self.vars.add(var)


class AnsibleUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AnsibleUser

    name = 'Test name'


class TaskTemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TaskTemplate

    name = 'Test name task template'
    description = 'Test description'
    playbook = '/home/pc/ansible/playbooks/test.yml'
    verbose = ''
    ansible_user = factory.SubFactory(AnsibleUserFactory)

    @factory.post_generation
    def hosts(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for host in extracted:
                self.hosts.add(host)

    @factory.post_generation
    def host_groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.host_groups.add(group)

    @factory.post_generation
    def vars(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for var in extracted:
                self.vars.add(var)


class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Task

    playbook = '/home/'
    template = factory.SubFactory(TaskTemplateFactory)
    status = 'in_progress'
    pid = 999
    user = factory.SubFactory(UserFactory)
    verbose = 'v'
    ansible_user = factory.SubFactory(AnsibleUserFactory)

    @factory.post_generation
    def hosts(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for host in extracted:
                self.hosts.add(host)

    @factory.post_generation
    def host_groups(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for group in extracted:
                self.host_groups.add(group)

    @factory.post_generation
    def vars(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for var in extracted:
                self.vars.add(var)


class TaskLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TaskLog

    task = factory.SubFactory(TaskFactory)
    status = 'in_progress'
    output = ''
    message = ''


def create_data_for_search_template():
    group_with_test = HostGroupFactory.create()
    group_without_test = HostGroupFactory.create(name='Jesus')
    host_with_test = HostFactory.create(groups=(group_with_test,))
    host_without_test = HostFactory.create(
        name='host',
        address='192.168.19.18',
        groups=(group_without_test,)
    )
    TaskTemplateFactory.create(hosts=(host_with_test,), host_groups=(group_with_test,))
    TaskTemplateFactory.create(
        name='Other Jesus test',
        hosts=(host_without_test,),
        host_groups=(group_without_test,)
    )


def create_data_for_search_task():
    group_with_test = HostGroupFactory.create()
    group_without_test = HostGroupFactory.create(name='Jesus')
    host_with_test = HostFactory.create(groups=(group_with_test,))
    host_without_test = HostFactory.create(name='host', address='192.168.19.18', groups=(group_without_test,))
    tsk_tmlt_wth_tst = TaskTemplateFactory.create(hosts=(host_with_test,), host_groups=(group_with_test,))
    tsk_tmlt_wthout_tst = TaskTemplateFactory.create(
        name='Other Jesus test',
        hosts=(host_without_test,),
        host_groups=(group_without_test,)
    )
    TaskFactory.create(hosts=(host_with_test,), host_groups=(group_with_test,),
                       template=tsk_tmlt_wth_tst, playbook='/tmp/playbooks/test.yml')
    TaskFactory.create(
        hosts=(host_without_test,),
        host_groups=(group_without_test,),
        template=tsk_tmlt_wthout_tst,
        playbook=settings.ANSIBLE_PLAYBOOKS_PATH + '/test.yml',
        status='fail'
    )
