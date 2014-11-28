"""Log important events appropriately from anywhere in Arcyd."""
# =============================================================================
# CONTENTS
# -----------------------------------------------------------------------------
# abdt_logging
#
# Public Functions:
#   set_external_system_error_logger
#   clear_external_system_error_logger
#   set_io_log_path
#   on_system_error
#   on_retry_exception
#   on_io_event
#
# -----------------------------------------------------------------------------
# (this contents block is generated, edits will be lost)
# =============================================================================

from __future__ import absolute_import

import datetime
import logging
import os
import threading

import phlsys_subprocess


_LOGGER = logging.getLogger(__name__)
_EXTERNAL_SYSTEM_ERROR_LOGGER = None
_IO_LOG_LOCK = threading.Lock()
_IO_LOG_PATH = None


def set_external_system_error_logger(logger):
    assert logger
    global _EXTERNAL_SYSTEM_ERROR_LOGGER
    _EXTERNAL_SYSTEM_ERROR_LOGGER = logger


def clear_external_system_error_logger():
    global _EXTERNAL_SYSTEM_ERROR_LOGGER
    _EXTERNAL_SYSTEM_ERROR_LOGGER = None


def set_io_log_path(path):
    assert path
    global _IO_LOG_PATH
    with _IO_LOG_LOCK:
        _IO_LOG_PATH = os.path.abspath(path)


def on_system_error(identifier, detail):
    if _EXTERNAL_SYSTEM_ERROR_LOGGER:

        #  It's easily possible for 'detail' to exceed the length of
        #  command-line parameters allowed when calling out to a registered
        #  external system error logger.
        #
        #  Limit the amount of detail that will be sent to an arbitrary
        #  small number to prevent errors when reporting errors.
        #
        detail = detail[:160]

        phlsys_subprocess.run(
            _EXTERNAL_SYSTEM_ERROR_LOGGER,
            identifier,
            detail)


def _log_system_exception(identifier, detail, exception):
    message = detail + '\n' + repr(exception)
    on_system_error(identifier, message)


def on_retry_exception(identifier, detail, e, delay):

    if delay is not None:
        _LOGGER.warning(
            'on_retry_exception: during "{}" encountered exception "{}", '
            'will retry in {}. More detail: "{}".'.format(
                identifier, type(e).__name__, delay, detail),
            exc_info=1)
    else:
        _LOGGER.error(
            'on_retry_exception: during "{}" encountered exception "{}", '
            'will not retry. More detail: "{}".'.format(
                identifier, type(e).__name__, detail),
            exc_info=1)

    _log_system_exception(identifier, detail, e)


def on_io_event(identifier, detail):
    with _IO_LOG_LOCK:
        if _IO_LOG_PATH:
            with open(_IO_LOG_PATH, 'a') as f:
                now = str(datetime.datetime.utcnow())
                description = '{}: {} - {}\n'.format(now, identifier, detail)
                f.write(description)


# -----------------------------------------------------------------------------
# Copyright (C) 2013-2014 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
