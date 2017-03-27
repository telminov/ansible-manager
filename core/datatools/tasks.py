import os
import signal
import traceback
from time import sleep
from multiprocessing import Process
import asyncio
from asyncio.subprocess import PIPE, create_subprocess_shell

from django.conf import settings

from core import consts
from core import models
import core.datatools.ansible


class TaskManager:
    def run(self):
        """ Tasks monitoring and check status"""
        while True:
            self.check_in_progress_tasks()
            self.start_waiting_tasks()
            sleep(1)

    def check_in_progress_tasks(self):
        tasks = models.Task.objects.filter(status=consts.IN_PROGRESS, pid__isnull=False)
        not_run_tasks = []
        for task in tasks:
            if not task.pid:
                task.logs.create(
                    status=consts.FAIL,
                    message='Error "pid is None"',
                )
                continue

            if not self._is_process_run(task.pid):
                not_run_tasks.append(task)

        for task in not_run_tasks:
            task.status = consts.FAIL
            task.save()

            task.logs.create(
                status=consts.FAIL,
                message='Task with pid %s is not running' % task.pid
            )

    def start_waiting_tasks(self):
        tasks = models.Task.objects.filter(status=consts.WAIT)
        for task in tasks:
            self.run_task_process(task)

    @classmethod
    def run_task(cls, task_id):
        from django.db import connection
        connection.connection.close()
        connection.connection = None

        task = models.Task.objects.get(id=task_id)

        shell_command = task.get_ansible_command()
        inventory_file_path = core.datatools.ansible.get_inventory_file_path(shell_command)
        task.logs.create(
            status=consts.IN_PROGRESS,
            message='Command: %s' % shell_command,
        )

        cwd = settings.ANSIBLE_WORK_DIR
        task.logs.create(
            status=consts.IN_PROGRESS,
            message='Working directory: %s' % cwd,
        )

        try:
            loop = asyncio.get_event_loop()

            create_proc = create_subprocess_shell(shell_command, stdout=PIPE, stderr=PIPE, cwd=cwd)
            proc = loop.run_until_complete(create_proc)

            tasks = [
                proc.wait(),
                cls._log_output(task, proc.stdout, consts.IN_PROGRESS),
                cls._log_output(task, proc.stderr, consts.FAIL),
            ]
            loop.run_until_complete(asyncio.wait(tasks))

            code = proc.returncode
            if code == 0:
                task.logs.create(
                    status=consts.COMPLETED,
                    message='Completed.'
                )
                task.status = consts.COMPLETED
                task.save()
            else:
                task.logs.create(
                    status=consts.FAIL,
                    message='Failed with status code %s' % code
                )
                task.status = consts.FAIL
                task.save()

        except Exception as e:
            task.status = consts.FAIL
            task.save()
            traceback_message = traceback.format_exc()
            task.logs.create(
                output=traceback_message,
                message='Progress error "%s"' % e,
                status=consts.FAIL
            )
        finally:
            os.remove(inventory_file_path)
            if os.path.exists("/proc/%s" % task.pid):
                os.kill(task.pid, signal.SIGTERM)

    @staticmethod
    def stop_task(task):
        assert task.status in consts.RUN_STATUSES

        if task.status == consts.IN_PROGRESS and task.pid:
            try:
                os.kill(task.pid, signal.SIGTERM)
            except Exception as e:
                traceback_message = traceback.format_exc()
                task.logs.create(
                    output=traceback_message,
                    messgae='Stop error "%s"' % e,
                    status=consts.FAIL
                )

        task.status = consts.STOPPED
        task.save()
        task.logs.create(
            status=consts.STOPPED,
            message='Task stopped'
        )

    def run_task_process(self, task):
        proc = Process(target=self.run_task, args=(task.id,))
        proc.start()
        pid = proc.pid

        from django.db import connection
        connection.connection.close()
        connection.connection = None

        task.pid = pid
        task.status = consts.IN_PROGRESS
        task.save()

        task.logs.create(
            status=consts.IN_PROGRESS,
            message='Start task with pid %s' % pid,
        )

    @staticmethod
    def _is_process_run(pid):
        return os.path.exists("/proc/%s" % pid)

    @staticmethod
    async def _log_output(task, stream, status):
        while True:
            output = await stream.readline()
            if not output:
                return

            task.logs.create(
                status=status,
                output=output,
            )