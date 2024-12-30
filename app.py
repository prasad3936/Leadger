from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuration for MySQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/customer_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model for Customer Data
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    products = db.Column(db.String(255), nullable=False)

# Home route to display all customers
@app.route('/')
def index():
    customers = Customer.query.all()
    total_amount = db.session.query(db.func.sum(Customer.amount)).scalar() or 0
    return render_template('index.html', customers=customers, total_amount=total_amount)

# Route to add a new customer
@app.route('/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        amount = request.form['amount']
        products = request.form['products']

        new_customer = Customer(name=name, mobile=mobile, amount=amount, products=products)
        db.session.add(new_customer)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add_customer.html')

# Route to edit customer details
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.mobile = request.form['mobile']
        customer.amount = request.form['amount']
        customer.products = request.form['products']

        db.session.commit()
        return redirect(url_for('index'))

    return render_template('edit_customer.html', customer=customer)

# Route to delete a customer
@app.route('/delete/<int:id>')
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
