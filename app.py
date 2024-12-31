from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuration for SQLite Database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customer_db.sqlite'
# Configuration for MySQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/customer_db'
#app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}/{os.getenv('MYSQL_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Model for Customer Data
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    products = db.Column(db.String(255), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'credit' or 'debit'
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

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

# Route to handle credit and debit operations
@app.route('/transaction/<int:id>/<string:action>', methods=['POST'])
def transaction(id, action):
    customer = Customer.query.get_or_404(id)
    amount = float(request.form['amount'])

    if action == 'credit':
        customer.amount += amount
        transaction = Transaction(customer_id=id, type='credit', amount=amount)
    elif action == 'debit':
        if customer.amount >= amount:
            customer.amount -= amount
            transaction = Transaction(customer_id=id, type='debit', amount=amount)
        else:
            return "Insufficient balance", 400

    db.session.add(transaction)
    db.session.commit()
    return redirect(url_for('index'))
# Route to print customer invoice
from datetime import datetime

@app.route('/print_invoice/<int:id>')
def print_invoice(id):
    customer = Customer.query.get_or_404(id)
    transactions = Transaction.query.filter_by(customer_id=id).order_by(Transaction.date.desc()).all()
    current_datetime = datetime.utcnow()  # Get the current UTC date and time
    return render_template('invoice.html', customer=customer, transactions=transactions, current_datetime=current_datetime)


if __name__ == '__main__':
    app.run(debug=True)
