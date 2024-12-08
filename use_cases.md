## Here are all the use cases in the application, and their queries. 

1. View public info
```
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
```
These two queries takes all the relevant information of flights within the time range and puts it in the flights search function for any user to see. 


2. Register
```
query = """
    INSERT INTO customer (email, password, first_name, last_name, building_num, street_name,
    apt_num, state, zip, passport_num, passport_expiration, passport_country, date_of_birth)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
params = (
    email_or_username, password, first_name, last_name, building_num, street_name,
    apt_num, state, zip_code, passport_num, passport_expiration, passport_country, date_of_birth
)

query = """
    INSERT INTO staff (username, password, first_name, last_name, date_of_birth)
    VALUES (%s, %s, %s, %s, %s)
"""
params = (email_or_username, password, first_name, last_name, date_of_birth)

query = """
    INSERT INTO staff_email (username, email)
    VALUES (%s, %s)
"""
params = (email_or_username, staff_email)

query = """
    INSERT INTO staff_phone (username, phone_num)
    VALUES (%s, %s)
"""
execute_query(query, (email_or_username, phone_num.strip()))
```
The above queries are for registering customers and staff, they are simple insert queries into the customer, staff, staff_email, and staff_phone tables. 


3. Login
```
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
```
The above queries are for authenticating the login information of customers and staff. They check for entries in the customer and staff tables for accounts where the username/email and the hashed passwords match. 


4. View My flights
```
upcoming_query = """
    SELECT t.ticket_id, f.name AS airline, f.flight_num, f.dep_datetime, f.arr_datetime, t.ticket_price
    FROM ticket t
    JOIN flight f ON t.ticket_id LIKE CONCAT(f.flight_num, '_%%')
    WHERE t.email = %s AND f.dep_datetime > %s
    ORDER BY f.dep_datetime ASC
"""

past_query = """
    SELECT t.ticket_id, f.name AS airline, f.flight_num, f.dep_datetime, f.arr_datetime, t.ticket_price
    FROM ticket t
    JOIN flight f ON t.ticket_id LIKE CONCAT(f.flight_num, '_%%')
    WHERE t.email = %s AND f.dep_datetime <= %s
    ORDER BY f.dep_datetime DESC
"""
```
These two queries checks for tickets that is owned by the customer, and divides them by the current time, seperating them into upcoming and past flights. 

5. Search for flights
```
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
```
Same function as the view public info use cases. These two queries takes all the relevant information of flights within the time range and puts it in the flights search function for any user to see. 


6. Purchase tickets
```
ticket_count_query = """
    SELECT COUNT(*) AS tickets_booked
    FROM ticket
    WHERE ticket_id LIKE CONCAT(%s, '_%%')
"""
ticket_count = execute_query(ticket_count_query, (flight_num,), fetch_one=True)['tickets_booked']

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
```
The first query checks if the flight is full first, making sure there are open seats available. Then the other 2 queries push the new data into the respective tables. 


7. Give ratings and comment
```
rate_query = """
    INSERT INTO rates (name, flight_num, dep_datetime, email, rating, comment)
    VALUES (%s, %s, %s, %s, %s, %s)
"""
execute_query(
    rate_query,
    (flight['name'], flight_num, flight['dep_datetime'], email, rating, comment)
)
```
Simple insert into the rates table when users rates a flight. 

8. Track spending
```
total_query = """
    SELECT SUM(t.ticket_price) AS total_spent
    FROM ticket t
    JOIN purchase_ticket pt ON t.ticket_id = pt.ticket_id
    WHERE t.email = %s AND pt.purchase_datetime BETWEEN %s AND %s
"""
total_spent = execute_query(total_query, (customer_email, start_date, end_date), fetch_one=True)

monthly_query = """
    SELECT DATE_FORMAT(pt.purchase_datetime, '%%Y-%%m') AS month, SUM(t.ticket_price) AS total_spent
    FROM ticket t
    JOIN purchase_ticket pt ON t.ticket_id = pt.ticket_id
    WHERE t.email = %s AND pt.purchase_datetime BETWEEN %s AND %s
    GROUP BY DATE_FORMAT(pt.purchase_datetime, '%%Y-%%m')
    ORDER BY DATE_FORMAT(pt.purchase_datetime, '%%Y-%%m') ASC
"""
monthly_spending = execute_query(monthly_query, (customer_email, start_date, end_date), fetch=True)
```
The first query takes the sum of all ticket prices from the specific customer in the past year, returning the past year's spending. The second query selects the sum of each month in the last 6 months. T


