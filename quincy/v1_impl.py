# Copyright (c) 2014 Dark Secret Software Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import random
import uuid


class Stream(object):
    def __init__(self, stream_id, trigger_name, state, last, start, fire,
                 expiry):
        self.last = last
        self.start = start
        self.fire = fire
        self.expiry = expiry
        self.stream_id = stream_id
        self.trigger_name = trigger_name
        self.state = state

    def to_dict(self):
        # Valid states ...
        # active = 1
        # firing = 2
        # expiring = 3
        # error = 4
        # expire_error = 5
        # completed = 6
        # retry_fire = 7
        # retry_expire = 8
        expire_timestamp = None
        if self.expiry:
            expire_timestamp = {
                "__type__": "datetime", "datetime": str(self.expiry)
            }
        fire_timestamp = None
        if self.fire:
            fire_timestamp = {
                "__type__": "datetime", "datetime": str(self.expiry)
            }
        begin = datetime.datetime.combine(self.start.date(), datetime.time.min)
        end = begin + datetime.timedelta(days=1)
        return {
            "distinguishing_traits": {
                "instance_id": str(uuid.uuid4()),
                "timestamp": {
                    "__type__": "timex.TimeRange",
                    "begin": str(begin),
                    "end": str(end)
                }
            },
            "expire_timestamp": expire_timestamp,
            "fire_timestamp": fire_timestamp,
            "first_event": {
                "__type__": "datetime",
                "datetime": str(self.start)
            },
            "id": self.stream_id,
            "last_event": {
                "__type__": "datetime",
                "datetime": str(self.last)
            },
            "name": self.trigger_name,
            "state": self.state
        }


class Impl(object):
    def __init__(self, config, scratchpad):
        self.config = config
        self.scratchpad = scratchpad
        self.streams = None

    def _make_streams(self):
        if self.streams:
            return self.streams

        states = ["active", "firing", "expiring", "error", "expire_error",
                  "completed", "retry_fire", "retry_expire"]
        pipeline_names = ['usage', 'performance', 'reporting', 'fraud']
        now = datetime.datetime.utcnow()

        # Make streams over the last 48 hours (+/- max_duration_minutes)
        minutes_in_48_hrs = 60 * 48
        max_duration_minutes = 60 * 2
        self.streams = []
        for stream_id in range(100):
            state = random.choice(states)
            name = random.choice(pipeline_names)

            last_minutes = random.randrange(minutes_in_48_hrs)
            duration = random.randrange(max_duration_minutes)
            last = now - datetime.timedelta(minutes=-last_minutes)
            start = last - datetime.timedelta(minutes=-duration)
            fire = None
            expiry = None
            if state != 'completed':
                finish = start + datetime.timedelta(
                                        minutes=max_duration_minutes)
                if random.randrange(2) == 0:
                    expiry = finish
                else:
                    fire = finish

            self.streams.append(Stream(stream_id + 100, name, state,
                                       last, start, fire, expiry))

        return self.streams

    def get_streams(self, **kwargs):
        """kwargs may be:
            count: True/False
            older_than
            younger_than
            state
            trigger_name
            distinguishing_traits
        """
        streams = self._make_streams()
        if kwargs.get('count', False):
            return [{"count": len(streams)}]

        return [stream.to_dict() for stream in streams]

    def get_stream(self, stream_id, details):
        return [self._make_streams()[0].to_dict()]

    def delete_stream(self, stream_id):
        pass

    def reset_stream(self, stream_id):
        pass
