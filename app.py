from flask import Flask, render_template, request, redirect, session, flash, url_for
import pymysql
from hashlib import md5
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'airline_system'
}

def execute_query(query, params=(), fetch=False, fetch_one=False):
    conn = pymysql.connect(**db_config)
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(query, params)
    if fetch:
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    if fetch_one:
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search_flights():
    departure_flights = None
    return_flights = None

    source = destination = departure_date = return_date = ""

    if request.method == 'POST':
        source = request.form['source']
        destination = request.form['destination']
        departure_date = request.form['departure_date']
        return_date = request.form.get('return_date')

        departure_query = """
            SELECT f.name AS airline, f.flight_num, f.dep_datetime, f.arr_datetime, f.base_price, f.status 
            FROM flight f
            JOIN departs_from df ON f.flight_num = df.flight_num
            JOIN arrives_at aa ON f.flight_num = aa.flight_num
            WHERE df.airport_id IN (
                SELECT airport_id FROM airport WHERE city = %s OR name = %s
            )
            AND aa.airport_id IN (
                SELECT airport_id FROM airport WHERE city = %s OR name = %s
            )
            AND DATE(f.dep_datetime) = %s
        """
        departure_params = (source, source, destination, destination, departure_date)
        departure_flights = execute_query(departure_query, departure_params, fetch=True)

        if return_date:
            return_query = """
                SELECT f.name AS airline, f.flight_num, f.dep_datetime, f.arr_datetime, f.base_price, f.status 
                FROM flight f
                JOIN departs_from df ON f.flight_num = df.flight_num
                JOIN arrives_at aa ON f.flight_num = aa.flight_num
                WHERE df.airport_id IN (
                    SELECT airport_id FROM airport WHERE city = %s OR name = %s
                )
                AND aa.airport_id IN (
                    SELECT airport_id FROM airport WHERE city = %s OR name = %s
                )
                AND DATE(f.dep_datetime) = %s
            """
            return_params = (destination, destination, source, source, return_date)
            return_flights = execute_query(return_query, return_params, fetch=True)

    return render_template(
        'search.html',
        departure_flights=departure_flights,
        return_flights=return_flights,
        source=source,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
    )


