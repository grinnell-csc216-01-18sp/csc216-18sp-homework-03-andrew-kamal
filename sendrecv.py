##
# CSC 216 (Spring 2018)
# Reliable Transport Protocols (Homework 3)
#
# Sender-receiver code for the RDP simulation program.  You should provide
# your implementation for the homework in this file.
#
# Your various Sender implementations should inherit from the BaseSender
# class which exposes the following important methods you should use in your
# implementations:
#
# - sender.send_to_network(seg): sends the given segment to network to be
#   delivered to the appropriate recipient.
# - sender.start_timer(interval): starts a timer that will fire once interval
#   steps have passed in the simulation.  When the timer expires, the sender's
#   on_interrupt() method is called (which should be overridden in subclasses
#   if timer functionality is desired)
#
# Your various Receiver implementations should also inherit from the
# BaseReceiver class which exposes thef ollowing important methouds you should
# use in your implementations:
#
# - sender.send_to_network(seg): sends the given segment to network to be
#   delivered to the appropriate recipient.
# - sender.send_to_app(msg): sends the given message to receiver's application
#   layer (such a message has successfully traveled from sender to receiver)
#
# Subclasses of both BaseSender and BaseReceiver must implement various methods.
# See the NaiveSender and NaiveReceiver implementations below for more details.
##

from sendrecvbase import BaseSender, BaseReceiver

import Queue

class Segment:
    def __init__(self, msg, dst):
        self.msg = msg
        self.dst = dst

class NaiveSender(BaseSender):
    def __init__(self, app_interval):
        super(NaiveSender, self).__init__(app_interval)

    def receive_from_app(self, msg):
        seg = Segment(msg, 'receiver')
        self.send_to_network(seg)

    def receive_from_network(self, seg):
        pass    # Nothing to do!

    def on_interrupt(self):
        pass    # Nothing to do!

class NaiveReceiver(BaseReceiver):
    def __init__(self):
        super(NaiveReceiver, self).__init__()

    def receive_from_client(self, seg):
        self.send_to_app(seg.msg)

class AltSender(BaseSender):
    def __init__(self, app_interval):
        super(AltSender, self).__init__(app_interval)
        self.segment = 0
        self.can_send = True
        self.last_msg = None
        self.timeout = 10

    def receive_from_app(self, msg):
        # get the hash of the message to be used for comparison for receiver
        if self.can_send:
            msg = {'segment':self.segment, 'message':msg, 'hash':hash(msg)}
            seg = Segment(msg, 'receiver')
            self.last_msg = seg
            self.send_to_network(seg)
            self.start_timer(self.timeout)
            # waiting for ACK
            self.can_send = False

    def receive_from_network(self, seg):
        if type(seg.msg) == dict and seg.msg['segment'] == self.segment \
                and hash(seg.msg['segment']) == seg.msg['hash']:
            self.segment = (self.segment + 1) % 2
            self.can_send = True
        else:
            self.send_to_network(self.last_msg)
            self.start_timer(self.timeout)

    def on_interrupt(self):
        self.send_to_network(self.last_msg)
        self.start_timer(self.timeout)


class AltReceiver(BaseReceiver):
    # TODO: fill me in!
    def __init__(self):
        super(AltReceiver, self).__init__()
        self.segment = 0

    def receive_from_client(self, seg):
        if type(seg.msg) == dict and seg.msg['segment'] == self.segment \
            and hash(seg.msg['message']) == seg.msg['hash']:
            # send an ACK TODO:
            self.send_to_app(seg.msg['message'])
            msg = {'segment': self.segment, 'hash': hash(self.segment)}
            self.segment = (self.segment + 1) % 2
            self.send_to_network(Segment(msg, 'sender'))
        else:
            # send NAK
            NAK_seg = 1 if self.segment else 0
            msg = {'segment': NAK_seg, 'hash': hash(NAK_seg)}
            self.send_to_network(Segment(msg, 'sender'))





class GBNSender(BaseSender):
    # TODO: fill me in!
    pass

class GBNReceiver(BaseReceiver):
    # TODO: fill me in!
    pass
