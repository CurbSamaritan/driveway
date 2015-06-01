import random
import datetime
import re

from google.appengine.ext import ndb

import SMS

def enum(**enums):
    return type('Enum', (), enums)

def first(l, f):
    for d in l:
        if f(d):
            return d
    return None

codeChars = '23456789ABCDEFGHJKMNPQRSTUVWXYZ'


def fetchFirst(q):
    iterQ = q.iter()
    return iterQ.next() if iterQ.has_next() else None


def listAsData(l):
    return [ d.asData() for d in l ]


class CodeProperty(ndb.StringProperty):
    @classmethod
    def concoctCode(cls, n):
        return "".join([ random.choice(codeChars) for i in range(n) ])

    def _validate(self, value):
      if value == '':
        return CodeProperty.concoctCode(6)


class User(ndb.Model):
    code = CodeProperty(default='')
    social_network = ndb.StringProperty()
    social_id = ndb.StringProperty()
    nickname = ndb.StringProperty()
    number = ndb.StringProperty()
    suspended = ndb.StringProperty(default='')


    @classmethod
    def register(cls, social_network, social_id, nickname):
        u = User(social_network=social_network, social_id=social_id, nickname=nickname)
        u.put()
        return u

    @classmethod
    def find(cls, idn):
        return ndb.Key('User', int(idn)).get()

    
    @classmethod
    def findBySocialID(cls, social_network, social_id):
        return fetchFirst(User.query(User.social_network == social_network, User.social_id == social_id))

    @classmethod
    def findByCode(cls, code):
        return fetchFirst(User.query(User.code == code))

    def update(self, form):
        if "nickname" in form:
            self.nickname = form["nickname"]
        self.put()
        return form

    def sendNumber(self, number):
        contact = Contact(user=self.key, number=number)
        contact.put()
        SMS.textConfirmation(number, contact.code)
        return contact

    def _getMine(self, cls):
        return cls.query(cls.user == self.key).fetch()
    
    def fetchCallers(self):
        return self._getMine(Caller)

    def fetchCalls(self):
        return self._getMine(Call)

    def fetchContacts(self):
        return self._getMine(Contact)

    def fetchPendingContacts(self):
        return filter(lambda contact: contact.isPending(),
                      self.fetchContacts())
    
    def confirmCode(self, code):
        contacts = self.fetchContacts()
        confirmed = first(contacts, 
                          lambda contact: contact.code == code and contact.isPending())
        if confirmed:
            self.number = confirmed.number
            self.put()
            for contact in contacts:
                print contact.number, contact.status
                if contact.status == 'active':
                    contact.status = 'former'
                    contact.put()
                elif contact.status == 'pending':
                    contact.status = 'active' if contact == confirmed else 'expired'
                    contact.put()
        return confirmed

    def hasPendingContacts(self):
        return len(self.fetchPendingContacts()) > 0


class Caller(ndb.Model):
    user = ndb.KeyProperty(kind=User, required=True)
    number = ndb.StringProperty(required=True)
    nickname = ndb.StringProperty(indexed=False)
    blocked = ndb.StringProperty()

    @classmethod
    def find(cls, idn):
        return ndb.Key('Caller', int(idn)).get()

    def update(self, form):
        if "nickname" in form:
            self.nickname = form["nickname"]
        self.put()
        return form

    def block(self, block):
        if not self.blocked:
            self.blocked = block
            self.put()
            return 'success'
        else:
            return 'invalid'

    @classmethod
    def findCaller(cls, u, number):
        caller = fetchFirst(Caller.query(Caller.user == u.key, Caller.number == number))
        if not caller:
            caller = Caller(user=u.key, number=number)
            caller.put()
        return caller

class Call(ndb.Model):
    user = ndb.KeyProperty(kind=User, required=True)
    caller = ndb.KeyProperty(kind=Caller, required=True)
    message = ndb.StringProperty(indexed=False, required=True)
    ctype = ndb.StringProperty(required=True)
    when = ndb.DateTimeProperty(auto_now_add=True)
    thanked = ndb.KeyProperty(kind='Call', default=None, indexed=False)
    reported = ndb.StringProperty(default='', indexed=False)

    callResults = enum(BAD_FORMAT='bad format', NO_USER='no user', 
                       TRY_AGAIN='try again', USER_SUSPENDED='user suspended', CALLER_BLOCKED='caller blocked')

    callRe = re.compile('[ \t]*([' + codeChars + ']+)[ \t]*(.*)')

    @classmethod
    def find(cls, idn):
        return ndb.Key('Call', int(idn)).get()

        
    @classmethod
    def callReceived(cls, number, text):
        m = cls.callRe.match(text)
        if not m:
            return Call.callResults.BAD_FORMAT
        code, message = m.groups()
        u = User.findByCode(code)
        if not u:
            return Call.callResults.NO_USER
        if u.suspended:
            return Call.callResults.USER_SUSPENDED
        caller = Caller.findCaller(u, number)
        if caller.blocked:
            return Call.callResults.CALLER_BLOCKED
        call = Call(user=u.key, caller=caller.key, message=message, ctype='incoming')
        call.put()
        call.result = SMS.textMessage(u, message)
        if call.result == 'success':
            return call
        else:
            return Call.callResults.TRY_AGAIN
        

    def thank(self, message):
        user = self.user.get()
        caller = self.caller.get()
        if self.ctype == 'incoming' and not self.thanked:
            result = SMS.textThanks(user, self, caller, message)
            if result == 'success':
                call = Call(user=user.key, caller=caller.key, message=message, ctype='thank')
                call.put()
                self.thanked = call.key
                self.put()
                return call
            else:
                return result
        else:
            return 'invalid'

    def report(self, reason):
        if self.reported:
            return 'duplicate'
        else:
            self.reported = reason
            self.put()
            return { "value": reason }




    
class Contact(ndb.Model):
    user = ndb.KeyProperty(kind=User)
    number = ndb.StringProperty()
    status = ndb.StringProperty(default='pending')
    created = ndb.DateTimeProperty(auto_now_add=True)
    code = CodeProperty(default='')

    def isPending(self):
        print (self.status == 'pending' )
        print (datetime.datetime.now() - self.created).days 

        return (self.status == 'pending' and
                (datetime.datetime.now() - self.created).days == 0)

