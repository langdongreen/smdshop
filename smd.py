from flask import Flask, render_template, url_for, session, redirect, request,flash
from werkzeug.datastructures import ImmutableOrderedMultiDict
from MySQLdb import escape_string as escape
from datetime import datetime
import xml.etree.ElementTree
import urllib2
import requests
from forms import CustomiseForm, AddressForm, ContactForm
import time
from flask_mail import Mail, Message
import products
from config import ADMIN, SKYPE, ORDER_EMAIL
from config import VALIDATION_FAIL, EMPTY_CART, LINE_NOT_FOUND, ORDER_ERROR, RETURN_ERROR
from config import LOG_SUCCESS, LOG_ERROR, SUCCESSFUL_ORDER
from config import HOME, BANNER, ABOUT, TERMS, SHIPPING
from config import API_BASE, API_KEY

app = Flask(__name__)

app.config.from_object('config')
mail = Mail(app)

@app.route('/<string:page_name>/')
def static_page(page_name):
    '''Render static pages from template.'''
    
    return render_template('%s.html' % page_name)
    
@app.route('/')
def index():    
     '''Render index template with banner, cart and contact details.'''   

     return render_template('index.html', banner = BANNER, lines = get_lines(),contact=get_contact())
    
@app.route('/order',methods=["GET","POST"])
def order():
    '''Render order template displaying order form and process submitted form data'''
    
    search_term =''
    product = None 
    customiseForm = CustomiseForm()
    total = 0
    #cartForm = CartForm(csrf_enabled=False)

    #
    #If search form has been submitted, find product using API
    #
    if customiseForm.search.data and customiseForm.is_submitted():
        search_term = customiseForm.productid.data
  
        if search_term != '':
            product = get_e14(search_term)
            
            if product:
                session['ordering_service'] = product          
        
    #If add or total has been clicked, handle order
    elif (customiseForm.add.data or customiseForm.total.data) and customiseForm.is_submitted():
        cart_line = []
        
        #Clean and verify input and set default values
        try:
            adapter_type = int(customiseForm.adapter_type.data)
        except ValueError:
            adapter_type = 0
            
        try:
            assemble = customiseForm.assemble.data
        except:
            assemble = 0
            
        try:
            qty = int(customiseForm.qty.data)
        except:
            qty = 1
            
        #calculate total and display total   
        if customiseForm.total.data:
            if adapter_type:
                total += products.product_list[adapter_type][3] #product price
            if assemble and adapter_type: 
                total += products.product_list[adapter_type][4] #assembly price
            if session.get('ordering_service'):
                total += session['ordering_service']['cost'] * products.ordering_service #chip to solder
            total *= qty
            
            session['subtotal'] = total
            
        #Add to cart clicked, add line to cart
        elif customiseForm.add.data:
            if adapter_type:
                line = {'type': adapter_type,'label': products.product_list[adapter_type][0],'qty': qty,'price': products.product_list[adapter_type][3] * qty}
                #line = [adapter_type, products.product_list[adapter_type][0], qty,products.product_list[adapter_type][3] * qty]
                add_to_cart(line)
            if assemble:
                line = {'type': -1, 'label': products.product_list[-1][0], 'qty': qty, 'price': products.product_list[adapter_type][4] * assemble * qty}
                add_to_cart(line)
            if session.get('ordering_service'):
                line = {'type': session['ordering_service']['e14id'], 'label': session['ordering_service']['name'], 'qty': qty, 'price': session['ordering_service']['cost']* products.ordering_service}
                add_to_cart(line)   

        

    return render_template('order.html',  banner = BANNER, product = product ,customiseForm = customiseForm, lines = get_lines(), product_list = products.product_list, total = total, contact=get_contact())
    
@app.route('/about')
def about():
    '''Render index template with banner, cart contact details and ABOUT text.'''  
    
    text = ABOUT
    return render_template('about.html', banner = BANNER, contact=get_contact(), lines = get_lines(), text = text)

    
