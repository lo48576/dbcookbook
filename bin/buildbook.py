#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import sys
import os

import argparse
import logging
import inspect
from functools import wraps


__author__ = "Thomas Schraitle"
__version__ = "0.5"
__docformat__ = "epytext"


BINDIR=os.path.dirname(os.path.abspath(__file__))
CONFIGFILE=".dbcookbook.ini"
LOGFILE='/var/tmp/%s.log' % os.path.splitext(os.path.basename(__file__))[0]
ENABLE_TRACE=True
MAINFILE="en/xml/DocBook-Cookbook.xml"



# Need to be global to make use of it in trace decorator
logger = logging.getLogger(os.path.basename(__file__))


class trace(object):
    '''Logging decorator that allows you to log with a specific logger.
    
    To be used as:
    
    @trace(logger)
    def test_logger(a, b=5, c=10, x=None):
        pass
    '''    
    
    # Customize these messages
    ENTRY_MESSAGE = '[ Entering {}{sig} called with args={args}, kwargs={kwargs} ]'
    EXIT_MESSAGE =  '[ Exiting  {}() ]'

    def __init__(self, logger=None):
        self.logger = logger

    def __call__(self, func, enable=True):
        '''Returns a wrapper that wraps func.
        The wrapper will log the entry and exit points of the function
        with logging.INFO level.
        '''
        # set logger if it was not set earlier
        if not self.logger:
            logging.basicConfig()
            self.logger = logging.getLogger(func.__module__)
            
        if not enable:
            return func

        @wraps(func)
        def logwrap(*args, **kwargs):
            sig=inspect.signature(func)
            
            self.logger.debug(self.ENTRY_MESSAGE.format(func.__name__, sig=str(sig), args=str(args), kwargs=kwargs))
            # self.logger.debug("  Full spec:{}".format(inspect.getfullargspec(func)))
            
            f_result = func(*args, **kwargs)
            
            self.logger.debug(self.EXIT_MESSAGE.format(func.__name__))
            return f_result
        return logwrap


def parsecommandline():
    """Parses commandline and returns parser and parsed arguments
    
    @return: parser object
    """
    import argparse
    parser = argparse.ArgumentParser(
        description='Transforms an AsciiDoc file into a target format',
    )

    parser.add_argument('--version',
        action='version',
        version='%(prog)s v{0}'.format(__version__)
        )
    parser.add_argument('-v', '--verbose',
        action='count',
        default=0,
        help="Increase verbosity level (default: %(default)i)",
        )
    parser.add_argument('-L', '--log-file',
        help="Write logging information into LOGFILE (default: '%(default)s')",
        metavar="LOGFILE",
        default=LOGFILE,
        nargs='?',
        )
    parser.add_argument('-r', '--rootid',
        help="Formats only the element that contains an "
             "attribute with xml:id='$ROOTID' (default: %(default)s)",
        # type=str,
        nargs='?',
        )
    parser.add_argument('--cleanup',
        help="Only perform cleanup step (default: %(default)s)",
        action='store_true',
        default=False,
        )
    parser.add_argument('-I', '--init',
        help="Remove any old build directory before starting (default: %(default)s)",
        action='store_true',
        default=False,
        )
    parser.add_argument('-E', '--no-example',
        help="Do NOT generate examples automatically (default: %(default)s)",
        action='store_true',
        default=False,
        )
    parser.add_argument('-c', '--no-category',
        help="Do NOT generate other categories automatically (default: %(default)s)",
        action='store_true',
        default=False,
        )
    parser.add_argument('mainfile',
        help="Use main XML file  (default: %(default)s)",
        default=MAINFILE,
        nargs='?',
        )
    # Should go away as soon as the script is stable
    parser.add_argument('--test',
        help="Just for testing",
        action='store_true',
        default=False,
        )
    
    return parser, parser.parse_args()

def createlogger(level):
    maptable = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
        }
    # Map the verbose level from argparse to log level:
    loglevel=maptable.get(level, logging.NOTSET)
    
    logger.setLevel(loglevel)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(LOGFILE)
    fh.setLevel(logging.DEBUG)
    
    # create console handler with our log level from verbose option
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)
    
    # create formatter and add it to the handlers
    formatter = logging.Formatter('{asctime} - {levelname:8s} - {funcName} {message}', style='{')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)


def main():
    parser, args=parsecommandline()
    createlogger(args.verbose)
    return parser, args


def internaltest():
    @trace(logger)
    def test_logger(a, b=5, c=10, x=None):
        pass
    logger.warn("Oha! This is %(file)s", dict(file=__file__, bindir=BINDIR))

    logger.debug('logfile=%(logfile)s', dict(logfile=LOGFILE))
    logger.debug('debug message')
    logger.info('info message')
    logger.warn('warn message')
    logger.error('error message')
    logger.critical('critical message')
    test_logger(55)
    logger.debug("-------")
    test_logger(x=100, a=10)
    
    logger.debug("Testing if MAINFILE({main}) exists={result}".format(
        main=MAINFILE,
        result=os.path.exists(MAINFILE),
        ))

def __test():
    import doctest
    doctest.testmod()

    
if __name__=="__main__":
        
    parser, args = main()
    
    logger.debug("CLI arguments: {args}".format(args=args))
    
    if args.test:
        internaltest()

# EOF