@app.route('/register', methods=['GET', 'POST'])
def register():
    role = request.args.get('role', 'customer')
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = md5(request.form['password'].encode()).hexdigest()
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        conn = pymysql.connect(**db_config)
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        try:
            if role == 'customer':
                building_num = request.form['building_num']
                street_name = request.form['street_name']
                apt_num = request.form['apt_num']
                state = request.form['state']
                zip_code = request.form['zip']
                passport_num = request.form['passport_num']
                passport_expiration = request.form['passport_expiration']
                passport_country = request.form['passport_country']
                date_of_birth = request.form['date_of_birth']

                query = """
                    INSERT INTO customer (email, password, first_name, last_name, building_num, street_name,
                    apt_num, state, zip, passport_num, passport_expiration, passport_country, date_of_birth)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                params = (
                    email_or_username, password, first_name, last_name, building_num, street_name,
                    apt_num, state, zip_code, passport_num, passport_expiration, passport_country, date_of_birth
                )
                execute_query(query, params)

            elif role == 'staff':
                date_of_birth = request.form['date_of_birth']
                staff_email = request.form['staff_email']
                phone_nums = request.form.getlist('phone_num')

                query = """
                    INSERT INTO staff (username, password, first_name, last_name, date_of_birth)
                    VALUES (%s, %s, %s, %s, %s)
                """
                params = (email_or_username, password, first_name, last_name, date_of_birth)
                execute_query(query, params)

                query = """
                    INSERT INTO staff_email (username, email)
                    VALUES (%s, %s)
                """
                params = (email_or_username, staff_email)
                execute_query(query, params)

                for phone_num in phone_nums:
                    if phone_num.strip():
                        query = """
                            INSERT INTO staff_phone (username, phone_num)
                            VALUES (%s, %s)
                        """
                        execute_query(query, (email_or_username, phone_num.strip()))

            conn.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        except pymysql.MySQLError as e:
            conn.rollback()
            flash(f'Error: {e}', 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('register.html', role=role)



@app.route('/change_status', methods=['GET', 'POST'])
def change_status():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))

    if request.method == 'POST':
        flight_num = request.form['flight_num']
        new_status = request.form['status']

        try:
            query = """
                UPDATE flight
                SET status = %s
                WHERE flight_num = %s
            """
            execute_query(query, (new_status, flight_num))
            flash('Flight status updated successfully!', 'success')
            return redirect(url_for('staff_dashboard'))
        except Exception as e:
            flash(f'Error updating flight status: {e}', 'danger')

    return render_template('change_status.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email_or_username = request.form['email_or_username']
        password = md5(request.form['password'].encode()).hexdigest()  

        customer_query = """
            SELECT email, first_name, last_name
            FROM customer
            WHERE email = %s AND password = %s
        """
        customer = execute_query(customer_query, (email_or_username, password), fetch_one=True)

        staff_query = """
            SELECT username, first_name, last_name
            FROM staff
            WHERE username = %s AND password = %s
        """
        staff = execute_query(staff_query, (email_or_username, password), fetch_one=True)

        if customer:
            session['user'] = customer['email']
            session['role'] = 'customer'
            session['name'] = f"{customer['first_name']} {customer['last_name']}"
            flash('Login successful! Welcome!', 'success')
            return redirect(url_for('customer_dashboard'))
        elif staff:
            session['user'] = staff['username']
            session['role'] = 'staff'
            session['name'] = f"{staff['first_name']} {staff['last_name']}"
            flash('Login successful! Welcome', 'success')
            return redirect(url_for('staff_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

    return render_template('login.html')



@app.route('/customer_dashboard', methods=['GET', 'POST'])
def customer_dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    current_time = datetime.now()
    customer_email = session.get('user')
    role = session.get('role')

    start_date = (current_time - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = current_time.strftime('%Y-%m-%d')
    total_spent = 0
    monthly_chart_data = []

    if request.method == 'POST':
        start_date = request.form.get('start_date', start_date)
        end_date = request.form.get('end_date', end_date)

    try:
        upcoming_query = """
            SELECT t.ticket_id, f.name AS airline, f.flight_num, f.dep_datetime, f.arr_datetime, t.ticket_price
            FROM ticket t
            JOIN flight f ON t.ticket_id LIKE CONCAT(f.flight_num, '_%%')
            WHERE t.email = %s AND f.dep_datetime > %s
            ORDER BY f.dep_datetime ASC
        """
        upcoming_flights = execute_query(upcoming_query, (customer_email, current_time), fetch=True)

        past_query = """
            SELECT t.ticket_id, f.name AS airline, f.flight_num, f.dep_datetime, f.arr_datetime, t.ticket_price
            FROM ticket t
            JOIN flight f ON t.ticket_id LIKE CONCAT(f.flight_num, '_%%')
            WHERE t.email = %s AND f.dep_datetime <= %s
            ORDER BY f.dep_datetime DESC
        """
        past_flights = execute_query(past_query, (customer_email, current_time), fetch=True)

        total_query = """
            SELECT SUM(t.ticket_price) AS total_spent
            FROM ticket t
            JOIN purchase_ticket pt ON t.ticket_id = pt.ticket_id
            WHERE t.email = %s AND pt.purchase_datetime BETWEEN %s AND %s
        """
        total_spent = execute_query(total_query, (customer_email, start_date, end_date), fetch_one=True)
        total_spent = total_spent['total_spent'] if total_spent['total_spent'] is not None else 0

        monthly_query = """
            SELECT DATE_FORMAT(pt.purchase_datetime, '%%Y-%%m') AS month, SUM(t.ticket_price) AS total_spent
            FROM ticket t
            JOIN purchase_ticket pt ON t.ticket_id = pt.ticket_id
            WHERE t.email = %s AND pt.purchase_datetime BETWEEN %s AND %s
            GROUP BY DATE_FORMAT(pt.purchase_datetime, '%%Y-%%m')
            ORDER BY DATE_FORMAT(pt.purchase_datetime, '%%Y-%%m') ASC
        """
        monthly_spending = execute_query(monthly_query, (customer_email, start_date, end_date), fetch=True)
        monthly_chart_data = [{'month': m['month'], 'total_spent': float(m['total_spent'])} for m in monthly_spending]

        return render_template(
            'customer_dashboard.html',
            upcoming_flights=upcoming_flights,
            past_flights=past_flights,
            total_spent=total_spent,
            monthly_chart_data=monthly_chart_data,
            start_date=start_date,
            end_date=end_date,
        )
    except Exception as e:
        flash(f'Error fetching dashboard data: {e}', 'danger')
        return redirect(url_for('login'))


@app.route('/staff_dashboard', methods=['GET', 'POST'])
def staff_dashboard():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))

    current_time = datetime.now()
    next_30_days = (current_time + timedelta(days=30)).strftime('%Y-%m-%d')
    username = session['user']

    start_date = current_time.strftime('%Y-%m-%d')
    end_date = next_30_days
    source = None
    destination = None
    flights = []

    if request.method == 'POST':
        start_date = request.form.get('start_date', start_date)
        end_date = request.form.get('end_date', end_date)
        source = request.form.get('source', None)
        destination = request.form.get('destination', None)

    try:
        query = """
            SELECT f.flight_num, f.dep_datetime, f.arr_datetime, f.base_price, f.status, 
                   src_airport.city AS source_city, src_airport.airport_id AS source_airport,
                   dest_airport.city AS destination_city, dest_airport.airport_id AS destination_airport
            FROM flight f
            JOIN employed_by eb ON f.name = eb.name
            JOIN departs_from df ON f.flight_num = df.flight_num
            JOIN arrives_at aa ON f.flight_num = aa.flight_num
            JOIN airport src_airport ON df.airport_id = src_airport.airport_id
            JOIN airport dest_airport ON aa.airport_id = dest_airport.airport_id
            WHERE eb.username = %s
              AND f.dep_datetime BETWEEN %s AND %s
              {source_filter} {destination_filter}
            ORDER BY f.dep_datetime ASC
        """
        source_filter = ""
        destination_filter = ""

        params = [username, start_date, end_date]

        if source:
            source_filter = "AND src_airport.city = %s"
            params.append(source)
        if destination:
            destination_filter = "AND dest_airport.city = %s"
            params.append(destination)

        query = query.format(source_filter=source_filter, destination_filter=destination_filter)

        flights = execute_query(query, tuple(params), fetch=True)

        return render_template(
            'staff_dashboard.html',
            flights=flights,
            start_date=start_date,
            end_date=end_date,
            source=source,
            destination=destination,
        )
    except Exception as e:
        flash(f'Error fetching flight data: {e}', 'danger')
        return redirect(url_for('staff_dashboard'))


@app.route('/create_flight', methods=['GET', 'POST'])
def create_flight():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))

    username = session['user']
    airplanes = []
    airports = []

    if request.method == 'POST':
        flight_num = request.form['flight_num']
        dep_datetime = request.form['dep_datetime']
        arr_datetime = request.form['arr_datetime']
        base_price = request.form['base_price']
        status = request.form['status']
        source_airport_id = request.form['source_airport_id']
        destination_airport_id = request.form['destination_airport_id']
        airplane_id = request.form['airplane_id']

        try:
            airline_query = "SELECT name FROM employed_by WHERE username = %s"
            airline_name = execute_query(airline_query, (username,), fetch_one=True)['name']

            flight_query = """
                INSERT INTO flight (name, flight_num, dep_datetime, arr_datetime, base_price, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            flight_params = (airline_name, flight_num, dep_datetime, arr_datetime, base_price, status)
            execute_query(flight_query, flight_params)

            departs_query = """
                INSERT INTO departs_from (airport_id, name, flight_num, dep_datetime)
                VALUES (%s, %s, %s, %s)
            """
            departs_params = (source_airport_id, airline_name, flight_num, dep_datetime)
            execute_query(departs_query, departs_params)

            arrives_query = """
                INSERT INTO arrives_at (airport_id, name, flight_num, dep_datetime)
                VALUES (%s, %s, %s, %s)
            """
            arrives_params = (destination_airport_id, airline_name, flight_num, dep_datetime)
            execute_query(arrives_query, arrives_params)

            uses_query = """
                INSERT INTO uses (airline_name_flight, flight_num, dep_datetime, airline_name_airplane, airplane_id)
                VALUES (%s, %s, %s, %s, %s)
            """
            uses_params = (airline_name, flight_num, dep_datetime, airline_name, airplane_id)
            execute_query(uses_query, uses_params)

            flash('Flight created successfully!', 'success')
            return redirect(url_for('staff_dashboard'))
        except Exception as e:
            flash(f'Error creating flight: {e}', 'danger')

    try:
        airports_query = "SELECT airport_id, name, city FROM airport"
        airports = execute_query(airports_query, fetch=True)

        airline_query = "SELECT name FROM employed_by WHERE username = %s"
        airline_name = execute_query(airline_query, (username,), fetch_one=True)['name']

        if request.method == 'POST':
            airplanes_query = """
                SELECT a.airplane_id, a.name AS airplane_name
                FROM airplane a
                WHERE a.name IN (
                    SELECT name
                    FROM employed_by
                    WHERE username = %s
                )
                AND NOT EXISTS (
                    SELECT 1
                    FROM airplane_maintenance am
                    WHERE am.airplane_id = a.airplane_id
                        AND (
                            am.start_datetime <= %s AND am.end_datetime >= %s
                        )
                )
            """
            airplanes = execute_query(airplanes_query, (username, dep_datetime, arr_datetime), fetch=True)
        else:
            airplanes_query = """
                SELECT a.airplane_id, a.name AS airplane_name
                FROM airplane a
                WHERE a.name IN (
                    SELECT name
                    FROM employed_by
                    WHERE username = %s
                )
            """
            airplanes = execute_query(airplanes_query, (username,), fetch=True)



    except Exception as e:
        flash(f'Error fetching data: {e}', 'danger')

    return render_template('create_flight.html', airports=airports, airplanes=airplanes)



@app.route('/add_airplane', methods=['GET', 'POST'])
def add_airplane():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))

    username = session.get('user')

    if request.method == 'POST':
        airplane_id = request.form['airplane_id']
        name = request.form['name']
        num_seats = request.form['num_seats']
        manufacturer = request.form['manufacturer']
        model_num = request.form['model_num']
        manufacture_date = request.form['manufacture_date']

        try:
            airline_query = "SELECT name FROM employed_by WHERE username = %s"
            airline = execute_query(airline_query, (username,), fetch_one=True)['name']

            query = """
                INSERT INTO airplane (airplane_id, name, num_seats, manufacturer, model_num, manufacture_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (airplane_id, airline, num_seats, manufacturer, model_num, manufacture_date)
            execute_query(query, params)

            flash('Airplane added successfully!', 'success')
            return redirect(url_for('staff_dashboard'))
        except Exception as e:
            flash(f'Error adding airplane: {e}', 'danger')

    return render_template('add_airplane.html')


@app.route('/add_maintenance', methods=['GET', 'POST'])
def add_maintenance():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))

    username = session.get('user')
    airplanes = []

    try:
        airline_query = "SELECT name FROM employed_by WHERE username = %s"
        airline = execute_query(airline_query, (username,), fetch_one=True)['name']

        airplane_query = "SELECT airplane_id, manufacturer, model_num FROM airplane WHERE name = %s"
        airplanes = execute_query(airplane_query, (airline,), fetch=True)
    except Exception as e:
        flash(f'Error fetching airplanes: {e}', 'danger')

    if request.method == 'POST':
        airplane_id = request.form['airplane_id']
        start_datetime = request.form['start_datetime']
        end_datetime = request.form['end_datetime']

        try:
            query = """
                INSERT INTO airplane_maintenance (airplane_id, start_datetime, end_datetime)
                VALUES (%s, %s, %s)
            """
            execute_query(query, (airplane_id, start_datetime, end_datetime))

            flash('Maintenance period added successfully!', 'success')
            return redirect(url_for('staff_dashboard'))
        except Exception as e:
            flash(f'Error adding maintenance period: {e}', 'danger')

    return render_template('add_maintenance.html', airplanes=airplanes)


@app.route('/add_airport', methods=['GET', 'POST'])
def add_airport():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))

    if request.method == 'POST':
        airport_id = request.form['airport_id']
        name = request.form['name']
        city = request.form['city']
        country = request.form['country']
        num_terminals = request.form['num_terminals']
        airport_type = request.form['type']

        try:
            query = """
                INSERT INTO airport (airport_id, name, city, country, num_terminals, type)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            params = (airport_id, name, city, country, num_terminals, airport_type)
            execute_query(query, params)

            flash('Airport added successfully!', 'success')
            return redirect(url_for('staff_dashboard'))
        except Exception as e:
            flash(f'Error adding airport: {e}', 'danger')

    return render_template('add_airport.html')