@app.route('/contact', methods=["GET","POST"])
def contact():
    '''Render contact template with contact form and process submitted form data.'''  
    contactForm = ContactForm(csrf_enabled=False)
    
    #if contact form submitted
    if contactForm.send.data:
        #Clean and verify input
        if contactForm.validate() == False:
            flash(VALIDATION_FAIL)
            return render_template('contact.html', contactForm = contactForm, lines = get_lines())
        else:
            try:
                name = contactForm.name.data
            except:
                name = ''
                
            try:
                sender = contactForm.email.data
            except:
                sender = ''
                
            try:
                message = contactForm.message.data
            except:
                message = ''
            
            send_email("Contact "+name,sender,[ADMIN],message,'')
            
    return render_template('contact.html', banner = BANNER, contact=get_contact(), contactForm = contactForm, lines = get_lines(), referrer = request.referrer)

@app.route('/cart')
def cart():
    '''Render cart template to display shopping cart.'''  
    cart = get_cart()
    total = get_total()
    
    #If cart is empty, redirect to contact
    if not cart:
        flash(EMPTY_CART)
        return redirect(url_for('error'))

    return render_template('cart.html', banner = BANNER, contact=get_contact(), lines = get_lines(), cart = cart, total = total, shipping = get_shipping())
    
@app.route('/empty')
def empty():
    '''Empty shopping cart list and redirect to order page.'''  
    empty_cart()
    return redirect(url_for('order'))
    
@app.route('/cart/delete/<int:row_id>')
def remove_row(row_id):
    '''Remove one row of shopping cart list.'''  
    cart = get_cart()
    
    if cart and row_id < len(cart):
        del cart[row_id]
        session['cart'] = cart
    else:
        flash(LINE_NOT_FOUND)
        return redirect(url_for('error'))
    
    return redirect(url_for('cart'))
    
@app.route('/checkout', methods=["GET","POST"])
def checkout():
    '''Render checkout template and display cart and address forms.  Deal with submitted data.'''  
    addressForm = AddressForm(csrf_enabled=False)
    cart = get_cart()
        
    #Address form submitted, save to session and redirect to payment page
    if addressForm.is_submitted() and cart:
        firstname = addressForm.firstname.data
        surname = addressForm.surname.data
        company = addressForm.company.data
        address1 = addressForm.address1.data
        address2 = addressForm.address2.data
        suburb = addressForm.suburb.data
        state = addressForm.state.data
        country = addressForm.country.data
        email = addressForm.email.data
        phone = addressForm.phone.data
        postcode = addressForm.postcode.data
        
        session['address'] =  {'name': firstname,'surname': surname,'company': company,
                                'address1': address1,'address2': address2,'suburb': suburb,
                                'state': state,'postcode': postcode,'country':country,
                                'phone':phone,'email': email }
        
        if addressForm.validate() == False:
              return render_template('cart.html', banner = BANNER, contact=get_contact(), lines = get_lines(), address = addressForm, total=get_total(), cart= cart, shipping = get_shipping(), addressdata=get_address())
        else:
            
            return redirect(url_for('pay'))
       
        
    return render_template('cart.html',banner = BANNER, contact=get_contact(), lines = get_lines(), address = addressForm, total=get_total(), cart= cart, shipping = get_shipping(), addressdata=get_address())
    
@app.route('/pay')
def pay():
    '''Render pay template displaying cart and payment button.'''  
    address = '' 
    cart = get_cart()
    total = get_total()
    address = get_address()
    
    if(not order_ok()):
        flash(ORDER_ERROR)
        return redirect(url_for('error'))

              
    return render_template('pay.html', banner = BANNER, contact=get_contact(),lines = get_lines(), address = address, cart = cart, total = total, shipping=get_shipping())
    
@app.route('/error')
def error():
    '''Render error template displaing flashed() message.'''  
    
    return render_template('error.html', banner = BANNER, contact=get_contact(),lines = get_lines())
    
