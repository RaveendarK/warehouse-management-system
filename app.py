import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange
from datetime import datetime
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET', 'dev-secret-change-me')

# Use DATABASE_URL environment variable; fallback placeholder
db_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:shadow123@localhost:5432/warehouse_db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models (simple string UUIDs used as PKs for portability)
class Product(db.Model):
    product_id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    sku = db.Column(db.String(64), nullable=True)
    description = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f"<Product {self.product_id} {self.name}>"

class Location(db.Model):
    location_id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return f"<Location {self.location_id} {self.name}>"

class ProductMovement(db.Model):
    movement_id = db.Column(db.String(36), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    from_location = db.Column(db.String(36), db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String(36), db.ForeignKey('location.location_id'), nullable=True)
    product_id = db.Column(db.String(36), db.ForeignKey('product.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    from_loc = db.relationship('Location', foreign_keys=[from_location])
    to_loc = db.relationship('Location', foreign_keys=[to_location])
    product = db.relationship('Product')

    def __repr__(self):
        return f"<Move {self.movement_id} {self.product_id} {self.qty}>"

# Forms
class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    sku = StringField('SKU', validators=[Optional()])
    description = StringField('Description', validators=[Optional()])
    submit = SubmitField('Save')

class LocationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    address = StringField('Address', validators=[Optional()])
    submit = SubmitField('Save')

class MovementForm(FlaskForm):
    product_id = SelectField('Product', validators=[DataRequired()], choices=[])
    from_location = SelectField('From (optional)', validators=[Optional()], choices=[])
    to_location = SelectField('To (optional)', validators=[Optional()], choices=[])
    qty = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Save')

# Routes
@app.route('/')
def index():
    return redirect(url_for('products'))

@app.route('/products')
def products():
    prods = Product.query.order_by(Product.name).all()
    return render_template('products.html', products=prods)

@app.route('/products/add', methods=['GET','POST'])
def add_product():
    form = ProductForm()
    if form.validate_on_submit():
        pid = str(uuid.uuid4())
        p = Product(product_id=pid, name=form.name.data.strip(), sku=form.sku.data.strip() if form.sku.data else None, description=form.description.data.strip() if form.description.data else None)
        db.session.add(p)
        db.session.commit()
        flash('Product saved.', 'success')
        return redirect(url_for('products'))
    return render_template('product_form.html', form=form)

@app.route('/products/<product_id>/edit', methods=['GET','POST'])
def edit_product(product_id):
    p = Product.query.get_or_404(product_id)
    form = ProductForm(obj=p)
    if form.validate_on_submit():
        p.name = form.name.data.strip()
        p.sku = form.sku.data.strip() if form.sku.data else None
        p.description = form.description.data.strip() if form.description.data else None
        db.session.commit()
        flash('Product updated.', 'success')
        return redirect(url_for('products'))
    return render_template('product_form.html', form=form, edit=True, product=p)

@app.route('/products/<product_id>')
def view_product(product_id):
    p = Product.query.get_or_404(product_id)
    movements = ProductMovement.query.filter_by(product_id=product_id).order_by(ProductMovement.timestamp.desc()).all()
    return render_template('product_view.html', product=p, movements=movements)

@app.route('/locations')
def locations():
    locs = Location.query.order_by(Location.name).all()
    return render_template('locations.html', locations=locs)

@app.route('/locations/add', methods=['GET','POST'])
def add_location():
    form = LocationForm()
    if form.validate_on_submit():
        lid = str(uuid.uuid4())
        l = Location(location_id=lid, name=form.name.data.strip(), address=form.address.data.strip() if form.address.data else None)
        db.session.add(l)
        db.session.commit()
        flash('Location saved.', 'success')
        return redirect(url_for('locations'))
    return render_template('location_form.html', form=form)

@app.route('/locations/<location_id>/edit', methods=['GET','POST'])
def edit_location(location_id):
    l = Location.query.get_or_404(location_id)
    form = LocationForm(obj=l)
    if form.validate_on_submit():
        l.name = form.name.data.strip()
        l.address = form.address.data.strip() if form.address.data else None
        db.session.commit()
        flash('Location updated.', 'success')
        return redirect(url_for('locations'))
    return render_template('location_form.html', form=form, edit=True, location=l)

@app.route('/locations/<location_id>')
def view_location(location_id):
    l = Location.query.get_or_404(location_id)
    movements = ProductMovement.query.filter((ProductMovement.from_location==location_id)|(ProductMovement.to_location==location_id)).order_by(ProductMovement.timestamp.desc()).all()
    return render_template('location_view.html', location=l, movements=movements)

@app.route('/movements')
def movements():
    mv = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).all()
    return render_template('movements.html', movements=mv)

@app.route('/movements/add', methods=['GET','POST'])
def add_movement():
    form = MovementForm()
    form.product_id.choices = [(p.product_id, f"{p.name} ({p.sku})" if p.sku else p.name) for p in Product.query.order_by(Product.name).all()]
    locs = [('', '---')] + [(l.location_id, l.name) for l in Location.query.order_by(Location.name).all()]
    form.from_location.choices = locs
    form.to_location.choices = locs

    if form.validate_on_submit():
        if not form.from_location.data and not form.to_location.data:
            flash('Either from or to location must be provided.', 'danger')
            return render_template('movement_form.html', form=form)
        mid = str(uuid.uuid4())
        m = ProductMovement(
            movement_id=mid,
            timestamp=datetime.utcnow(),
            from_location=form.from_location.data or None,
            to_location=form.to_location.data or None,
            product_id=form.product_id.data,
            qty=form.qty.data
        )
        db.session.add(m)
        db.session.commit()
        flash('Movement recorded.', 'success')
        return redirect(url_for('movements'))
    return render_template('movement_form.html', form=form)

@app.route('/balance')
def balance():
    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()

    balances = []
    for p in products:
        for l in locations:
            incoming = db.session.query(db.func.coalesce(db.func.sum(ProductMovement.qty),0)).filter(ProductMovement.product_id==p.product_id, ProductMovement.to_location==l.location_id).scalar() or 0
            outgoing = db.session.query(db.func.coalesce(db.func.sum(ProductMovement.qty),0)).filter(ProductMovement.product_id==p.product_id, ProductMovement.from_location==l.location_id).scalar() or 0
            qty = incoming - outgoing
            balances.append({'product': p, 'location': l, 'qty': qty})
    return render_template('balance.html', balances=balances)

# API endpoint to support AJAX search
@app.route('/api/products/search')
def api_product_search():
    q = request.args.get('q', '').strip()
    if not q:
        prods = Product.query.limit(20).all()
    else:
        prods = Product.query.filter(Product.name.ilike(f"%{q}%") | Product.sku.ilike(f"%{q}%")).limit(50).all()
    results = [{'id': p.product_id, 'text': f"{p.name} ({p.sku})" if p.sku else p.name} for p in prods]
    return jsonify({'results': results})

if __name__ == '__main__':
    # create tables if not present (use migrations in prod)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
