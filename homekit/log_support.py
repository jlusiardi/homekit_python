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


def add_log_arguments(parser):
    parser.add_argument('--log', action='store', dest='loglevel')
