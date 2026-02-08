from flask import Flask, render_template_string, request, jsonify
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    issue_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Open')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    resolved_at = db.Column(db.DateTime)

# Routes
@app.route('/')
def index():
    # Inside your index() route in rms.py
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Wi-Fi Issue Reporting | RMS</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Inter', sans-serif;
                background-color: #f2f4f8;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }
            .card {
                background: white;
                padding: 2rem;
                border-radius: 12px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 500px;
            }
            h2 {
                margin-bottom: 1.5rem;
                color: #2f3e46;
            }
            label {
                font-weight: 600;
                display: block;
                margin-top: 1rem;
                margin-bottom: 0.5rem;
            }
            input, select, textarea {
                width: 100%;
                padding: 0.7rem;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 1rem;
            }
            button {
                margin-top: 1.5rem;
                padding: 0.8rem;
                width: 100%;
                background-color: #007bff;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                cursor: pointer;
            }
            button:hover {
                background-color: #0056b3;
            }
            .message {
                margin-top: 1rem;
                color: green;
                font-weight: 600;
            }
        </style>
        <script>
            function submitComplaint() {
                const customer_id = document.getElementById("customer_id").value;
                const issue_type = document.getElementById("issue_type").value;
                const description = document.getElementById("description").value;

                fetch('/complaint', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ customer_id, issue_type, description })
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById("message").textContent = data.message;
                })
                .catch(error => {
                    document.getElementById("message").textContent = "Something went wrong.";
                    console.error(error);
                });
            }
        </script>
    </head>
    <body>
        <div class="card">
            <h2>Report Wi-Fi Issue</h2>
            <label for="customer_id">Customer ID:</label>
            <input type="number" id="customer_id" name="customer_id" required>

            <label for="issue_type">Issue Type:</label>
            <select id="issue_type" name="issue_type">
                <option value="No Connection">No Connection</option>
                <option value="Disconnected After Some Time">Disconnected After Some Time</option>
                <option value="Low Speed">Low Speed</option>
                <option value="Unable to Connect">Unable to Connect</option>
            </select>

            <label for="description">Description:</label>
            <textarea id="description" name="description" rows="4"></textarea>

            <button type="button" onclick="submitComplaint()">Submit Complaint</button>
            <div class="message" id="message"></div>
        </div>
    </body>
    </html>
    """)


@app.route('/add-customer', methods=['POST'])
def add_customer():
    data = request.get_json()
    customer = Customer(
        name=data['name'],
        email=data['email'],
        phone_number=data.get('phone_number')
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({'message': 'Customer added successfully', 'id': customer.id})

@app.route('/complaint', methods=['POST'])
def create_complaint():
    data = request.get_json()
    complaint = Complaint(
        customer_id=data['customer_id'],
        issue_type=data['issue_type'],
        description=data['description']
    )
    db.session.add(complaint)
    db.session.commit()
    return jsonify({"message": "Complaint registered successfully"}), 201

@app.route('/complaint/<int:id>', methods=['PUT'])
def update_complaint(id):
    complaint = Complaint.query.get_or_404(id)
    data = request.get_json()
    complaint.status = data.get('status', complaint.status)
    if complaint.status == 'Resolved':
        complaint.resolved_at = db.func.current_timestamp()
    db.session.commit()
    return jsonify({"message": "Complaint updated successfully"}), 200

@app.route('/complaints', methods=['GET'])
def get_complaints():
    complaints = Complaint.query.all()
    return jsonify([{
        'id': c.id,
        'issue_type': c.issue_type,
        'status': c.status,
        'created_at': c.created_at,
        'resolved_at': c.resolved_at
    } for c in complaints])

@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([
        {
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'phone_number': c.phone_number
        }
        for c in customers
    ])

@app.route('/view/customers')
def view_customers():
    customers = Customer.query.all()
    return render_template_string("""
    <html>
    <head>
        <title>Customer List</title>
        <style>
            table {
                border-collapse: collapse;
                width: 60%;
                margin: 20px auto;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <h2 style="text-align:center;">Customer List</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone Number</th>
            </tr>
            {% for c in customers %}
            <tr>
                <td>{{ c.id }}</td>
                <td>{{ c.name }}</td>
                <td>{{ c.email }}</td>
                <td>{{ c.phone_number }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """, customers=customers)

@app.route('/view/complaints')
def view_complaints():
    complaints = Complaint.query.join(Customer).add_columns(
        Complaint.id,
        Complaint.issue_type,
        Complaint.status,
        Complaint.created_at,
        Complaint.resolved_at,
        Customer.name.label("customer_name")
    ).all()

    return render_template_string("""
    <html>
    <head>
        <title>Complaint List</title>
        <style>
            table {
                border-collapse: collapse;
                width: 90%;
                margin: 20px auto;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: center;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <h2 style="text-align:center;">Complaint List</h2>
        <table>
            <tr>
                <th>ID</th>
                <th>Customer</th>
                <th>Issue Type</th>
                <th>Status</th>
                <th>Created At</th>
                <th>Resolved At</th>
            </tr>
            {% for c in complaints %}
            <tr>
                <td>{{ c.id }}</td>
                <td>{{ c.customer_name }}</td>
                <td>{{ c.issue_type }}</td>
                <td>{{ c.status }}</td>
                <td>{{ c.created_at }}</td>
                <td>{{ c.resolved_at if c.resolved_at else '—' }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """, complaints=complaints)


# Create tables if not exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

