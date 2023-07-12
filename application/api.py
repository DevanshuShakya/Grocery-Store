from flask_restful import Resource, fields, marshal_with, reqparse
from application.database import db
from application.models import Product,Category,Cart

product_fields={
    "prod_id": fields.Integer,
    "prod_name": fields.String,
    "unit": fields.String,
    "rate_per_unit": fields.Integer,
    "quantity": fields.Integer,
    "manufacture": fields.String,
    "expiry": fields.String,
    "prod_cat_name": fields.String
}

create_user_parser=reqparse.RequestParser()
create_user_parser.add_argument('prod_name',type=str,required=True)
create_user_parser.add_argument('unit',type=str,required=True)
create_user_parser.add_argument('rate_per_unit',type=int,required=True)
create_user_parser.add_argument('quantity',type=int,required=True)
create_user_parser.add_argument('manufacture',type=str,required=True)
create_user_parser.add_argument('expiry',type=str,required=True)
create_user_parser.add_argument('prod_cat_name',type=str,required=True)

update_user_parser=reqparse.RequestParser()
update_user_parser.add_argument('prod_name',type=str)
update_user_parser.add_argument('unit',type=str)
update_user_parser.add_argument('rate_per_unit',type=int)
update_user_parser.add_argument('quantity',type=int)
update_user_parser.add_argument('manufacture',type=str)
update_user_parser.add_argument('expiry',type=str)


class ProductAPI(Resource):
    @marshal_with(product_fields)
    def get(self,prod_name):
     
        product=Product.query.filter(Product.prod_name==prod_name).first()
        if product:
            return product
        else:
            return "No such product available",404
        
    @marshal_with(product_fields)
    def put(self,prod_name):
        product=Product.query.filter(Product.prod_name==prod_name).first()

        if product:        
            args=update_user_parser.parse_args()
            if args.get("prod_name",None):
                product.prod_name=args.get("prod_name",None)
            if args.get("unit",None):
                product.unit=args.get("unit",None)
            if args.get("rate_per_unit",None):
                product.rate_per_unit=args.get("rate_per_unit",None)
            if args.get("quantity",None):
                product.quantity=args.get("quantity",None)
            if args.get("manufacture",None):
                product.manufacture=args.get("manufacture",None)
            if args.get("expiry",None):
                product.expiry=args.get("expiry",None)
                
            db.session.commit()
            return product
        else:
            return "",404

    def delete(self,prod_name):
        product=Product.query.filter(Product.prod_name==prod_name).first()
        print(product.prod_name)

        if product:
            carts=Cart.query.filter(Cart.prod_id==product.prod_id).all()
            for cart in carts:
                print(cart)
                db.session.delete(cart)
            
            db.session.delete(product)
            db.session.commit()
            return "",200


        
        else:
            return "No such product available",404
    

    def post(self):
        args=create_user_parser.parse_args()
        prod_name=args.get("prod_name",None)
        unit=args.get("unit",None)
        rate_per_unit=args.get("rate_per_unit",None)
        quantity=args.get("quantity",None)
        manufacture=args.get("manufacture",None)
        expiry=args.get("expiry",None)
        prod_cat_name=args.get("prod_cat_name",None)

        category=Category.query.filter(Category.cat_name==prod_cat_name).first()
        prod_cat_id=category.cat_id


        print("prod_cat_id:",prod_cat_id)

        # prod_cat_id=10
        print(prod_name)
        
        prodcut=Product.query.filter(Product.prod_name==prod_name).first()
        if product:
            return "Product is available already",404
       
         
        else:
            product=Product(prod_name=prod_name,unit=unit,rate_per_unit=rate_per_unit,quantity=quantity,manufacture=manufacture,expiry=expiry,prod_cat_id=prod_cat_id)
            print(product.prod_cat_id)
            db.session.add(product)
            db.session.commit()

            # return redirect(url_for('category',cat_id=cat_id))
            return "",201
        

category_fields={
    "cat_id": fields.Integer,
    "cat_name": fields.String,
    "description": fields.String
}


create_category_parser=reqparse.RequestParser()

create_category_parser.add_argument("cat_name",type=str,required=True) 
create_category_parser.add_argument('description',type=str) 

update_category_parser=reqparse.RequestParser()
update_category_parser.add_argument("cat_name",type=str)
update_category_parser.add_argument("description",type=str)

class CategoryAPI(Resource):
    @marshal_with(category_fields)
    def get(self,cat_name):
        category=Category.query.filter(Category.cat_name==cat_name).first()
        if category:
            return category
        else:
            return "",404
        

    @marshal_with(category_fields)
    def put(self,cat_name):
        category=Category.query.filter(Category.cat_name==cat_name).first()
        if category:
            args=update_category_parser.parse_args()

            if args.get("cat_name",None):
                category.cat_name=args.get("cat_name")
            if args.get("description",None):
                category.description=args.get("description")
        
            db.session.commit()
            return category
        else:
            return "No such category available",404

    def delete(self,cat_name):
        category=Category.query.filter(Category.cat_name==cat_name).first()

        if category:
            products=Product.query.filter(Product.prod_cat_id==category.cat_id).all()
            for product in products:
                if product:
                    carts=Cart.query.filter(Cart.prod_id==product.prod_id).all()
                    for cart in carts:
                        db.session.delete(cart)
                    
                    db.session.delete(product)
    
            
            db.session.delete(category)
            db.session.commit()
            return "",200


        
        else:
            return "No such category available",404
        
    def post(self):

        args=create_category_parser.parse_args()
        
        
        cat_name=args.get("cat_name",None)
        description=args.get("description",None)
        print(cat_name)
        # cat_name="Home and Office"

        category=Category.query.filter(Category.cat_name==cat_name).first()
        if category:
            return "Category is already available",404
        else:

            category=Category(cat_name=cat_name,description=description)
            db.session.add(category)
            db.session.commit()
            return "",201