@app.route('/success')
def success():
    '''Render success template displaying success or failure of order.'''  
    if(order_ok()):
        send_order()
        log_order(LOG_SUCCESS)
        
    else:
        send_error()
        log_order(LOG_ERROR)
        flash(RETURN_ERROR)
        return redirect(url_for('error'))
        
    empty_cart()
    
    return render_template('success.html', banner = BANNER, contact=get_contact(),lines=get_lines(),message=SUCCESSFUL_ORDER)
      
@app.route('/shipping')
def shipping():
    '''Render shipping template to display SHIPPING and TERMS from config file.'''  
    shipping = SHIPPING
    terms = TERMS
    return render_template('shipping.html', banner = BANNER, contact=get_contact(),lines=get_lines(), shipping = shipping, terms = terms)
    
    
@app.route('/ipn',methods=['GET','POST'])
def ipn():
    '''Receive and process IPN details from paypal to verify correct payment and complete order or display error.'''  
    try:
        arg = ''
        request.parameter_storage_class = ImmutableOrderedMultiDict
        values = request.form
        for x, y in values.iteritems():
            arg += "&{x}={y}".format(x=x,y=y)

        validate_url = 'https://www.sandbox.paypal.com' \
                       '/cgi-bin/webscr?cmd=_notify-validate{arg}' \
                       .format(arg=arg)
        r = requests.get(validate_url)
        
        
        if r.text == 'VERIFIED':

            try:
                payer_email =  escape(request.form.get('payer_email'))
                unix = int(time.time())
                payment_date = escape(request.form.get('payment_date'))
                username = escape(request.form.get('custom'))
                last_name = escape(request.form.get('last_name'))
                payment_gross = escape(request.form.get('payment_gross'))
                payment_fee = escape(request.form.get('payment_fee'))
                payment_net = float(payment_gross) - float(payment_fee)
                payment_status = escape(request.form.get('payment_status'))
                txn_id = escape(request.form.get('txn_id'))
                
                if(order_ok()):
                    send_order()
                    log_order(LOG_SUCCESS)
                    
                else:
                    send_error()
                    log_order(LOG_ERROR)
                    flash(RETURN_ERROR)
                    return redirect(url_for('error'))
                    
                empty_cart() 
        
                
            except Exception as e:
                with open('ipnout.txt','a') as f:
                    data = 'ERROR WITH IPN DATA\n'+str(values)+'\n'
                    f.write(data)
            
            with open('ipnout.txt','a') as f:
                data = 'SUCCESS\n'+str(values)+'\n'
                f.write(data)
                
                #successful payment, send order email
            
            ''' c,conn = connection()
            c.execute("INSERT INTO ipn (unix, payment_date, username, last_name, payment_gross, payment_fee, payment_net, payment_status, txn_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (unix, payment_date, username, last_name, payment_gross, payment_fee, payment_net, payment_status, txn_id))
            conn.commit()
            c.close()
            conn.close()
            gc.collect()'''

        else:
             with open('/tmp/ipnout.txt','a') as f:
                data = 'FAILURE\n'+str(values)+'\n'
                f.write(data)
                
        return r.text
    except Exception as e:
        return str(e)
        
@app.route('/emptysearch')        
def empty_search():
    '''Empty element14 product ordering_service list'''
    total = 0
    if session.get('ordering_service'):
        total = session['ordering_service']['cost']
        session['subtotal'] = session['subtotal'] - total

    session['ordering_service'] = None

    return redirect(url_for('index'))
    
@app.route('/cart/add/<int:row_id>')
def add(row_id):
    '''Add 1 to the qty of row_id in cart list'''
    
    cart = get_cart()
    
    if cart and row_id < len(cart):
        cart[row_id]['qty'] += 1     
        session['cart'] = cart
    else:
        flash(LINE_NOT_FOUND)
        return redirect(url_for('error'))
    
    return redirect(redirect_url())
    
