#!/usr/bin/env python

""" Initialize a repo with some commits. """

import argparse
import logging
import os
import random
import subprocess
import time


WORKER_QUEUE = []


class Worker(object):

    """Models a worker."""

    __repo = None

    def __init__(self, worker_id, branch):
        super(Worker, self).__init__()
        self.__worker_id = worker_id
        self.__branch = branch
        self.__branch_name = None
        self.__branch_has_commits = False

    def do_work(self):
        if self.__branch:
            action = random.randint(0, 6)
            if 2 > action and self.__branch_action_possible():
                self.__branch_action()
            elif 5 < action:
                self.__do_nothing()
            else:
                self.__commit()
        else:
            self.__commit()

    def __do_nothing(self):
        logging.debug("  ..worker #%d is doing nothing.", self.__worker_id)

    def __branch_action_possible(self):
        return self.__branch_has_commits or not self.__branch_name

    def __branch_action(self):
        self.__switch_worker()
        if not self.__branch_name:
            logging.debug("  ..worker #%d would branch.", self.__worker_id)
            self.__branch_name = "Worker%dTopicBranch" % self.__worker_id
        else:
            logging.debug("  .. worker #%d would merge.", self.__worker_id)
            self.__branch_has_commits = False
            self.__branch_name = None

    def __commit(self):
        self.__switch_worker()

        logging.debug("  ..worker #%d is doing some work.", self.__worker_id)

        with open("Worker%dFile" % self.__worker_id, "a") as fil:
            fil.write("Writing a line at %s\n" % time.ctime())

        if self.__branch_name:
            self.__branch_has_commits = True

    def __switch_worker(self):
        name = "John Doe #%d" % self.__worker_id
        email = "johndoe%d@localhost" % self.__worker_id
        logging.debug("  ..switching to committer <%s, %s>", name, email)


def setup_logging(args):
    logging.basicConfig(format='%(asctime)-15s %(message)s')

    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARNING)

    logger.debug("Finished setting up logging")


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument('REPO', type=str, help="The path to the repo")
    parser.add_argument('--branch',
                        help="Should branching and merging be allowed",
                        action="store_true")
    parser.add_argument('--actions', type=int,
                        help="The amount of actions to perform", default=1)
    parser.add_argument('--committers', type=int,
                        help="The amount of committers", default=1)
    parser.add_argument("--debug", help="Increase debug logging",
                        action="store_true")

    return parser.parse_args()


def create_repo(repo):
    """Create the repo."""

    if not os.path.exists(repo):
        logging.debug("Creating %s.", repo)
        os.mkdir(repo)

    os.chdir(repo)

    if not os.path.exists('.git'):
        logging.debug("Initializing repo")
        subprocess.call(["git", "init"])


def create_workers(committer_count, branch):
    """Create the workers."""

    for i in range(0, committer_count):
        logging.debug("Creating worker #%d", i)
        WORKER_QUEUE.append(Worker(i, branch))


def start_working(actions):
    """Perform actions number of actions on the repo."""

    for i in range(0, actions):
        logging.debug("..performing action %d.", i)
        worker = WORKER_QUEUE.pop(0)
        worker.do_work()
        WORKER_QUEUE.append(worker)


def main():
    """Provide the main functionality of the script."""
    args = parse_arguments()
    setup_logging(args)

    create_repo(args.REPO)

    random.seed()
    create_workers(args.committers, args.branch)
    start_working(args.actions)


if __name__ == '__main__':
    main()
