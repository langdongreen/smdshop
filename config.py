DEBUG = True

URL = 'http://localhost:5000'

MAIL_SERVER = "secure.pigeonpost.com.au"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_DEBUG = False
MAIL_USERNAME = 'lg@idealcs.com.au'
MAIL_PASSWORD = 'h289andd'
WTF_CSRF_ENABLED = True
SECRET_KEY = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

ADMIN = "lg@langdongreen.com"
ORDER_EMAIL = "lgreen@microengines.com.au"
SKYPE = "microengines"

VALIDATION_FAIL = 'All fields are required.'
EMPTY_CART = 'No products in shopping cart'
LINE_NOT_FOUND = 'Cannot find item in shopping cart'
ORDER_ERROR = 'Please Check your order and address and try again'
RETURN_ERROR = 'There was a problem returning from Paypal, the problem has been logged'
LOG_SUCCESS =  'Success'
LOG_ERROR = 'Incomplete'
SUCCESSFUL_ORDER = 'Your order has been completed successfully'

#BANNER = '<img src="'+URL+'/static/web_banner_metal.png" alt="MicroEngines">'
BANNER="MicroEngines"
HOME = "Home"
TERMS = "<p>I am careful with assembly and inspect every job before sending.  If the part is faulty please contact me within 30 days and I will\
        either refund or repair.  After 30 days still contact me and I will see what I can do</p><p>I cannot be responsible if the part is used in a way its not meant to (for eg. connected incorrectly)  I can only\
        cover soldering/PCB faults.<p>If you need large orders <a href=\""+ORDER_EMAIL+"\">contact</a> me and I will arrange a quote and lead time.</p>"
SHIPPING = "<p>Products will be shipped using Australia Post the shipping cost will be displayed\
            in the checkout process, in some cases it will be free</p><p>Products can be shipped standard or express and are usually sent the next day\
            after ordering to give time for parts to arrive and assembly/testing.</p>"
ABOUT = "About"

