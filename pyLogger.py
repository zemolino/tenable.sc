#-------------------------------------------------------------------------------
# Name:         pyLogger.py
# Purpose:      Configures logging for scripts to a log file
#               
#
#-------------------------------------------------------------------------------

# Requirements:
#
#    variable 'scriptname' comes from calling script
#    Must be defined in calling script as:
#       import os
#       scriptname = os.path.splitext(os.path.basename(__file__))[0]
#
#    Implement this logging script by adding the
#    following:
#        from pyLogging import Logger
#        loginstance = Logger(scriptname)
#        logger = loginstance.setup()

# Import logging and logging.handlers modules (embedded into Python)

import logging
import logging.handlers


class Logger(object):

    def __init__(self, path, filename):
        self._scriptloc = path
        self._scriptname = filename
        self._fh = None
        self._ch = None
        # Configure debug logging
        # create logger with '__main__'
        self._logger = logging.getLogger(filename)
        self._logger.setLevel(logging.DEBUG)

    def setup(self):
        # create rotating filehandler which logs messages to file
        self._fh = logging.handlers.RotatingFileHandler(
            self._scriptloc + self._scriptname + '.log', maxBytes=500000, backupCount=5)
        self._fh.setLevel(logging.DEBUG)
        # create console handler which sends log messages to console
        self._ch = logging.StreamHandler()
        self._ch.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self._fh.setFormatter(formatter)
        self._ch.setFormatter(formatter)
        # add the handlers to the logger
        self._logger.addHandler(self._fh)
        self._logger.addHandler(self._ch)
        return self._logger

    def closeHandlers(self):
        self._fh.close()
        self._ch.close()
    
    
