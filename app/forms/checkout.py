from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, RadioField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class CheckoutForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    address_line1 = StringField('Address Line 1', validators=[DataRequired()])
    address_line2 = StringField('Address Line 2')
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State/Province', validators=[DataRequired()])
    zip_code = StringField('ZIP/Postal Code', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    shipping_method = RadioField(
        'Shipping Method',
        choices=[
            ('standard', 'Standard (5-7 days) - $5.99'),
            ('express', 'Express (2-3 days) - $12.99'),
            ('overnight', 'Overnight - $24.99')
        ],
        default='standard'
    )
    submit = SubmitField('Place Order')