@app.route('/view_ratings', methods=['GET', 'POST'])
def view_ratings():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))

    average_rating = None
    ratings = []
    flight_num = None

    if request.method == 'POST':
        flight_num = request.form['flight_num']

        try:
            average_rating_query = """
                SELECT AVG(r.rating) AS average_rating
                FROM rates r
                WHERE r.flight_num = %s
            """
            avg_result = execute_query(average_rating_query, (flight_num,), fetch_one=True)
            average_rating = avg_result['average_rating'] if avg_result['average_rating'] else 'No Ratings'

            ratings_query = """
                SELECT r.rating, r.comment, c.email, c.first_name, c.last_name
                FROM rates r
                JOIN customer c ON r.email = c.email
                WHERE r.flight_num = %s
                ORDER BY r.rating DESC
            """
            ratings = execute_query(ratings_query, (flight_num,), fetch=True)

        except Exception as e:
            flash(f'Error fetching ratings: {e}', 'danger')

    return render_template(
        'view_ratings.html',
        flight_num=flight_num,
        average_rating=average_rating,
        ratings=ratings
    )


@app.route('/frequent_flyers', methods=['GET'])
def frequent_flyers():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))

    try:
        username = session.get('user')
        current_time = datetime.now()
        one_year_ago = (current_time - timedelta(days=365)).strftime('%Y-%m-%d')

        frequent_flyers_query = """
            SELECT c.email, c.first_name, c.last_name, COUNT(t.ticket_id) AS ticket_count
            FROM ticket t
            JOIN customer c ON t.email = c.email
            JOIN purchase_ticket pt ON t.ticket_id = pt.ticket_id
            JOIN flight f ON t.ticket_id LIKE CONCAT(f.flight_num, '_%%')
            JOIN employed_by eb ON f.name = eb.name
            WHERE eb.username = %s AND pt.purchase_datetime >= %s
            GROUP BY c.email
            ORDER BY ticket_count DESC
            LIMIT 10
        """
        frequent_flyers = execute_query(frequent_flyers_query, (username, one_year_ago), fetch=True)

        return render_template(
            'frequent_flyers.html',
            frequent_flyers=frequent_flyers
        )
    except Exception as e:
        flash(f'Error fetching frequent flyers: {e}', 'danger')
        return redirect(url_for('staff_dashboard'))


