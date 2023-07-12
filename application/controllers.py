from flask import Flask, request,redirect,flash,url_for
from flask import render_template
from flask import current_app as app
from application.models import User,Category,Product,Cart
from flask_login import login_required,current_user,logout_user
from flask_security import roles_required
from .database import db
from PIL import Image
import io
import numpy as np
import base64
from sqlalchemy import text



  


@app.route('/') 
def index():
    if request.method=="GET":
        query=text("""select * from product order by prod_id desc;""")
        products=db.session.execute(query).fetchall()[:12]

        # products=Product.query.all()[:12]
        
        categories=Category.query.all()
       
        # print(categories) 
        length=len(categories)

        return render_template('index.html',products=products,categories=categories,len=length)       
    

@app.route('/admin/dashboard',methods=['GET','POST'])

@login_required
@roles_required('admin')

def admin_dashboard():
    if request.method=="GET":
        # print(current_user)
        return render_template('admin_dashboard.html',admin=current_user)
    
@app.route('/categories',methods=['GET','POST'])
@login_required
@roles_required('admin')
def categories():
    if request.method=='GET':  
        query=text("""select * from category order by cat_id desc;""")
        categories=db.session.execute(query).fetchall()
        query = text("""SELECT * FROM product p WHERE ( SELECT COUNT(*) FROM product WHERE prod_cat_id = p.prod_cat_id AND prod_id <= p.prod_id ) <= 5;""")
        result = db.session.execute(query)
        products = result.fetchall()
        # print(categories)    
        return render_template('categories.html',categories=categories,products=products)
        
    
@app.route('/category/add',methods=['POST'])
@login_required
@roles_required('admin')
def add_category():
    if request.method=='POST':
        cat_name=request.form['cat_name']
        descrp=request.form['descrp']
      
        category=Category.query.filter(Category.cat_name.ilike(cat_name)).first()
        if not category:
            category=Category(cat_name=cat_name,description=descrp)

            db.session.add(category)
            db.session.commit()
            
            return redirect(url_for('category',cat_id=category.cat_id))
        flash("This category exists already")
        return redirect('/categories')
    
@app.route('/category/<int:cat_id>',methods=['GET'])
@login_required
@roles_required('admin')
def category(cat_id):

    category=Category.query.filter(Category.cat_id==cat_id).first()
    products=Product.query.filter(Product.prod_cat_id==cat_id).all()
    # print(current_user.roles[0].name)
    return render_template('category.html',category=category,products=products,user=current_user)

@app.route('/category/<int:cat_id>/edit',methods=['GET','POST'])
@login_required
@roles_required('admin')
def edit_category(cat_id):
    if request.method=='GET':
        category=Category.query.filter(Category.cat_id==cat_id).first()
        return render_template('edit_category.html',category=category)
    else:
        cat_name=request.form['cat_name']
        descrp=request.form['description']
      
        category=Category.query.filter(Category.cat_id==cat_id).first()
       
        category.cat_name=cat_name
        category.description=descrp

        db.session.commit()
        
        return redirect(url_for('category',cat_id=cat_id))
    
from flask import send_from_directory

@app.route('/images/<filename>')
def get_image(filename):
    filename=str(filename+'.jpg')
    # print(filename)
    # print(type(filename))
    
    return send_from_directory('static', filename)

    

@app.route('/category/<int:cat_id>/delete' ,methods=['GET','POST'])
@login_required
@roles_required('admin')
def delete_category(cat_id):
    category=Category.query.filter(Category.cat_id==cat_id).first()


    products=Product.query.filter(Product.prod_cat_id==category.cat_id).all()
    for product in products:
        if product:
            carts=Cart.query.filter(Cart.prod_id==product.prod_id).all()
            for cart in carts:
                db.session.delete(cart)
            
            db.session.delete(product)

    
    db.session.delete(category)
    db.session.commit()
    return redirect('/categories') 


       
    
    
@app.route("/<int:cat_id>/add_prod",methods=['GET','POST'])
@login_required
@roles_required('admin')
def add_prod(cat_id):
    if request.method=='GET':
        category=Category.query.filter(Category.cat_id==cat_id).first()
        return render_template('add_product.html',category=category)
    if request.method=='POST':
        prod_name=request.form['prod_name']
        unit=request.form['unit']
        rate_per_unit=request.form['rate']
        quantity=request.form['quantity']
        manufacture=request.form['manufacture']
        expiry=request.form['expiry']
        image=request.files['image']
        if image.filename!='':
        
            image_name=str(prod_name+'.jpg')
        
            image.save('static/{}'.format(image_name))
            cropped_image = crop_image('static/{}'.format(image_name))

            # cropped_image.show()
            cropped_image.save('static/{}'.format(image_name))
         
        

        product=Product(prod_name=prod_name,unit=unit,rate_per_unit=rate_per_unit,quantity=quantity,manufacture=manufacture,expiry=expiry,prod_cat_id=cat_id)
        
        db.session.add(product)
        db.session.commit()

        return redirect(url_for('category',cat_id=cat_id))
    
