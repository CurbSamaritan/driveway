from phoneservice import send
import appConfig



def getProject():
  return appConfig.get()["public"]["project"]

def getStandardDisclaimer():
    return "  Curb Samaritan is free service.  See %(url)s for more info." % getProject()


def textResponse(cls, result, number):
    pass

confirmationMessage = """Enter this code on Curb Samaritan: %(code)s.""" + getStandardDisclaimer()

def textConfirmation(number, code):
    return send(number, confirmationMessage % {
        'number' : number,
        'code' : code
        })

standardMessage = """A kind soul sends you a message through Curb Samaritan: %(message)s.""" + getStandardDisclaimer()

def textMessage(user, message):
    return send(user.number, standardMessage % {
        'message' : message,
        'separator' : ": " if message else "",
        'salutation' : user.nickname + ", " if user.nickname else ""
        })

thanksMessage = """A thank-you from %(nickname)s for your Curb Samaritan message of %(when)s: %(message)s.""" + getStandardDisclaimer()

def textThanks(user, call, caller, message):
    return send(caller.number, thanksMessage % {
        'message' : message if message else "Thanks a lot!",
        'nickname' : user.nickname if user.nickname else "the recipient",
        'when' : call.when
        })
    
