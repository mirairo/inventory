from flask import Flask, render_template, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = Flask(__name__)

# Vercel Postgres 연결
def get_db():
    # Vercel이 자동으로 제공하는 환경변수
    database_url = os.environ.get('POSTGRES_URL')
    if not database_url:
        # 로컬 개발용 폴백
        database_url = os.environ.get('DATABASE_URL', 'postgresql://localhost/inventory')
    
    conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return conn

# 데이터베이스 초기화
def init_db():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        queries = [
            '''CREATE TABLE IF NOT EXISTS products (
                product_id SERIAL PRIMARY KEY,
                product_code VARCHAR(100) UNIQUE NOT NULL,
                product_name VARCHAR(200) NOT NULL,
                category VARCHAR(100),
                unit_price DECIMAL(12,2) NOT NULL,
                supplier VARCHAR(200),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS inventory (
                inventory_id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0,
                min_quantity INTEGER DEFAULT 10,
                location VARCHAR(100),
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
            )''',
            '''CREATE TABLE IF NOT EXISTS customers (
                customer_id SERIAL PRIMARY KEY,
                customer_code VARCHAR(100) UNIQUE NOT NULL,
                customer_name VARCHAR(200) NOT NULL,
                contact VARCHAR(50),
                address TEXT,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS sales (
                sale_id SERIAL PRIMARY KEY,
                customer_id INTEGER NOT NULL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount DECIMAL(12,2) NOT NULL,
                payment_status VARCHAR(20) DEFAULT '미수',
                notes TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
            )''',
            '''CREATE TABLE IF NOT EXISTS sale_details (
                detail_id SERIAL PRIMARY KEY,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(12,2) NOT NULL,
                subtotal DECIMAL(12,2) NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(sale_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
            )'''
        ]
        
        for query in queries:
            cursor.execute(query)
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"데이터베이스 초기화 오류: {e}")
        return False

# 라우트
@app.route('/')
def index():
    # 앱 시작시 테이블 생성
    init_db()
    return render_template('index.html')

@app.route('/api/products', methods=['GET', 'POST'])
def products():
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        try:
            cursor.execute(
                'INSERT INTO products (product_code, product_name, category, unit_price, supplier, description) VALUES (%s, %s, %s, %s, %s, %s) RETURNING product_id',
                (data['product_code'], data['product_name'], data.get('category', ''), 
                 data['unit_price'], data.get('supplier', ''), data.get('description', ''))
            )
            result = cursor.fetchone()
            product_id = result['product_id']
            cursor.execute('INSERT INTO inventory (product_id) VALUES (%s)', (product_id,))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': '제품이 등록되었습니다'})
        except psycopg2.IntegrityError as e:
            conn.rollback()
            conn.close()
            return jsonify({'success': False, 'message': '이미 존재하는 제품 코드입니다'}), 400
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({'success': False, 'message': f'오류 발생: {str(e)}'}), 500
    
    else:  # GET
        try:
            search = request.args.get('search', '')
            if search:
                cursor.execute(
                    'SELECT * FROM products WHERE product_name ILIKE %s ORDER BY product_id DESC',
                    (f'%{search}%',)
                )
            else:
                cursor.execute('SELECT * FROM products ORDER BY product_id DESC')
            
            products = cursor.fetchall()
            conn.close()
            return jsonify(products)
        except Exception as e:
            conn.close()
            return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT', 'DELETE'])
def product_detail(product_id):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        if request.method == 'PUT':
            data = request.json
            cursor.execute(
                'UPDATE products SET product_code=%s, product_name=%s, category=%s, unit_price=%s, supplier=%s, description=%s WHERE product_id=%s',
                (data['product_code'], data['product_name'], data.get('category', ''),
                 data['unit_price'], data.get('supplier', ''), data.get('description', ''), product_id)
            )
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': '제품이 수정되었습니다'})
        
        elif request.method == 'DELETE':
            cursor.execute('DELETE FROM products WHERE product_id=%s', (product_id,))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': '제품이 삭제되었습니다'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/inventory', methods=['GET'])