# cropped_image.show()  # Display the cropped image


    
from PIL import Image

def crop_image(image_path):
    # Open the image using PIL
    image = Image.open(image_path)

    # Calculate the desired crop dimensions
    width, height = image.size
    desired_ratio = 173.5 / 150
    image_ratio = width / height

    if image_ratio > desired_ratio:
        new_width = int(height * desired_ratio)
        new_height = height
    else:
        new_width = width
        new_height = int(width / desired_ratio)

    # Calculate the crop box coordinates
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    right = left + new_width
    bottom = top + new_height

    # Crop the image
    cropped_image = image.crop((left, top, right, bottom))

    # Return the cropped image
    return cropped_image


# # @app.route('/upload', methods=['POST'])
# def upload():
#     file = request.files['image']
#     file.save('static/image.jpg')
#     # Additional logic to store image path in the database if needed
#     return 'Image uploaded successfully'


@app.route('/edit_prod/<int:prod_id>',methods=['GET','POST'])
@login_required
@roles_required('admin')
def edit_prod(prod_id):
    product=Product.query.filter(Product.prod_id==prod_id).first()
    if request.method=='GET':
        category=Category.query.filter(Category.cat_id==product.prod_cat_id).first()
        return render_template('edit_product.html',product=product,category=category)
    
    elif request.method=='POST':
        product.prod_name=request.form['prod_name']
        product.unit=request.form['unit']
        product.rate_per_unit=request.form['rate']
        product.quantity=request.form['quantity']
        product.manufacture=request.form['manufacture']
        product.expiry=request.form['expiry']
        image=request.files['image']
        # print(image.filename)
        # print(type(image))
        if image.filename!='':
        
            image_name=str(product.prod_name+'.jpg')
        
            image.save('static/{}'.format(image_name))
            cropped_image = crop_image('static/{}'.format(image_name))

            # cropped_image.show()
            cropped_image.save('static/{}'.format(image_name))
            
        

        # product=Product(prod_name=prod_name,unit=unit,rate_per_unit=rate_per_unit,quantity=quantity,manufacture=manufacture,expiry=expiry,prod_cat_id=cat_id)
        
        # db.session.add(product)
        db.session.commit()

        return redirect(url_for('edit_prod',prod_id=prod_id))
    
@app.route('/delete/<int:prod_id>')
@login_required
@roles_required('admin')
def delete_product(prod_id):
    product=Product.query.filter(Product.prod_id==prod_id).first()
    # print(product.prod_name)


    carts=Cart.query.filter(Cart.prod_id==product.prod_id).all()
    for cart in carts:
        # print(cart)
        db.session.delete(cart)
    
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('products'))


    
 

@app.route('/products')
@login_required
@roles_required('admin')
def products():
    if request.method=='GET':
        products=Product.query.all()
        return render_template('products.html',products=products)
    
@app.route('/select/category',methods=['GET','POST'])
def select_category():
    if request.method=='GET':
        categories=Category.query.all()
        return render_template('select_category.html',categories=categories)
    # elif request.method=='POST':
    #     return redirect(url_for('add_prod'))



    
@app.route('/show/image')
def show_image():
    product=Product.query.filter(Product.prod_id==7).first()
    # binary_data=product.image

    # # Create a BytesIO object
    # bytes_io = io.BytesIO(binary_data)

    # # Open the image from BytesIO
    # image = Image.open(bytes_io)
    # print(type(image))
    # # Convert the image to a data URL
    # buffered = io.BytesIO()
    # image.save(buffered, format="PNG")
    # image_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
    # data_url = f"data:image/png;base64,{image_data}"
    

    return render_template('image.html')

# @app.route('/add_to_cart/<int:prod_id>',methods=['GET','POST'])
# @login_required

# def add_to_cart(prod_id):
#     if request.method=='GET':
#         product=Product.query.filter(Product.prod_id==prod_id).first()
#         category=Category.query.filter(Category.cat_id==product.prod_cat_id).first()
#         return render_template('add_to_cart.html',product=product,category=category)
    
#     else:
#         quantity=request.form['quantity']
#         cart=Cart.query.filter(Cart.prod_id==prod_id,Cart.user_id==current_user.id).first()
#         if cart:
#             cart.quantity=cart.quantity+int(quantity)
#             product=Product.query.filter(Product.prod_id==prod_id).first()
#             product.quantity=product.quantity-int(quantity)

#         else:
#             cart_product=Cart(prod_id=prod_id,user_id=current_user.id,quantity=quantity)
#             product=Product.query.filter(Product.prod_id==prod_id).first()
#             product.quantity=product.quantity-int(quantity)

#             db.session.add(cart_product)
#         db.session.commit()
#         return redirect(url_for('user_dashboard'))