@app.route('/cart/minus/<int:row_id>')
def minus(row_id):
    '''Remove 1 from the qnty of row_id in cart list or remove entirely'''
    cart = get_cart()
    
    if cart and row_id < len(cart):
        if cart[row_id]['qty'] > 0:
            cart[row_id]['qty'] -= 1    
        else:
            del cart[row_id]

        session['cart'] = cart
    else:
        flash(LINE_NOT_FOUND)
        return redirect(url_for('error'))
    
    return redirect(redirect_url())
      
    

def get_e14(search_term):
    '''Use element14 API to get the details of the product searched'''
    product = 0
    ns = '{http://pf.com/soa/services/v1}'
    api_call = API_BASE + API_KEY + search_term
    
    try:
        e = xml.etree.ElementTree.parse(urllib2.urlopen(api_call)).getroot()
    except Exception:
        return 0
    
    results = 0

    #if there are some results, populate the dictionary
    if e.find(ns+'numberOfResults') != None:
        results = int(e.find(ns+'numberOfResults').text )

        if results == 1: 
        
            for product in e.findall(ns+'products'):
                name = ''
                e14id = 0
                partNumber = ''
                new = False
                package = ''
                totalStock = 0
                intStock = 0
                stock = 0
                price = 0         
                
                if product.find(ns+'sku') != None:
                    e14id = int(escape(product.find(ns+'sku').text))

                if product.find(ns+'displayName') != None:
                    name = escape(product.find(ns+'displayName').text)
        
                if product.find(ns+'translatedManufacturerPartNumber') != None:
                    partNumber = escape(product.find(ns+'translatedManufacturerPartNumber').text)
            
                if product.find(ns+'stock/'+ns+'level') != None:        
                    totalStock = int(escape(product.find(ns+'stock/'+ns+'level').text))
                                  
                if product.find(ns+'inventoryCode') != None:
                    if escape(product.find(ns+'inventoryCode').text) == 2:
                        new = True            
                        
            #loop through all stock locations and get the AU stock
                for s in product.findall(ns+'stock/'+ns+'breakdown'):
                    if s.find(ns+'region').text == 'AU':
                        stock = int(escape(s.find(ns+'inv').text))
        
                #loop through all price breaks and get the highest
                for p in product.findall(ns+'prices'):
                    if p.find(ns+'from').text == '1':
                        price = float(escape(p.find(ns+'cost').text))
        
                if totalStock >=0  and stock >=0:
                    intStock = totalStock - stock
        
    #dictionary of product details
    product = {'e14id': e14id, 'name': name,'part':partNumber,'austock':stock, 'intstock':intStock, 'cost':price}
    
   
    return product
    
    
def add_to_cart(product):
    '''Add the selected product to the cart session variable'''
    if session.get('cart'):
       cart = session['cart']
       cart.append(product)
       session['cart'] = cart
    else:
       session['cart'] = [product]


def display_cart():
    '''Unused'''
    lines = []

    '''
    if session.get('cart'):
        for l in session['cart']:
            
            try:
                pid = int(l[0])  
            except ValueError:
                pid = None
                
            if l[1]:
                qty = int(l[1])
            else:
                qty = 1
                
            part_cost = 0.0
                        
            if len(l) == 3:
                part_cost = l[2]

             #If element14 line
            if pid > 1000:
                lines.append(('Ordering Service: '+str(pid),qty,part_cost))
                
            #if an adapter line
            elif pid > 0:
                description = products.product_list[pid][0:3]
                description = description[0]+' to ' +description[1]+' ' + str(description[2])+ ' pins'
                price = products.product_list[pid][3]
                lines.append((description,qty,price))

            #assembly line
            if pid == -1:
                lines.append(("Assembly", qty,l[4])) #assembly charge     
                
      '''
    return lines

