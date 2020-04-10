#
# Copyright 2018 Joachim Lusiardi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging


def setup_logging(level):
    """
    Set up the logging to use a decent format and the log level given as parameter.
    :param level: the log level used for the root logger
    """
    logging.basicConfig(format='%(asctime)s %(filename)s:%(lineno)04d %(levelname)s %(message)s')
    if level:
        getattr(logging, level.upper())
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % level)
        logging.getLogger().setLevel(numeric_level)


def add_log_arguments(parser, level=None):
    """
    Adds command line arguments to control logging behaviour.

    :param parser: The argparse.ArgumentParser object to add to.
    :param level: the default log level if not given as command line parameter. defaults to None which means no logging
    """
    parser.add_argument('--log', action='store', dest='loglevel', default=level, help='Set the log level of the script',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