9. Logout
No database query for logging out. 


10. View flights
```
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
```
The query takes all the flights from the staff's company within the specified time range, departure and arrival destinations for the admin's dashboard. 


11. Create new flight
```
flight_query = """
    INSERT INTO flight (name, flight_num, dep_datetime, arr_datetime, base_price, status)
    VALUES (%s, %s, %s, %s, %s, %s)
"""
flight_params = (airline_name, flight_num, dep_datetime, arr_datetime, base_price, status)

departs_query = """
    INSERT INTO departs_from (airport_id, name, flight_num, dep_datetime)
    VALUES (%s, %s, %s, %s)
"""
departs_params = (source_airport_id, airline_name, flight_num, dep_datetime)

arrives_query = """
    INSERT INTO arrives_at (airport_id, name, flight_num, dep_datetime)
    VALUES (%s, %s, %s, %s)
"""
arrives_params = (destination_airport_id, airline_name, flight_num, dep_datetime)

uses_query = """
    INSERT INTO uses (airline_name_flight, flight_num, dep_datetime, airline_name_airplane, airplane_id)
    VALUES (%s, %s, %s, %s, %s)
"""
uses_params = (airline_name, flight_num, dep_datetime, airline_name, airplane_id)
```
The first query inserts into the flight table, the second inserts into departs_from, the third arrives_at, and the last into uses. They all need to updated when a new flight is created. 


12. Change flight status
```
query = """
    UPDATE flight
    SET status = %s
    WHERE flight_num = %s
"""
execute_query(query, (new_status, flight_num))
```
This query changes the status of a preexisting flight by updating the row inside of the flight table. 


13. Add airplane in the system
```
query = """
    INSERT INTO airplane (airplane_id, name, num_seats, manufacturer, model_num, manufacture_date)
    VALUES (%s, %s, %s, %s, %s, %s)
"""
params = (airplane_id, airline, num_seats, manufacturer, model_num, manufacture_date)
```
The query inserts the new airplane into the airplane table. 


14. Add new airport in the system
```
query = """
    INSERT INTO airport (airport_id, name, city, country, num_terminals, type)
    VALUES (%s, %s, %s, %s, %s, %s)
"""
params = (airport_id, name, city, country, num_terminals, airport_type)
```
This query inserts a new airport into the airport table. 



15. View flight ratings
```
average_rating_query = """
    SELECT AVG(r.rating) AS average_rating
    FROM rates r
    WHERE r.flight_num = %s
"""
avg_result = execute_query(average_rating_query, (flight_num,), fetch_one=True)

ratings_query = """
    SELECT r.rating, r.comment, c.email, c.first_name, c.last_name
    FROM rates r
    JOIN customer c ON r.email = c.email
    WHERE r.flight_num = %s
    ORDER BY r.rating DESC
"""
ratings = execute_query(ratings_query, (flight_num,), fetch=True)
```
The first query takes the average rating out of all the ratings on a specific flight, displaying it in the template. The second query takes all the ratings from every customer on a flight and displays the customer information, along with their rating and comment. 


16. Schedule Maintenance
```
query = """
    INSERT INTO airplane_maintenance (airplane_id, start_datetime, end_datetime)
    VALUES (%s, %s, %s)
"""
execute_query(query, (airplane_id, start_datetime, end_datetime))
```
The query inserts maintenance time periods for preexisting airplanes into the airplane_maintenance table. 


17. View frequent customers
```
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

query = """
    SELECT f.flight_num, f.dep_datetime, f.arr_datetime, f.base_price, f.status
    FROM flight f
    JOIN ticket t ON t.ticket_id LIKE CONCAT(f.flight_num, '_%%')
    JOIN employed_by eb ON f.name = eb.name
    WHERE t.email = %s AND eb.username = %s
    ORDER BY f.dep_datetime DESC
"""
flights = execute_query(query, (customer_email, username), fetch=True)
```
The first query takes the staff's company's every flight and calculates the total number of times each account has bought a ticket, and displays the ones with the most tickets bought. The second returns every ticket one customer has bought, showing their flying and purchase history. 


18. View earned revenue
```
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
```
The first query sums the total price of all tickets sold by the staff's company in the last month, and the second query takes the sum of the last year. 


19. Logout
The logout function does not use queries. 