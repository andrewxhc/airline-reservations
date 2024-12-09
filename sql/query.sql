select * from flight where dep_datetime > NOW();


name	flight_num	dep_datetime	arr_datetime	base_price	
Jet Blue	XG201	2024-12-01 12:00:00	2024-12-03 10:00:00	1200.23	
Jet Blue	DD334	2025-01-01 02:15:00	2025-01-03 03:10:00	1104.98	
Jet Blue	LP234	2025-02-27 21:30:00	2025-02-28 09:05:00	987.09	




select * from flight where status='delayed';



Jet Blue	LP234	2025-02-27 21:30:00	2025-02-28 09:05:00	987.09	delayed	




select distinct customer.first_name, customer.last_name
from customer
join purchase_ticket on customer.email=purchase_ticket.email;


first_name	last_name	
Alice	Zhang	
Daniel	Park	
John	Smith	




select *
from airplane 
where name='Jet Blue';


airplane_id	name	num_seats	manufacturer	model_num	manufacture_date	
0	Jet Blue	110	Boeing	737	2012-02-01	
1	Jet Blue	300	Boeing	767	2008-09-01	
2	Jet Blue	555	Airbus	A380	2002-12-01	