@app.route('/view_customer', methods=['GET', 'POST'])
def view_customer():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))

    customer_email = None
    flights = []
    username = session.get('user')

    if request.method == 'POST':
        customer_email = request.form['customer_email']

        try:
            query = """
                SELECT f.flight_num, f.dep_datetime, f.arr_datetime, f.base_price, f.status
                FROM flight f
                JOIN ticket t ON t.ticket_id LIKE CONCAT(f.flight_num, '_%%')
                JOIN employed_by eb ON f.name = eb.name
                WHERE t.email = %s AND eb.username = %s
                ORDER BY f.dep_datetime DESC
            """
            flights = execute_query(query, (customer_email, username), fetch=True)
        except Exception as e:
            flash(f'Error fetching customer flights: {e}', 'danger')

    return render_template(
        'view_customer.html',
        customer_email=customer_email,
        flights=flights
    )


@app.route('/view_revenue', methods=['GET'])
def view_revenue():
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))

    username = session.get('user')
    current_time = datetime.now()
    last_month_start = (current_time - timedelta(days=current_time.day)).strftime('%Y-%m-01')
    last_month_end = current_time.strftime('%Y-%m-%d')
    last_year_start = (current_time - timedelta(days=365)).strftime('%Y-%m-%d')

    try:
        last_month_query = """
            SELECT SUM(t.ticket_price) AS total_revenue
            FROM ticket t
            JOIN purchase_ticket pt ON t.ticket_id = pt.ticket_id
            JOIN flight f ON t.ticket_id LIKE CONCAT(f.flight_num, '_%%')
            JOIN employed_by eb ON f.name = eb.name
            WHERE eb.username = %s AND pt.purchase_datetime BETWEEN %s AND %s
        """
        last_month_revenue = execute_query(
            last_month_query, (username, last_month_start, last_month_end), fetch_one=True
        )
        last_month_revenue = last_month_revenue['total_revenue'] if last_month_revenue['total_revenue'] else 0

        last_year_query = """
            SELECT SUM(t.ticket_price) AS total_revenue
            FROM ticket t
            JOIN purchase_ticket pt ON t.ticket_id = pt.ticket_id
            JOIN flight f ON t.ticket_id LIKE CONCAT(f.flight_num, '_%%')
            JOIN employed_by eb ON f.name = eb.name
            WHERE eb.username = %s AND pt.purchase_datetime >= %s
        """
        last_year_revenue = execute_query(
            last_year_query, (username, last_year_start), fetch_one=True
        )
        last_year_revenue = last_year_revenue['total_revenue'] if last_year_revenue['total_revenue'] else 0

        return render_template(
            'view_revenue.html',
            last_month_revenue=last_month_revenue,
            last_year_revenue=last_year_revenue
        )
    except Exception as e:
        flash(f'Error fetching revenue data: {e}', 'danger')
        return redirect(url_for('staff_dashboard'))



