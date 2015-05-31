
standardDisclaimer = "  Curb Samaritan is free service.  See http://curbsamaritan.com for more info."



def textResponse(cls, result, number):
    pass

confirmationMessage = """Please enter the follow cod Curb Samaritan to confirm your phone number: %(code)s.""" + standardDisclaimer

def textConfirmation(cls, number, code):
    return sendSMS(user.number, confirmationMessage % {
        number : number,
        code : code
        })

standardMessage = """A kind soul sends you a message through Curb Samaritan: %(message)s.""" + standardDisclaimer

def textMessage(cls, user, message):
    return sendSMS(user.number, standardMessage % {
        message : message,
        separator : ": " if message else "",
        salutation : user.nickname + ", " if user.nickname else ""
        })

thanksMessage = """A thank-you from %(nickname)s for your Curb Samaritan message of %(when)s: %(message)s.""" + standardDisclaimer

def textThanks(cls, user, call, caller, message):
    return sendSMS(caller.number, thanksMessage % {
        message : message if message else "Thanks a lot!",
        nickname : user.nickname if user.nickname else "the recipient",
        when : call.when
        })
    
