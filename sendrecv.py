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
import collections

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
            self.end_timer()
        else:
            self.send_to_network(self.last_msg)
            self.start_timer(self.timeout)

    def on_interrupt(self):
        self.send_to_network(self.last_msg)
        self.start_timer(self.timeout)


class AltReceiver(BaseReceiver):
    def __init__(self):
        super(AltReceiver, self).__init__()
        self.segment = 0

    def receive_from_client(self, seg):
        if type(seg.msg) == dict and seg.msg['segment'] == self.segment \
            and hash(seg.msg['message']) == seg.msg['hash']:
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
    def __init__(self, app_interval):
        super(GBNSender, self).__init__(app_interval)
        self.segment     = 0
        self.window_size = 10
        self.last_msg    = collections.deque([], self.window_size)
        self.window_size = 10
        self.timeout     = 10

    def receive_from_app(self, msg):
        # get the hash of the message to be used for comparison for receiver
        if len(self.last_msg) < self.last_msg.maxlen:
            # only add message to the queue if there is space
            msg = {'segment':self.segment, 'message':msg, 'hash':hash(msg)}
            seg = Segment(msg, 'receiver')
            self.last_msg.append(seg)  # do not wait for packet if full
            self.send_to_network(seg)
            self.start_timer(self.timeout)
            # waiting for ACK

    def receive_from_network(self, seg):
        if type(seg.msg) == dict and seg.msg['segment'] >= self.segment \
                and hash(seg.msg['segment']) == seg.msg['hash']:
            self.segment = seg.msg['segment'] + 1
            try:
                # if we ACK the last item in the dequeue then we get an IndexError since the queue would be empty
                current_seg = self.last_msg.popleft()
                print current_seg.msg
                while current_seg.msg['segment'] < self.segment:
                    # pull stuff off queue if ACKed
                    current_seg = self.last_msg.popleft()
                self.last_msg.append(current_seg)
                # still waiting to get ACKs
                self.start_timer()
            except IndexError:
                # no more packets to wait on
                self.end_timer()
        else:
            # resend everything in the dequeue
            self.resend()

    def on_interrupt(self):
        self.resend()

    def resend(self):
        for seg in self.last_msg:
            # send every message back to receiver
            self.send_to_network(seg)
        self.start_timer(self.timeout)



class GBNReceiver(BaseReceiver):
    # TODO: fill me in!
    def __init__(self):
        super(GBNReceiver, self).__init__()
        self.segment = 0 # note this is an int that can be greater than 1

    def receive_from_client(self, seg):
        if type(seg.msg) == dict and seg.msg['segment'] == self.segment \
            and hash(seg.msg['message']) == seg.msg['hash']:
            # send an ACK:
            self.send_to_app(seg.msg['message'])
            msg = {'segment': self.segment, 'hash': hash(self.segment)}
            self.segment += 1
            self.send_to_network(Segment(msg, 'sender'))
        else:
            # NAK case
            msg = {'segment': self.segment - 1, 'hash': hash(self.segment - 1)}
            self.send_to_network(Segment(msg, 'sender'))
