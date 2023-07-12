from .database import db
from flask_security import UserMixin,RoleMixin,Security
from flask_security.forms import SubmitField,StringField,PasswordField,Email,Required,Form,request,BooleanField,LoginForm
from flask_security.forms import RegisterForm,RegisterFormMixin,NextFormMixin,get_form_field_label,Required,ValidatorMixin,Length,password_required
from flask_security.forms import ResetPasswordForm,valid_user_email,ForgotPasswordForm,LoginForm,_datastore,get_message,verify_and_update_password,requires_confirmation,EqualTo,email_required, email_validator, unique_user_email,password_length
from wtforms import StringField


class ExtendedResetPasswordForm(ResetPasswordForm):
    password = PasswordField(
        get_form_field_label('password'),
        validators=[password_required, password_length],render_kw={'placeholder':'New Password'})
    password_confirm = PasswordField(
        get_form_field_label('retype_password'),
        validators=[EqualTo('password', message='RETYPE_PASSWORD_MISMATCH'),
                    password_required],render_kw={'placeholder':'Confirm Password'})
    submit = SubmitField(get_form_field_label('reset_password'),render_kw={'style': 'background-color: #0b4341; color: white;' })

class ExtendedForgotPasswordForm(ForgotPasswordForm):
    """The default forgot password form"""
    email = StringField(
        get_form_field_label('email'),
        validators=[email_required, email_validator, valid_user_email],render_kw={'placeholder':'Email'})


    submit = SubmitField(get_form_field_label('recover_password'),render_kw={'style': 'background-color: #0b4341; color: white;' })

    def validate(self,extra_validators=None):
        if not super(ForgotPasswordForm, self).validate():
            return False
        if requires_confirmation(self.user):
            self.email.errors.append(get_message('CONFIRMATION_REQUIRED')[0])
            return False
        return True


class ExtendedRegisterForm(RegisterForm):
# Form, RegisterFormMixin,UniqueEmailFormMixin, NewPasswordFormMixin
# ConfirmRegisterForm, PasswordConfirmFormMixin,NextFormMixin

# class UniqueEmailFormMixin():
    email = StringField(
        get_form_field_label('email'),
        validators=[email_required, email_validator, unique_user_email],render_kw={'placeholder': 'Email' })

# class NewPasswordFormMixin():
    password = PasswordField(
        get_form_field_label('password'),
        validators=[password_required, password_length],render_kw={'placeholder': 'Password' })

# class PasswordConfirmFormMixin():
    password_confirm = PasswordField(
        get_form_field_label('retype_password'),
        validators=[EqualTo('password', message='RETYPE_PASSWORD_MISMATCH'),
                    password_required],render_kw={'placeholder': 'Confirm Password' })
    
# class RegisterFormMixin  
    submit = SubmitField(get_form_field_label('register'),render_kw={'style': 'background-color: #0b4341; color: white;' })



class ExtendedLoginForm(LoginForm):
    email = StringField(get_form_field_label('email'),
                        validators=[Required(message='EMAIL_NOT_PROVIDED')],render_kw={'placeholder': 'Email' })
    password = PasswordField(get_form_field_label('password'),
                             validators=[password_required],render_kw={'placeholder': 'Password' })
    remember = BooleanField(get_form_field_label('remember_me'))
    submit = SubmitField(get_form_field_label('login'),render_kw={'style': 'background-color: #0b4341; color: white; border-radius: 0px; font-size: 20px;'  })
    def validate(self,extra_validators=None):
        if not super(LoginForm, self).validate():
            return False

        self.user = _datastore.get_user(self.email.data)

        if self.user is None:
            self.email.errors.append(get_message('USER_DOES_NOT_EXIST')[0])
            return False
        if not self.user.password:
            self.password.errors.append(get_message('PASSWORD_NOT_SET')[0])
            return False
        if not verify_and_update_password(self.password.data, self.user):
            self.password.errors.append(get_message('INVALID_PASSWORD')[0])
            return False
        if requires_confirmation(self.user):
            self.email.errors.append(get_message('CONFIRMATION_REQUIRED')[0])
            return False
        if not self.user.is_active:
            self.email.errors.append(get_message('DISABLED_ACCOUNT')[0])
            return False
        return True



# class ExtendedRegisterForm(RegisterForm):
#     email=
    

    # password = PasswordField(get_form_field_label('password'),
    #                          validators=[password_required])
    # email = StringField(get_form_field_label('email'),
    #                     validators=[])
    # submit = SubmitField(get_form_field_label('register'))
    # def __init__(self, *args, **kwargs):
    #     super(ExtendedRegisterForm, self).__init__(*args, **kwargs)
    #     if not self.next.data:
    #         self.next.data = request.args.get('next', '')
    

# class RegisterFormMixin():
#     submit = SubmitField(get_form_field_label('register'))

#     def to_dict(form):
#         def is_field_and_user_attr(member):
#             return isinstance(member, Field) and \
#                 hasattr(_datastore.user_model, member.name)

#         fields = inspect.getmembers(form, is_field_and_user_attr)
#         return dict((key, value.data) for key, value in fields)

# class ConfirmRegisterForm(Form, RegisterFormMixin,
#                           UniqueEmailFormMixin, NewPasswordFormMixin):
#     pass


# class RegisterForm(ConfirmRegisterForm, PasswordConfirmFormMixin,
#                    NextFormMixin):
#     def __init__(self, *args, **kwargs):
#         super(RegisterForm, self).__init__(*args, **kwargs)
#         if not self.next.data:
#             self.next.data = request.args.get('next', '')


roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class User(db.Model,UserMixin):
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String)
    password=db.Column(db.String,nullable=False )
    email=db.Column(db.String)
    active=db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users,backref=db.backref('users', lazy='dynamic'))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True) 
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class Category(db.Model):
    _tablename_='category'
    cat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cat_name=db.Column(db.String,nullable=False,unique=True)
    description=db.Column(db.String)

class Product(db.Model):
    _tablename_='product'
    prod_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    prod_name=db.Column(db.String,nullable=False,unique=True)
    unit=db.Column(db.String,nullable=False)
    rate_per_unit=db.Column(db.Integer,nullable=False)
    quantity=db.Column(db.Integer,nullable=False)
    manufacture=db.Column(db.String,nullable=False)
    expiry=db.Column(db.String,nullable=False)
    prod_cat_id=db.Column(db.Integer,db.ForeignKey("category.cat_id"),nullable=False)
    image=db.Column(db.LargeBinary)
    
   
class Cart(db.Model):
    _tablename_='cart'
    cart_id=db.Column(db.Integer, primary_key=True, autoincrement=True)
    prod_id=db.Column(db.Integer, nullable=False)
    user_id=db.Column(db.Integer, nullable=False)
    quantity=db.Column(db.Integer, nullable=False)
    


    

