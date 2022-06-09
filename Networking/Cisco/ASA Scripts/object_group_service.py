#!/usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

import ipaddress, re
from object_service import object_service

#
# Service Group Object Class
#
# Usage example:
#

class object_group_service:
    def __init__(self, line):
        self.name = line
        self.service_objects = []

    def add_object_service(self, line):
        if isinstance(line, str):
            self.service_objects.append(object_service(line))
        elif isinstance(line, object_service):
            self.service_objects.append(line)

    def __str__(self):
        output = 'object-group service %s' % (self.name)
        if self.service_objects:
            for _ in self.service_objects:
                if _.type == 'ERROR':
                    output = 'There was an error creating this object: ' + self.name
                else:
                    output = output + '\n service-object object %s' % (_.name)
                                       
        return output

test_group = object_group_service('Test_Group')
test_group.add_object_service(object_service('service tcp destination eq 3389'))
print(test_group)
test_group.add_object_service('service tcp source eq 3389')
print(test_group)