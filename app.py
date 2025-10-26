from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# 데이터베이스 초기화
def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    queries = [
        '''CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_code TEXT UNIQUE NOT NULL,
            product_name TEXT NOT NULL,
            category TEXT,
            unit_price REAL NOT NULL,
            supplier TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS inventory (
            inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 0,
            min_quantity INTEGER DEFAULT 10,
            location TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        )''',
        '''CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_code TEXT UNIQUE NOT NULL,
            customer_name TEXT NOT NULL,
            contact TEXT,
            address TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL,
            sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL NOT NULL,
            payment_status TEXT DEFAULT '미수',
            notes TEXT,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
        )''',
        '''CREATE TABLE IF NOT EXISTS sale_details (
            detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        )'''
    ]
    
    for query in queries:
        cursor.execute(query)
    
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row
    return conn

# 라우트
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/products', methods=['GET', 'POST'])
def products():
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        try:
            cursor.execute(
                'INSERT INTO products (product_code, product_name, category, unit_price, supplier, description) VALUES (?, ?, ?, ?, ?, ?)',
                (data['product_code'], data['product_name'], data.get('category', ''), 
                 data['unit_price'], data.get('supplier', ''), data.get('description', ''))
            )
            product_id = cursor.lastrowid
            cursor.execute('INSERT INTO inventory (product_id) VALUES (?)', (product_id,))
            conn.commit()
            return jsonify({'success': True, 'message': '제품이 등록되었습니다'})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': '이미 존재하는 제품 코드입니다'}), 400
        finally:
            conn.close()
    
    else:  # GET
        search = request.args.get('search', '')
        if search:
            cursor.execute(
                'SELECT * FROM products WHERE product_name LIKE ? ORDER BY product_id DESC',
                (f'%{search}%',)
            )
        else:
            cursor.execute('SELECT * FROM products ORDER BY product_id DESC')
        
        products = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(products)

@app.route('/api/products/<int:product_id>', methods=['PUT', 'DELETE'])
def product_detail(product_id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'PUT':
        data = request.json
        cursor.execute(
            'UPDATE products SET product_code=?, product_name=?, category=?, unit_price=?, supplier=?, description=? WHERE product_id=?',
            (data['product_code'], data['product_name'], data.get('category', ''),
             data['unit_price'], data.get('supplier', ''), data.get('description', ''), product_id)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': '제품이 수정되었습니다'})
    
    elif request.method == 'DELETE':
        cursor.execute('DELETE FROM products WHERE product_id=?', (product_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': '제품이 삭제되었습니다'})

@app.route('/api/inventory', methods=['GET'])
def inventory():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.product_id, p.product_code, p.product_name, i.quantity, i.min_quantity, i.location, i.last_updated
        FROM inventory i JOIN products p ON i.product_id = p.product_id
        ORDER BY p.product_name
    ''')
    inventory = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(inventory)

@app.route('/api/inventory/transaction', methods=['POST'])
def inventory_transaction():
    conn = get_db()
    cursor = conn.cursor()
    data = request.json
    
    try:
        product_id = data['product_id']
        quantity = data['quantity']
        trans_type = data['type']  # '입고' or '출고'
        
        cursor.execute('SELECT quantity FROM inventory WHERE product_id=?', (product_id,))
        current_qty = cursor.fetchone()[0]
        
        if trans_type == '출고' and current_qty < quantity:
            return jsonify({'success': False, 'message': '재고가 부족합니다'}), 400
        
        new_qty = current_qty + quantity if trans_type == '입고' else current_qty - quantity
        cursor.execute('UPDATE inventory SET quantity=?, last_updated=CURRENT_TIMESTAMP WHERE product_id=?', 
                      (new_qty, product_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'{trans_type} 처리가 완료되었습니다'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/customers', methods=['GET', 'POST'])
def customers():
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        try:
            cursor.execute(
                'INSERT INTO customers (customer_code, customer_name, contact, email, address) VALUES (?, ?, ?, ?, ?)',
                (data['customer_code'], data['customer_name'], data.get('contact', ''),
                 data.get('email', ''), data.get('address', ''))
            )
            conn.commit()
            return jsonify({'success': True, 'message': '거래처가 등록되었습니다'})
        except sqlite3.IntegrityError:
            return jsonify({'success': False, 'message': '이미 존재하는 거래처 코드입니다'}), 400
        finally:
            conn.close()
    
    else:  # GET
        search = request.args.get('search', '')
        if search:
            cursor.execute(
                'SELECT * FROM customers WHERE customer_name LIKE ? ORDER BY customer_id DESC',
                (f'%{search}%',)
            )
        else:
            cursor.execute('SELECT * FROM customers ORDER BY customer_id DESC')
        
        customers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(customers)

@app.route('/api/sales', methods=['GET', 'POST'])
def sales():
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        try:
            # 재고 확인
            cursor.execute('SELECT quantity FROM inventory WHERE product_id=?', (data['product_id'],))
            current_qty = cursor.fetchone()[0]
            
            if current_qty < data['quantity']:
                return jsonify({'success': False, 'message': '재고가 부족합니다'}), 400
            
            # 판매 등록
            subtotal = data['quantity'] * data['unit_price']
            cursor.execute(
                'INSERT INTO sales (customer_id, total_amount, notes) VALUES (?, ?, ?)',
                (data['customer_id'], subtotal, data.get('notes', ''))
            )
            sale_id = cursor.lastrowid
            
            cursor.execute(
                'INSERT INTO sale_details (sale_id, product_id, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)',
                (sale_id, data['product_id'], data['quantity'], data['unit_price'], subtotal)
            )
            
            # 재고 차감
            new_qty = current_qty - data['quantity']
            cursor.execute('UPDATE inventory SET quantity=? WHERE product_id=?', (new_qty, data['product_id']))
            
            conn.commit()
            return jsonify({'success': True, 'message': '판매가 등록되었습니다', 'sale_id': sale_id})
        except Exception as e:
            conn.rollback()
            return jsonify({'success': False, 'message': str(e)}), 500
        finally:
            conn.close()
    
    else:  # GET
        cursor.execute('''
            SELECT s.sale_id, s.sale_date, c.customer_name, p.product_name, 
                   sd.quantity, sd.unit_price, sd.subtotal, s.payment_status
            FROM sales s
            JOIN customers c ON s.customer_id = c.customer_id
            JOIN sale_details sd ON s.sale_id = sd.sale_id
            JOIN products p ON sd.product_id = p.product_id
            ORDER BY s.sale_id DESC LIMIT 200
        ''')
        sales = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(sales)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
