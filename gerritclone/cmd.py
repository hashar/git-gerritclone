#!/usr/bin/env python
#
# Copyright (c) 2013 Antoine Musso
# Copyright (c) Wikimedia Foundation Inc.
#
# Licensed under the GPL Version 2.0
# See LICENSE for details.
#

import argparse
import ConfigParser
import logging
import os
import subprocess
import sys

default_conf_file = os.path.expanduser('~/.gerritclone.conf')
default_conf = {
    'base_path': '~/projects',
    'protocol': 'ssh',
    'user': None,
    'port': 29418,
    'path': '/',
    'remotename': 'origin',
}
logger = None


def main():
    options = parse_args()

    logging.basicConfig(level=options.log_level)
    logger = logging.getLogger(__name__)

    validate_options(options)

    my_config = confreader(options)
    my_config['base_path'] = os.path.expanduser(my_config['base_path'])
    logger.debug("Config: %s" % my_config)

    # Fetch URL parts. Note that defaults are handled by ConfigParser
    user_part = my_config.get('user')
    if user_part:
        user_part += '@'
    else:
        user_part = ''  # normalize None values

    port_part = my_config.get('port')
    if port_part:
        port_part = ':%s' % port_part

    # Normalize project and destination paths using conventions
    real_project = resolve_project(
        options.project,
        my_config.get('base_path'),
    )
    dest_path = resolve_dest(
        options.project,
        my_config.get('base_path'),
    )

    clone_url = (
        "{protocol}://{user_part}{hostname}{port_part}{path}{project}.git"
    ).format(
        protocol=my_config.get('protocol'),
        user_part=user_part,
        hostname=my_config.get('host'),
        port_part=port_part,
        path=my_config.get('path'),
        project=real_project.lstrip('/'),
    )

    cmd = ['git', 'clone', '-o', my_config.get('remotename'),
           clone_url, dest_path]
    if options.dry_run:
        print "Git command:\n%s" % ' '.join(cmd)
        sys.exit(0)

    logger.debug("Spawning: %s" % cmd)
    exit_code = subprocess.call(cmd)
    sys.exit(exit_code)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--conf', dest='conf', default=None,
        help='Configuration file. Will fallback to ~/.gerritclone if it exist')
    parser.add_argument(
        '-n', '--dry-run', dest='dry_run', action='store_true',
        help='Do not clone. Useful with --debug')
    parser.add_argument(
        'instance', nargs='?',
        help='A gerrit instance as defined in ~/.gerritclone.conf. Default '
             'to the first project found in the configuration file.'
    )
    parser.add_argument('project', help='Gerrit project name to clone')
    log_options = parser.add_mutually_exclusive_group()
    log_options.add_argument(
        '--debug', dest='log_level',
        action='store_const', const=logging.DEBUG,
        help='No output')
    log_options.add_argument(
        '-v', '--verbose', dest='log_level',
        action='store_const', const=logging.INFO,
        help='Print out internal processing')
    log_options.add_argument(
        '-q', '--quiet', dest='log_level',
        action='store_const', const=logging.WARNING,
        help='No output')

    return parser.parse_args()


def validate_options(options):
    # Validate options related to the configuration file
    if not options.conf and os.path.isfile(default_conf_file):
        options.conf = default_conf_file

    if options.conf and not os.path.isfile(options.conf):
        sys.exit("Configuration file not found: %s" % options.conf)

    if options.instance and not options.conf:
        sys.exit("Could not specify an instance without a configuration file")


def common_part(project, base_path):
    """ Find out where we are in basepath hierarchy"""
    logger = logging.getLogger(__name__)

    # Make us recognize '~' in base path
    base_path = os.path.expanduser(base_path)
    # Normalize Gerrit project to the OS:
    gerrit_path = os.sep.join(project.split('/'))
    cur_path = os.getcwd()

    logger.debug("PATHS:\nbase....: %s\ncur.....: %s\ngerrit..: %s" % (
        base_path, cur_path, gerrit_path))

    parts = cur_path.partition(base_path)

    logger.info("Common part is: %s" % parts[2])
    return parts[2]


def resolve_project(project, base_path):
    newproject = os.sep.join(
        (common_part(project, base_path), project)
    )
    return newproject


def resolve_dest(project, base_path):
    logger = logging.getLogger(__name__)

    common = common_part(project, base_path)
    dest_path = os.sep.join(
        (base_path, common, project)
    )

    # Normalize path name (like getting ride of dupes slashes)
    dest_path = os.path.normpath(dest_path)

    logger.info("Got destination path: %s" % dest_path)

    return dest_path


def confreader(options):
    logger = logging.getLogger(__name__)
    logger.debug("Proceeding configuration")

    config = ConfigParser.ConfigParser(default_conf)

    if not options.conf:
        logger.info('No configuration file, using build-in defaults')
        return dict(config.defaults())

    config.read(options.conf)

    if not options.instance:
        # Fallback to whatever first instance has been defined or give up
        try:
            options.instance = config.sections()[0]
            logger.info("Gerrit instance is %s" % options.instance)
        except IndexError:
            sys.exit('No Gerrit instance defined in %s.\nYou need at '
                     'least one.' % options.conf)

    # The requested instance really should be in the conf file
    if not config.has_section(options.instance):
        sys.exit('No Gerrit instance named "%s" in %s' %
                 (options.instance, options.conf))

    return dict(config.items(options.instance))

if __name__ == '__main__':
    main()
