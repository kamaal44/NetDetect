from . import config
from .logger import set_logger
from ..utils import shaping_utils
import numpy as np


def load(test_size):
  '''
  Loads preprocessed data dump if possible.
  '''
  try:
    with open(config.DUMPS_DIR + config.PROCESSED_TEST_NAME + "_features",
              'rb') as f_x:
      full_test_X = np.load(f_x)
    with open(config.DUMPS_DIR + config.PROCESSED_TEST_NAME + "_labels",
              'rb') as f_y:
      full_test_Y = np.load(f_y)
    full_test_X, full_test_Y = shaping_utils.shuffle_twins(full_test_X, full_test_Y)
    test_X = full_test_X[:test_size]
    del(full_test_X)
    test_Y = full_test_Y[:test_size]
    del(full_test_Y)

    with open(config.DUMPS_DIR + config.PROCESSED_TRAIN_NAME + "_features",
              'rb') as f_x:
      train_X = np.load(f_x)
    with open(config.DUMPS_DIR + config.PROCESSED_TRAIN_NAME + "_labels",
              'rb') as f_y:
      train_Y = np.load(f_y)
    train_X, train_Y = shaping_utils.shuffle_twins(train_X, train_Y)

    set_logger.info("Dataset exists. Processing...")
    return (train_X, train_Y), (test_X, test_Y)

  except (EOFError, OSError, IOError) as e:
    set_logger.info("Dataset does not exist. Returning None.")
    return None