def inventory():
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT p.product_id, p.product_code, p.product_name, i.quantity, i.min_quantity, i.location, i.last_updated
            FROM inventory i JOIN products p ON i.product_id = p.product_id
            ORDER BY p.product_name
        ''')
        inventory = cursor.fetchall()
        conn.close()
        return jsonify(inventory)
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/api/inventory/transaction', methods=['POST'])
def inventory_transaction():
    conn = get_db()
    cursor = conn.cursor()
    data = request.json
    
    try:
        product_id = data['product_id']
        quantity = data['quantity']
        trans_type = data['type']
        
        cursor.execute('SELECT quantity FROM inventory WHERE product_id=%s', (product_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'success': False, 'message': '제품을 찾을 수 없습니다'}), 404
            
        current_qty = result['quantity']
        
        if trans_type == '출고' and current_qty < quantity:
            conn.close()
            return jsonify({'success': False, 'message': '재고가 부족합니다'}), 400
        
        new_qty = current_qty + quantity if trans_type == '입고' else current_qty - quantity
        cursor.execute('UPDATE inventory SET quantity=%s, last_updated=CURRENT_TIMESTAMP WHERE product_id=%s', 
                      (new_qty, product_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': f'{trans_type} 처리가 완료되었습니다'})
    except Exception as e:
        conn.rollback()
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
                'INSERT INTO customers (customer_code, customer_name, contact, email, address) VALUES (%s, %s, %s, %s, %s)',
                (data['customer_code'], data['customer_name'], data.get('contact', ''),
                 data.get('email', ''), data.get('address', ''))
            )
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': '거래처가 등록되었습니다'})
        except psycopg2.IntegrityError:
            conn.rollback()
            conn.close()
            return jsonify({'success': False, 'message': '이미 존재하는 거래처 코드입니다'}), 400
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({'success': False, 'message': str(e)}), 500
    
    else:  # GET
        try:
            search = request.args.get('search', '')
            if search:
                cursor.execute(
                    'SELECT * FROM customers WHERE customer_name ILIKE %s ORDER BY customer_id DESC',
                    (f'%{search}%',)
                )
            else:
                cursor.execute('SELECT * FROM customers ORDER BY customer_id DESC')
            
            customers = cursor.fetchall()
            conn.close()
            return jsonify(customers)
        except Exception as e:
            conn.close()
            return jsonify({'error': str(e)}), 500

@app.route('/api/customers/<int:customer_id>', methods=['PUT', 'DELETE'])
def customer_detail(customer_id):
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        if request.method == 'PUT':
            data = request.json
            cursor.execute(
                'UPDATE customers SET customer_code=%s, customer_name=%s, contact=%s, email=%s, address=%s WHERE customer_id=%s',
                (data['customer_code'], data['customer_name'], data.get('contact', ''),
                 data.get('email', ''), data.get('address', ''), customer_id)
            )
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': '거래처가 수정되었습니다'})
        
        elif request.method == 'DELETE':
            cursor.execute('DELETE FROM customers WHERE customer_id=%s', (customer_id,))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': '거래처가 삭제되었습니다'})
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sales', methods=['GET', 'POST'])
def sales():
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        try:
            cursor.execute('SELECT quantity FROM inventory WHERE product_id=%s', (data['product_id'],))
            result = cursor.fetchone()
            if not result:
                conn.close()
                return jsonify({'success': False, 'message': '제품을 찾을 수 없습니다'}), 404
                
            current_qty = result['quantity']
            
            if current_qty < data['quantity']:
                conn.close()
                return jsonify({'success': False, 'message': '재고가 부족합니다'}), 400
            
            subtotal = data['quantity'] * data['unit_price']
            cursor.execute(
                'INSERT INTO sales (customer_id, total_amount, notes) VALUES (%s, %s, %s) RETURNING sale_id',
                (data['customer_id'], subtotal, data.get('notes', ''))
            )
            result = cursor.fetchone()
            sale_id = result['sale_id']
            
            cursor.execute(
                'INSERT INTO sale_details (sale_id, product_id, quantity, unit_price, subtotal) VALUES (%s, %s, %s, %s, %s)',
                (sale_id, data['product_id'], data['quantity'], data['unit_price'], subtotal)
            )
            
            new_qty = current_qty - data['quantity']
            cursor.execute('UPDATE inventory SET quantity=%s WHERE product_id=%s', (new_qty, data['product_id']))
            
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': '판매가 등록되었습니다', 'sale_id': sale_id})
        except Exception as e:
            conn.rollback()
            conn.close()
            return jsonify({'success': False, 'message': str(e)}), 500
    
    else:  # GET
        try:
            cursor.execute('''
                SELECT s.sale_id, s.sale_date, c.customer_name, p.product_name, 
                       sd.quantity, sd.unit_price, sd.subtotal, s.payment_status
                FROM sales s
                JOIN customers c ON s.customer_id = c.customer_id
                JOIN sale_details sd ON s.sale_id = sd.sale_id
                JOIN products p ON sd.product_id = p.product_id
                ORDER BY s.sale_id DESC LIMIT 200
            ''')
            sales = cursor.fetchall()
            conn.close()
            return jsonify(sales)
        except Exception as e:
            conn.close()
            return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        conn = get_db()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