@app.route('/flight_customers/<flight_num>', methods=['GET'])
def flight_customers(flight_num):
    if 'user' not in session or session.get('role') != 'staff':
        return redirect(url_for('login'))

    try:
        query = """
            SELECT t.email, t.first_name, t.last_name, t.date_of_birth, t.ticket_price
            FROM ticket t
            WHERE t.ticket_id LIKE CONCAT(%s, '_%%')
        """
        customers = execute_query(query, (flight_num,), fetch=True)

        return render_template('flight_customers.html', flight_num=flight_num, customers=customers)
    except Exception as e:
        flash(f'Error fetching customer data: {e}', 'danger')
        return redirect(url_for('staff_dashboard'))



@app.route('/rate_flight/<flight_num>', methods=['GET', 'POST'])
def rate_flight(flight_num):
    if 'user' not in session or session.get('role') != 'customer':
        flash('You need to be logged in as a customer to rate flights.', 'danger')
        return redirect(url_for('login'))

    if request.method == 'POST':
        rating = request.form['rating']
        comment = request.form['comment']

        email = session['user']

        flight_query = """
            SELECT dep_datetime, name
            FROM flight
            WHERE flight_num = %s
        """
        flight = execute_query(flight_query, (flight_num,), fetch_one=True)

        if not flight:
            flash('Flight not found.', 'danger')
            return redirect(url_for('customer_dashboard'))

        if flight['dep_datetime'] > datetime.now():
            flash('You can only rate past flights.', 'danger')
            return redirect(url_for('customer_dashboard'))

        try:
            rate_query = """
                INSERT INTO rates (name, flight_num, dep_datetime, email, rating, comment)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            execute_query(
                rate_query,
                (flight['name'], flight_num, flight['dep_datetime'], email, rating, comment)
            )
            flash('Thank you for your feedback!', 'success')
        except Exception as e:
            flash(f'Error submitting your rating: {e}', 'danger')

        return redirect(url_for('customer_dashboard'))

    return render_template('rate_flight.html', flight_num=flight_num)



@app.route('/purchase_ticket/<flight_num>', methods=['GET', 'POST'])
def purchase_ticket(flight_num):
    if 'user' not in session or session.get('role') != 'customer':
        flash('You need to be logged in as a customer to purchase tickets.', 'danger')
        return redirect(url_for('login'))

    try:
        flight_query = """
            SELECT f.name AS airline, f.dep_datetime, f.base_price, a.num_seats
            FROM flight f
            JOIN uses u ON f.flight_num = u.flight_num
            JOIN airplane a ON u.airplane_id = a.airplane_id
            WHERE f.flight_num = %s
        """
        flight = execute_query(flight_query, (flight_num,), fetch_one=True)

        if not flight:
            flash('Flight not found.', 'danger')
            return redirect(url_for('search_flights'))

        ticket_count_query = """
            SELECT COUNT(*) AS tickets_booked
            FROM ticket
            WHERE ticket_id LIKE CONCAT(%s, '_%%')
        """
        ticket_count = execute_query(ticket_count_query, (flight_num,), fetch_one=True)['tickets_booked']
        available_seats = flight['num_seats'] - ticket_count

        if available_seats <= 0:
            flash('Sorry, this flight is fully booked.', 'danger')
            return redirect(url_for('search_flights'))

        ticket_price = flight['base_price']
        if ticket_count / flight['num_seats'] >= 0.8:
            ticket_price *= 1.25

        if request.method == 'POST':
            customer_email = session['user']
            num_tickets = int(request.form['num_tickets'])
            if num_tickets > available_seats:
                flash(f'Only {available_seats} seats are available.', 'danger')
                return redirect(url_for('purchase_ticket', flight_num=flight_num))

            card_type = request.form['card_type']
            card_num = request.form['card_num']
            card_name = request.form['card_name']
            exp_date = request.form['exp_date']
            purchase_time = datetime.now()

            for i in range(num_tickets):
                first_name = request.form[f'first_name_{i}']
                last_name = request.form[f'last_name_{i}']
                date_of_birth = request.form[f'date_of_birth_{i}']

                ticket_id = f"{flight_num}_{hash(first_name + last_name + date_of_birth) % 1000000}"

                ticket_query = """
                    INSERT INTO ticket (ticket_id, email, first_name, last_name, date_of_birth, ticket_price)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                execute_query(
                    ticket_query,
                    (ticket_id, customer_email, first_name, last_name, date_of_birth, ticket_price)
                )

                purchase_query = """
                    INSERT INTO purchase_ticket (name, flight_num, dep_datetime, email, ticket_id, card_type, card_num, card_name, exp_date, purchase_datetime)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                execute_query(
                    purchase_query,
                    (
                        flight['airline'],
                        flight_num,
                        flight['dep_datetime'],
                        customer_email,
                        ticket_id,
                        card_type,
                        card_num,
                        card_name,
                        exp_date,
                        purchase_time,
                    )
                )

            flash('Tickets purchased successfully!', 'success')
            return redirect(url_for('search_flights'))

        return render_template('purchase_ticket.html', flight_num=flight_num, ticket_price=ticket_price, available_seats=available_seats)

    except Exception as e:
        flash(f'Error purchasing tickets: {e}', 'danger')
        return redirect(url_for('search_flights'))


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# def test():
#     conn = pymysql.connect(**db_config)
#     cursor = conn.cursor(pymysql.cursors.DictCursor)
    
#     query = """
#                 INSERT INTO customer (email, password, first_name, last_name, building_num, street_name,
#                 apt_num, state, zip, passport_num, passport_expiration, passport_country, date_of_birth)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """
#     params = (
#         "a@a", "123a", "test", "test", "12", "asdf",
#         "12", "NY", "12234", "123423", '2024-12-06', "USA", '2024-12-06'
#     )
    
#     cursor.execute(query, params)
#     result = cursor.fetchall()

#     conn.commit()
#     cursor.close()
#     conn.close()
#     print(result)

if __name__ == '__main__':
    app.run(debug=True)
    # test()