# Buy now
@app.route('/buy_now',methods=['GET','POST'])
@login_required

def buy_now():
    # if request.method=='GET':
    #     product=Product.query.filter(Product.prod_id==prod_id).first()
    #     category=Category.query.filter(Category.cat_id==product.prod_cat_id).first()
    #     return render_template('add_to_cart.html',product=product,category=category)
    
    if request.method=="GET":
        # quantity=request.form['quantity']
        cart=Cart.query.filter(Cart.user_id==current_user.id).all()
        for item in cart:
            print(cart)
            
            
       

        
           
        # db.session.commit()
        return "Buy now"

@app.route('/add_to_cart/<int:prod_id>',methods=['GET','POST'])
@login_required

def add_to_cart(prod_id):
    if request.method=="GET":
        product=Product.query.filter(Product.prod_id==prod_id).first()
        category=Category.query.filter(Category.cat_id==product.prod_cat_id).first()
        cart=Cart.query.filter(Cart.prod_id==prod_id,Cart.user_id==current_user.id).first()
        return render_template('add_to_cart.html',product=product,category=category,cart=cart)
    
    elif request.method=="POST":
        quantity=request.form['quantity']
        cart=Cart.query.filter(Cart.prod_id==prod_id,Cart.user_id==current_user.id).first()
        if cart:
            cart.quantity=cart.quantity+float(quantity)
            # product=Product.query.filter(Product.prod_id==prod_id).first()
            # product.quantity=product.quantity-int(quantity)

        else:
            cart_product=Cart(prod_id=prod_id,user_id=current_user.id,quantity=quantity)
            # product=Product.query.filter(Product.prod_id==prod_id).first()
            # product.quantity=product.quantity-int(quantity)

            db.session.add(cart_product)
        db.session.commit()
        return redirect(url_for('user_dashboard'))

    





@app.route('/cart',methods=['GET','POST'])
@login_required
def cart():
    if request.method=='GET':
        # cart_prod=db.session.query(Cart,Product).join(Product).filter(Cart.user_id==current_user.id and Cart.prod_id==Product.prod_id).all()
        query = text("select product.prod_id,prod_name,product.quantity as stock,cart.quantity as quantity,cat_name,rate_per_unit,unit from product,cart,category where category.cat_id=prod_cat_id and cart.prod_id=product.prod_id and user_id={} group by product.prod_id;".format(current_user.id))
        result = db.session.execute(query)
        cart_prod = result.fetchall()
        query = text("SELECT sum(cart.quantity*rate_per_unit) as sum FROM product,cart,category where cart.user_id={} and cart.prod_id=product.prod_id and product.prod_cat_id=category.cat_id;".format(current_user.id))
        result = db.session.execute(query)
        total = result.first()
        # print(cart_prod)
        return render_template("cart.html",cart=cart_prod,total=total)
    
    # else:
    #     return redirect('/cart')


@app.route('/edit_cart/<int:user_id>/<int:prod_id>',methods=['POST'])
@login_required
def edit_cart(user_id,prod_id):
    quantity_new=request.form['quantity']

    cart=Cart.query.filter(Cart.user_id==user_id,Cart.prod_id==prod_id).first()
    # quantity_old=cart.quantity
    cart.quantity=float(quantity_new)
    # product=Product.query.filter(Product.prod_id==prod_id).first()
    # product.quantity=product.quantity+int(quantity_old)
    # product.quantity=product.quantity-int(quantity_new)
    
    
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/cart_remove/<int:prod_id>')
@login_required
def cart_remove(prod_id):
    # cart=Cart.query.filter(Cart.user_id==current_user.id,Cart.prod_id==prod_id).first()
    # quantity_old=cart.quantity
    # product=Product.query.filter(Product.prod_id==prod_id).first()
    # product.quantity=product.quantity+int(quantity_old)
    query=text("delete from cart where prod_id={} and user_id={};".format(prod_id,current_user.id))

    db.session.execute(query)
    db.session.commit()
    return redirect(url_for('cart'))




@app.route('/user/dashboard',methods=['GET','POST'])
@login_required
def user_dashboard():
    if request.method=="GET":    
        categories=Category.query.all()
        products=Product.query.all() 
        return render_template('user_dashboard.html',user=current_user,categories=categories,products=products)
    
@app.route('/display/<int:cat_id>')
@login_required
def display_cat(cat_id):
    category=Category.query.filter(Category.cat_id==cat_id).first()
    products=Product.query.filter(Product.prod_cat_id==cat_id).all()
    categories=Category.query.all()
    return render_template('display_cat.html',category=category,products=products,categories=categories)

@app.route('/product/<int:prod_id>')

def product(prod_id):
    if request.method=='GET':
        product=Product.query.filter(Product.prod_id==prod_id).first()
        category=Category.query.filter(Category.cat_id==product.prod_cat_id).first()
        return render_template('product.html',product=product,category=category)
    

    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
    

