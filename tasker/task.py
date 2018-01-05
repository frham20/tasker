"""
Tasks
"""
from enum import Flag
import os
import re
import zipfile
import logging
import dirsync

class TaskStatus(Flag):
    """The status of a task"""
    PENDING = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = 4
    STOPPED = (COMPLETED | FAILED)


class Task(object):
    """Base task class"""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.status = TaskStatus.PENDING

    def run(self):
        """Run the task"""
        self.status = TaskStatus.RUNNING
        try:
            self._do_work()
        except Exception as ex:
            self.status = TaskStatus.FAILED
            self.logger.exception(ex)
        else:
            self.status = TaskStatus.COMPLETED
        return self.status

    def _do_work(self):
        assert False, '_do_work needs to be implemented for derived tasks'

    @staticmethod
    def factory_name():
        """Returns the task factory name"""
        return 'base-task'

    @staticmethod
    def create(**kwargs):
        """Instantiate a task"""
        assert False, 'Cannot create base task instance'


def run_tasks(tasks):
    """Runs a series of tasks"""
    for task in tasks:
        status = task.run()
        if status == TaskStatus.FAILED:
            return False

    return True


def create_task(name, **kwargs):
    """Creates a new task based on factory task name and named args"""
    for subclass in Task.__subclasses__():
        if subclass.factory_name() == name:
            return subclass.create(**kwargs)
    return None


class TaskDirectoryMirror(Task):
    """Mirror a whole directory tree"""
    def __init__(self, dst, src):
        super().__init__()
        self.src = src
        self.dst = dst

    def _do_work(self):
        self.logger.info('Copying %s in %s...', self.src, self.dst)
        dirsync.sync(self.src, self.dst, 'sync', create=True, purge=True)

    @staticmethod
    def factory_name():
        return 'directory-mirror'

    @staticmethod
    def create(**kwargs):
        return TaskDirectoryMirror(**kwargs)


class TaskDirectoryCopy(Task):
    """Copies a whole directory tree"""
    def __init__(self, dst, src):
        super().__init__()
        self.src = src
        self.dst = dst

    def _do_work(self):
        self.logger.info('Copying %s in %s...', self.src, self.dst)
        dirsync.sync(self.src, self.dst, 'sync', create=True, purge=False)

    @staticmethod
    def factory_name():
        return 'directory-copy'

    @staticmethod
    def create(**kwargs):
        return TaskDirectoryCopy(**kwargs)


class TaskArchiveCreate(Task):
    """Creates an archive of a whole directory tree"""
    def __init__(self, archive_name, dst, src, exclude=None):
        super().__init__()
        self.src = src
        self.dst = dst
        self.archive_name = archive_name
        self.exclude = exclude

    def _do_work(self):
        self.logger.info('Creating archive %s\\%s.zip...', self.dst, self.archive_name)
        filenames = []
        for dirpath, _, files in os.walk(self.src, topdown=True, onerror=None, followlinks=True):
            for file in files:
                fullname = os.path.join(dirpath, file)
                skip_file = False
                if self.exclude is not None:
                    for exclusion in self.exclude:
                        if re.search(exclusion, fullname) is not None:
                            skip_file = True
                            break
                if not skip_file:
                    filenames.append(fullname)
        os.makedirs(self.dst, mode=0o777, exist_ok=True)
        zip_filename = os.path.join(self.dst, '{}.zip'.format(self.archive_name))
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_LZMA) as zf:
            for filename in filenames:
                zf.write(filename)

    @staticmethod
    def factory_name():
        return 'archive-create'

    @staticmethod
    def create(**kwargs):
        return TaskArchiveCreate(**kwargs)
