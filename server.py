from bson import SON
from flask import Flask, request, jsonify, send_from_directory
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt
from datetime import datetime

# Configurazione dell'app Flask e del database MongoDB
app = Flask(__name__, static_folder='paginaWeb')
client = MongoClient('mongodb://localhost:27017/')
db = client['finance_tracker']

# Route per servire i file statici
@app.route('/')
def home():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/app.js')
def static_js():
    return send_from_directory(app.static_folder, 'app.js')

# Funzione per inizializzare il database (se necessario)
def initialize_db():
    # Creazione delle collezioni 'users' e 'transactions' se non esistono
    if 'users' not in db.list_collection_names():
        db.create_collection('users')
    if 'transactions' not in db.list_collection_names():
        db.create_collection('transactions')
    print("Database and collections initialized successfully!")

# Endpoint per la registrazione degli utenti
@app.route('/register', methods=['POST'])
def register():
    users = db.users
    username = request.json['username']
    password = request.json['password']
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    users.insert_one({'username': username, 'password': hashed_password})
    return jsonify({"message": "Registered successfully"}), 201

# Endpoint per l'aggiunta di transazioni
@app.route('/transaction', methods=['POST'])
def add_transaction():
    transactions = db.transactions
    transaction = {
        "customer_id": request.json['customer_id'],
        "customer_details": {
            "name": request.json['name'],
            "surname": request.json['surname'],
            "gender": request.json['gender'],
            "birthdate": datetime.strptime(request.json['birthdate'], '%Y-%m-%d')  # Ensure date format is correct
        },
        "transaction_amount": request.json['amount'],
        "transaction_date": datetime.strptime(request.json['date'], '%Y-%m-%d'),  # Ensure date format is correct
        "merchant_name": request.json['merchant_name'],
        "category": request.json['category']
    }
    transactions.insert_one(transaction)
    return jsonify({"message": "Transaction added"}), 201
# Endpoint per recuperare le transazioni di un utente
@app.route('/transactions/<user_id>', methods=['GET'])
def get_transactions(user_id):
    transactions = list(db.transactions.find({"user_id": ObjectId(user_id)}))
    return jsonify(transactions), 200


#gestione dei report

# Funzioni di Reportistica
def monthly_spending_report():
    pipeline = [
        {
            "$group": {
                "_id": {"year": {"$year": "$date"}, "month": {"$month": "$date"}},
                "total_spending": {"$sum": "$amount"},
                "total_income": {"$sum": {"$cond": [{"$eq": ["$category", "income"]}, "$amount", 0]}},
                "balance": {"$sum": {"$cond": [{"$eq": ["$category", "expense"]}, {"$multiply": [-1, "$amount"]}, "$amount"]}}
            }
        },
        {"$sort": SON([("_id.year", 1), ("_id.month", 1)])}
    ]
    return list(db.transactions.aggregate(pipeline))

def category_analysis():
    pipeline = [
        {
            "$group": {
                "_id": "$category_id",
                "total_by_category": {"$sum": "$amount"}
            }
        },
        {"$sort": {"total_by_category": -1}}
    ]
    return list(db.transactions.aggregate(pipeline))

def spending_trends():
    pipeline = [
        {
            "$group": {
                "_id": {"year": {"$year": "$date"}, "month": {"$month": "$date"}},
                "total_spending": {"$sum": "$amount"}
            }
        },
        {"$sort": SON([("_id.year", 1), ("_id.month", 1)])}
    ]
    return list(db.transactions.aggregate(pipeline))

def year_on_year_comparison(category_id):
    pipeline = [
        {
            "$match": {"category_id": category_id}
        },
        {
            "$group": {
                "_id": {"year": {"$year": "$date"}},
                "annual_spending": {"$sum": "$amount"}
            }
        },
        {"$sort": {"_id.year": 1}}
    ]
    return list(db.transactions.aggregate(pipeline))

# Route Flask per i Report
@app.route('/report/monthly_spending', methods=['GET'])
def get_monthly_spending():
    result = monthly_spending_report()
    return jsonify(result)

@app.route('/report/category_analysis', methods=['GET'])
def get_category_analysis():
    result = category_analysis()
    return jsonify(result)

@app.route('/report/spending_trends', methods=['GET'])
def get_spending_trends():
    result = spending_trends()
    return jsonify(result)

@app.route('/report/year_comparison', methods=['GET'])
def get_year_comparison():
    category_id = request.args.get('category_id')
    result = year_on_year_comparison(category_id)
    return jsonify(result)

# Altre funzioni e route del tuo Flask app qui...
# Ad esempio, gestione di utenti, transazioni, ecc.



# Avvio dell'applicazione
if __name__ == '__main__':
    initialize_db()  # Assicurati che il database sia inizializzato prima di avviare l'app
    app.run(debug=True)
