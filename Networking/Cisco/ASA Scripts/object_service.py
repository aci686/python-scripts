#!/usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

#
# Service Object Class
#
# Usage example:
#
# test = object_service("service tcp source eq 443")
# print(test)
#     object network tcp_eq_443
#      service tcp source eq 443
#
# test = object_service("service tcp destination eq 3389")
# print(test)
#     object network tcp_eq_3389
#      service tcp destination eq 3389
#
# test = object_service(service tcp source range 1024 65500 destination eq 80")
# print(test)
#     object network tcp_range_1024_65500_eq_80
#      service tcp source range 1024 65500 destination eq 80

class object_service:
    def __init__(self, line):
        self.source = ''
        self.destination = ''
        if line.split(' ')[0] != 'service':
            self.type = 'ERROR'
            self.name = line
        else:
            if line.split(' ')[1] in ['tcp', 'udp']: 
                self.type = line.split(' ')[1]
                if not 'source' in line and not 'destination' in line:
                    self.type = 'ERROR'
                    self.name = line
                else:
                    self.name = line.split(' ')[1]
                    if 'source' in line:
                        if 'destination' in line.split('source')[1]:
                            self.name = self.name + str(line.split('source')[1].split('destination')[0].rstrip().replace(' ', '_'))
                            self.source = str(line.split('source')[1].strip().split('destination')[0].strip())
                            self.destination = str(line.split('destination')[1].strip())
                        else:
                            self.name = self.name + str(line.split('source')[1].replace(' ', '_'))
                            self.source = str(line.split('source')[1].strip())
                    if 'destination' in line:
                        self.name = self.name + str(line.split('destination')[1].replace(' ', '_'))
                        self.destination = str(line.split('destination')[1].strip())
            else:
                self.type = 'ERROR'
                self.name = line

    def __str__(self):
        output = ''
        if self.type == 'ERROR':
            output = 'There was an error creating this object: ' + self.name
        else:
            if self.source and not self.destination:
                output = 'object network %s\n service %s source %s' % (self.name, self.type, self.source)
            elif self.source and self.destination:
                output = 'object network %s\n service %s source %s destination %s' % (self.name, self.type, self.source, self.destination)
            elif not self.source and self.destination:
                output = 'object network %s\n service %s destination %s' % (self.name, self.type, self.destination)
            else:
                output = 'object network %s' % (self.name)
        return output