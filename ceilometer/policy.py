# -*- encoding: utf-8 -*-
#
# Copyright © 2014 Huawei Technologies Co., Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Policy engine for Ceilometer."""

import os
from oslo.config import cfg

from ceilometer.openstack.common import log
from ceilometer.openstack.common import policy


CONF = cfg.CONF
LOG = log.getLogger(__name__)


_ENFORCER = None
_POLICY_PATH = None
_POLICY_CACHE = {}


def reset():
    global _POLICY_PATH
    global _POLICY_CACHE
    global _ENFORCER
    _POLICY_PATH = None
    _POLICY_CACHE = {}
    _ENFORCER = None


def read_cached_file(filename, cache_info, reload_func=None):
    """Read from a file if it has been modified.

    :param cache_info: dictionary to hold opaque cache.
    :param reload_func: optional function to be called with data when
    file is reloaded due to a modification.
    :returns: data from file

    """
    mtime = os.path.getmtime(filename)
    if not cache_info or mtime != cache_info.get('mtime'):
        with open(filename) as fap:
            cache_info['data'] = fap.read()
        cache_info['mtime'] = mtime
        if reload_func:
            reload_func(cache_info['data'])
    return cache_info['data']

def init():
    global _POLICY_PATH
    global _POLICY_CACHE
    global _ENFORCER
    if not _POLICY_PATH:
        _POLICY_PATH = CONF.policy_file
        if not os.path.exists(_POLICY_PATH):
            _POLICY_PATH = CONF.find_file(_POLICY_PATH)
    if not _ENFORCER:
        _ENFORCER = policy.Enforcer(policy_file=_POLICY_PATH)
    read_cached_file(_POLICY_PATH,
                     _POLICY_CACHE,
                     reload_func=_set_rules)


def _set_rules(data):
    global _ENFORCER
    default_rule = CONF.policy_default_rule
    _ENFORCER.set_rules(policy.Rules.load_json(
        data, default_rule))


def enforce(action, target, credentials, do_raise=True, **kwargs):
    """Verifies that the action is valid on the target in this context.

       :param credentials: user credentials
       :param action: string representing the action to be checked, which
                      should be colon separated for clarity.
       :param target: dictionary representing the object of the action
                      for object creation this should be a dictionary
                      representing the location of the object e.g.
                      {'project_id': object.project_id}
       :raises: kwargs['exc'] or PolicyNotAuthorized if verification fails.

       Actions should be colon separated for clarity. For example:

        * telemetry:list_alarms

    """
    init( )

    if do_raise:
        kwargs.update({'do_raise': True})

    return _ENFORCER.enforce(action, target, credentials, **kwargs)
