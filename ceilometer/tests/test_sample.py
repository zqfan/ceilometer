# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Tests for ceilometer/sample.py"""

import datetime
import uuid

from ceilometer import sample
from ceilometer.tests import base


class TestSample(base.BaseTestCase):
    SAMPLE = sample.Sample(
        name='cpu',
        type=sample.TYPE_CUMULATIVE,
        unit='ns',
        volume='1',
        user_id=uuid.uuid4().hex,
        project_id=uuid.uuid4().hex,
        resource_id=str(uuid.uuid4()),
        timestamp=datetime.datetime.utcnow(),
        resource_metadata={}
    )

    def test_sample_string_format(self):
        self.assertEqual(str(self.SAMPLE.as_dict()), str(self.SAMPLE))
        self.assertNotIn("ceilometer.sample.Sample object at 0x",
                         str(self.SAMPLE))
