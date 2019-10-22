import logging

def formatter(logfmt = '%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt = '%d.%m.%y %I:%M:%S %p'):
    return logging.Formatter(fmt=logfmt, datefmt=datefmt)

def setupLogging(
        name,
        loglvl = logging.DEBUG,
        logfile = None,
        logfmt = '%(asctime)s %(name)s %(levelname)s: %(message)s',
        datefmt = '%d.%m.%yT%I:%M:%S %p',
    ):

    rootLogger = logging.getLogger()
    rootLogger.setLevel(loglvl)
    
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter(logfmt, datefmt))

    rootLogger.addHandler(streamHandler)

    if logfile is not None:
        handler = logging.FileHandler(logfile)
        handler.setFormatter(formatter(logfmt, datefmt))
        rootLogger.addHandler(handler)
    return rootLogger

ROOT_LOGGER = setupLogging('habitat')
BASE_LOGGER = ROOT_LOGGER.getChild('habitat')

def get_logger(root, name):
    if not '.' in name:
        return root.getChild(name)
    lvl = name.split('.')
    return get_logger(root.getChild(lvl.pop(0)), '.'.join(lvl))

def Log(name):
    return get_logger(BASE_LOGGER, name)
