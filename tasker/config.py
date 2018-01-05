"""
Config
"""
import json
from tasker.task import create_task, run_tasks

class Config:
    """Represents a config to run"""
    def __init__(self, tasks=None):
        if tasks is None:
            self.tasks = []
        else:
            self.tasks = tasks


def load_config(filename):
    """Loads a config files containing the tasks and settings to execute"""
    config_content = None
    with open(filename, "rt") as fp:
        config_content = json.load(fp)

    if config_content is None:
        raise Exception("Couldn't parse config")

    config = Config()
    tasks = config_content['tasks']
    for task in tasks:
        for k, v in task.items():
            new_task = create_task(k, **v)
            if new_task is not None:
                config.tasks.append(new_task)

    return config


def run_config(config):
    """Executes a config"""
    run_tasks(config.tasks)