def empty_cart():
    '''Remove all data from cart, ordering service and address session variables'''
    session['cart'] = []
    session['ordering_service'] = []
    session['address'] = []

def get_lines():
    '''Return number of lines in the shopping cart'''
    lines = 0
    
    if session.get('cart'):
        lines = len(session['cart'])
        
    return lines
    
def get_shipping():
    '''Return the amount of shipping for a product from the config file'''
    shipping = 0
    
    if get_lines():
        shipping = products.shipping
        
    return shipping
    
def get_total():
    '''Return the total price for all cart including shipping'''
    total = 0
    
    if session.get('cart'):
        for l in session.get('cart'):
            total = total + l['qty']*float(l['price'])
            
    total += get_shipping()
            
    return total
    
def get_cart():
    '''Return the cart list from the session'''
    cart = None

    if session.get('cart'):
        cart = session.get('cart')
        
    return cart
    
def get_address():
    '''Return the address details from the session'''
    address = None
    
    if session.get('address'):
        address = session.get('address')
        
    return address
    
def get_part():
    '''Return the element14 part ID from the session'''
    part = None
    
    if session.get('ordering_service'):
        part = session.get('ordering_service')
        
    return part
    

def order_ok():
    '''Checks if order has something in the cart and an address'''
    ok = False
        

    if get_lines() and get_address():
         ok = True
         
    return ok

def get_contact():
    '''Return dictionary of contact details from the configuration file'''
    return {"email": ADMIN, "skype": SKYPE}


 
    
def send_order():
    '''Send an email to the ADMIN and customer address with an order summary'''
    customer = None #index of email in address tuple
    address = get_address()
    admin = ORDER_EMAIL
    subject = "Order"
    body = ""
    
    if(address):
        customer = address['email']
    
    body += "<table><th><td>Product</td><td>Qty</td><td>Price</td><td>Total</td></th>"
    
    if get_cart():
        for l in get_cart():
            body += "<tr>"
            for p in l:
                body += "<td>"+str(p)+"</td>"
            body += "<td>"+ '%0.2f' %(l['qty'] * l['price']) + "</td>"    
            body += "</tr>"
    body += "</table><table>"
    
    if get_address():
        for l in get_address():
            body +="<tr>"
            body += "<td>"+str(l)+"</td>"
            body += "</tr>"
    
    body += "</table>"
    
    #email customer
    send_email(subject,admin,[customer],'',body)
    #email admin
    send_email(subject,customer,[admin],'',body)
    
def log_order(message = ''):
    '''Write the order to a log file 'orders'''
    address = get_address()
    cart = get_cart()
    log = str(datetime.utcnow()) + '\n'
    
    if address:
        log += str(address) + '\n'
    if cart:
        log += str(cart) + '\n'
    if message:
        log += message + '\n'
        
    with open('orders','a') as f:
        f.write(log)
    
def send_error():
    '''Send an error message to the ADMIN email'''
    admin = ADMIN
    subject = "Order Error"
    body = "<b>ORDER INPUT ERROR</b>"

        
    body += "<table><th><td>Product</td><td>Qty</td><td>Price</td><td>Total</td></th>"
    if get_cart():
        for l in get_cart():
            body += "<tr>"
            for p in l:
                body += "<td>"+str(p)+"</td>"
            body += "<td>"+ '%0.2f' %(l['qty'] * l['price']) + "</td>"    
            body += "</tr>"
    body += "</table><table>"
    if get_address():
        for l in get_address():
            body +="<tr>"
            body += "<td>"+str(l)+"</td>"
            body += "</tr>"
    
    body += "</table>"
    
    
    send_email(subject,admin,[admin],'',body)
        
def send_email(subject, sender, recipients, text_body, html_body):
    '''Actually send email to recipient'''
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)   
    
def redirect_url(default='index'):
    '''Redirect user to previous page'''
    return request.args.get('next') or \
       request.referrer or \
       url_for(default)



        
    
    
            

