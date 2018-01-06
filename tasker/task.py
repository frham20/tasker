"""
Tasks
"""
from enum import Flag
from string import Template
import datetime
import os
import re
import zipfile
import logging
import dirsync
import isodate

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


def _list_filenames(path, recurse=False):
    filenames = []
    if recurse:
        filenames = [os.path.join(dirpath, os.path.normpath(f))
                     for dirpath, _, files in os.walk(path,
                                                      topdown=True,
                                                      onerror=None,
                                                      followlinks=True)
                     for f in files]
    else:
        filenames = [os.path.join(path, file) for file in os.listdir(path)]
    return filenames


def _filter_filenames(filenames, include=None, exclude=None):
    filtered_filenames = []
    for filename in filenames:
        skip_filename = False
        if include is not None:
            for pattern in include:
                if re.search(pattern, filename) is None:
                    skip_filename = True
                    break
        if exclude is not None:
            for pattern in exclude:
                if re.search(pattern, filename) is not None:
                    skip_filename = True
                    break
        if not skip_filename:
            filtered_filenames.append(filename)
    return filtered_filenames


class TaskDirectoryMirror(Task):
    """Mirror a whole directory tree"""
    def __init__(self, dst, src):
        super().__init__()
        self.src = src
        self.dst = dst

    def _do_work(self):
        self.logger.info('Copying %s in %s...', self.src, self.dst)
        dirsync.sync(self.src, self.dst, 'sync', create=True, purge=True, verbose=False, logger=self.logger)

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
        dirsync.sync(self.src, self.dst, 'sync', create=True, purge=False, verbose=False, logger=self.logger)

    @staticmethod
    def factory_name():
        return 'directory-copy'

    @staticmethod
    def create(**kwargs):
        return TaskDirectoryCopy(**kwargs)


class TaskArchiveCreate(Task):
    """Creates an archive of a whole directory tree"""
    def __init__(self, archive_name, dst, src, include=None, exclude=None):
        super().__init__()
        self.src = src
        self.dst = dst
        self.archive_name = archive_name
        self.include = include
        self.exclude = exclude

    def _do_work(self):
        formatted_name = TaskArchiveCreate._format_archive_name(self.archive_name)

        self.logger.info('Creating archive %s\\%s.zip...', self.dst, formatted_name)

        filenames = _list_filenames(self.src, recurse=True)
        filenames = _filter_filenames(filenames, include=self.include, exclude=self.exclude)

        os.makedirs(self.dst, mode=0o777, exist_ok=True)
        zip_filename = os.path.join(self.dst, '{}.zip'.format(formatted_name))
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_LZMA) as zf:
            for filename in filenames:
                zf.write(filename)

    @staticmethod
    def _format_archive_name(name):
        cur_time = datetime.datetime.now()
        tpl = Template(name)
        return tpl.substitute(YYYY=cur_time.year,
                              DD='{:02d}'.format(cur_time.day),
                              MM='{:02d}'.format(cur_time.month))

    @staticmethod
    def factory_name():
        return 'archive-create'

    @staticmethod
    def create(**kwargs):
        return TaskArchiveCreate(**kwargs)


class TaskFilePurge(Task):
    """Delete files based on conditions"""
    def __init__(self, path, recurse=False, include=None, exclude=None, older_than=None):
        super().__init__()
        self.path = path
        self.recurse = recurse
        self.include = include
        self.exclude = exclude

        # older_than should be a timedelta or a string using the ISO 8601 standard for Durations
        # see https://en.wikipedia.org/wiki/ISO_8601
        if isinstance(older_than, str):
            self.older_than = isodate.parse_duration(older_than)
        else:
            self.older_than = older_than

    def _do_work(self):
        self.logger.info('Purging files in %s...', self.path)

        filenames = _list_filenames(self.path, recurse=self.recurse)
        filenames = _filter_filenames(filenames, include=self.include, exclude=self.exclude)

        if self.older_than is not None:
            max_seconds = (datetime.datetime.now() - self.older_than).timestamp()
            old_filenames = []
            for filename in filenames:
                fs = os.lstat(filename)
                if fs.st_mtime <= max_seconds:
                    old_filenames.append(filename)
            filenames = old_filenames

        self.logger.info('Removing %d files...', len(filenames))
        for filename in filenames:
            self.logger.info('Removing %s', filename)
            os.remove(filename)

    @staticmethod
    def factory_name():
        return 'file-purge'

    @staticmethod
    def create(**kwargs):
        return TaskFilePurge(**kwargs)
