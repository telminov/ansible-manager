import os
import signal
from time import sleep

from multiprocessing import Process
from subprocess import PIPE, Popen

from core import consts
from core import models


class TaskChecker:
    def run(self):
        """ Tasks monitoring and check status"""
        while True:
            self.check_in_progress()
            self.start_wait_tasks()
            sleep(1)

    @staticmethod
    def process_is_run(pid):
        return os.path.exists("/proc/%s" % pid)

    def check_in_progress(self):
        tasks = models.Task.objects.filter(status=consts.IN_PROGRESS)
        not_run_tasks = []
        for task in tasks:
            if not self.process_is_run(task.pid):
                not_run_tasks.append(task)

        for task in not_run_tasks:
            task.status = consts.FAIL
            task.save()

            models.TaskLog.objects.create(
                task=task,
                status=consts.FAIL,
                message='Task with pid %s is failed' % task.pid
            )

    @staticmethod
    def run_task(task_id):
        from django.db import connection
        connection.connection.close()
        connection.connection = None

        task = models.Task.objects.get(id=task_id)
        task.status = consts.IN_PROGRESS
        task.save()

        # TODO log for task bla bla bla started

        try:
            proc = Popen(task.get_command(splited=True), stdout=PIPE)
            while proc.poll() is None:
                output = proc.stdout.readline()
                models.TaskLog.objects.create(
                    task=task,
                    status=consts.IN_PROGRESS,
                    output=output
                )
            task.status = consts.COMPLETED
            task.save()
            models.TaskLog.objects.create(
                task=task,
                status=consts.COMPLETED,
                message='Task complete'
            )

        except Exception as e:
            pass
            # TODO log error

    def run_in_new_process(self, task):
        proc = Process(target=self.run_task, args=(task.id,))
        proc.start()

        from django.db import connection
        connection.connection.close()
        connection.connection = None

        # TODO log start process with pid

        task.pid = proc.pid
        task.save()

    def start_wait_tasks(self):
        tasks = models.Task.objects.filter(status=consts.WAIT)
        for task in tasks:
            self.run_in_new_process(task)


def stop(task):
    if task.status == consts.IN_PROGRESS and task.pid:
        try:
            os.kill(task.pid, signal.SIGTERM)
        except Exception as e:
            pass
            # TODO log error

        models.TaskLog.objects.create(
            task=task,
            status=consts.STOPPED,
            message='Task stopped'
        )



