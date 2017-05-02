from flask_wtf import Form
from wtforms import StringField, BooleanField, SelectField, IntegerField, SubmitField,TextAreaField, validators
from wtforms.validators import DataRequired, Email,Required
import products

class CustomiseForm(Form):
    productid = StringField('productid')
    search = SubmitField('Search')

    adapters = [(None,'')]
    for p in products.product_list:
        if p > 0:
            description = products.product_list[p][0] + '-' + products.product_list[p][1]
            adapters.append((p,description))
    
    adapter_type = SelectField("Adapter", choices = adapters)

    assemble = BooleanField('Assemble')
    qty = SelectField('Qty', choices=[(i,i) for i in range(1,10)])
    add = SubmitField('Add To Cart')
    total = SubmitField('Get Total')

class AddressForm(Form):
    firstname = StringField('firstName',[validators.Required("Please enter your first name")])
    surname = StringField('surname',[validators.Required("Please enter your surname")])
    company = StringField('company')
    address1 = StringField('address1',[validators.Required("Please enter your street")])
    address2 = StringField('address2')
    suburb = StringField('suburb',[validators.Required("Please enter your suburb")])
    state = StringField('state',[validators.Required("Please enter your state")])
    postcode = StringField('postcode',[validators.Required("Please enter your postcode")])
    country = StringField('country')
    email = StringField('email',[validators.Required("Please enter an email address"), validators.Email("Valid email address required")])
    phone = StringField('phone')
    pay = SubmitField('Payment')
    
class ContactForm(Form):
    name = StringField('name',[validators.Required("Please enter your name")])
    email = StringField('email',[validators.Required("Please enter an email address"), validators.Email("Valid email address required")])
    message = TextAreaField('message',[validators.Required("Please enter a message")])
    send = SubmitField('Send')
    
    
