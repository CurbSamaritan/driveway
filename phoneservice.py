from twilio.rest import TwilioRestClient
import logging

account_sid = "AC888bdf652500c36645782e8e428d0d25"
auth_token = "460fdc16d01d9b8680cf0105b458c121"
twilio_number = "+1 415-951-3997"

#
# Q: Is it safe to keep the client in a global like this??
#
client = TwilioRestClient(account_sid, auth_token)

def send(target, message):
    logging.info("sending message {} to {}".format(message, target))
    client.messages.create(body = message, to = target, from_ = twilio_number )
    return 'success'

