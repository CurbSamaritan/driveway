from twilio.rest import TwilioRestClient
import logging
import appConfig


def send(target, message):
    import appConfig
    config = appConfig.get()
    client = TwilioRestClient(config['twilio']['account_sid'],
                              config['twilio']['auth_token'])
    logging.info("sending message {} to {}".format(message, target))
    client.messages.create(body=message, to=target, from_=config['twilio']['number'] )
    return 'success'

