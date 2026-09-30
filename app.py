import os
from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "orders_db")
DB_USER = os.getenv("DB_USER", "orders_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "orders_password")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )


def init_db():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_name VARCHAR(100) NOT NULL,
            food_item VARCHAR(100) NOT NULL,
            quantity INTEGER NOT NULL,
            price NUMERIC(10, 2) NOT NULL
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "application": "Online Food Ordering Platform",
        "status": "UP"
    })


@app.route("/health", methods=["GET"])
def health():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        connection.close()

        return jsonify({
            "status": "UP",
            "database": "CONNECTED"
        })
    except Exception as e:
        return jsonify({
            "status": "DOWN",
            "database": "DISCONNECTED",
            "error": str(e)
        }), 500


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    customer_name = data["customer_name"]
    food_item = data["food_item"]
    quantity = data["quantity"]
    price = data["price"]

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO orders
        (customer_name, food_item, quantity, price)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """,
        (customer_name, food_item, quantity, price)
    )

    order_id = cursor.fetchone()[0]

    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({
        "message": "Order created successfully",
        "order_id": order_id,
        "customer_name": customer_name,
        "food_item": food_item,
        "quantity": quantity,
        "price": price
    }), 201


@app.route("/orders", methods=["GET"])
def get_orders():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, customer_name, food_item, quantity, price
        FROM orders
        ORDER BY id
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    orders = []

    for row in rows:
        orders.append({
            "id": row[0],
            "customer_name": row[1],
            "food_item": row[2],
            "quantity": row[3],
            "price": float(row[4])
        })

    return jsonify(orders)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)