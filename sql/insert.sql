insert into airline values ("Jet Blue");


insert into airport
values 
('0', 'JFK', 'New York City', 'USA', 5, 'Both'),
('1', 'PVG', 'Shanghai', 'China', 2, 'Both')
;


insert into customer
values
('johnsmith213@gmail.com', 'raccoon2112', 'John', 'Smith', '21', 'Gold St', '23D', 'NY', '11201', '123456789', '2025-01-01', "USA", '1991-02-22'),
('alicezhang@gmail.com', 'panda88', 'Alice', 'Zhang', '1', 'Johnson St', '22', 'NY', '11201', '283649272', '2027-08-08', "USA", '2001-08-10'),
('danielpark999@gmail.com', 'zebra80', 'Daniel', 'Park', '6', 'Water St', '20X', 'MA', '01869', '973846112', '2030-05-30', "USA", '1966-03-04')
;


insert into customer_phone
values
('johnsmith213@gmail.com', '4752732711'),
('johnsmith213@gmail.com', '2341112450'),
('alicezhang@gmail.com', '2341239921'),
('danielpark999@gmail.com', '5731102221')
;


insert into airplane
values
('0', 'Jet Blue', 110, 'Boeing', '737', '2012-02-01'),
('1', 'Jet Blue', 300, 'Boeing', '767', '2008-09-01'),
('2', 'Jet Blue', 555, 'Airbus', 'A380', '2002-12-01')
;


insert into airplane_maintenance
values
('0', '2016-02-01', '2017-02-01'),
('1', '2012-09-01', '2013-09-01'),
('2', '2008-12-01', '2009-12-01')
;


insert into staff
values
('ac31', 'chicken2003', 'Angela', 'Cheng', '2003-01-01')
;


insert into staff_phone
values
('ac31', '6672992003')
;


insert into staff_email
values
('ac31', 'ac31@jetblue.com')
;


insert into employed_by
values
('ac31', 'Jet Blue')
;



insert into flight
values
('Jet Blue', 'XG201', '2024-12-01 12:00:00', '2024-12-03 10:00:00', 1200.23, 'on time'),
('Jet Blue', 'DD334', '2025-01-01 02:15:00', '2025-01-03 03:10:00', 1104.98, 'on time'),
('Jet Blue', 'LP234', '2025-02-27 21:30:00', '2025-02-28 09:05:00', 987.09, 'delayed')
;


insert into departs_from
values
('0', 'Jet Blue', 'XG201', '2024-12-01 12:00:00'),
('0', 'Jet Blue', 'DD334', '2025-01-01 02:15:00'),
('1', 'Jet Blue', 'LP234', '2025-02-27 21:30:00')
;


insert into arrives_at
values
('1', 'Jet Blue', 'XG201', '2024-12-01 12:00:00'),
('1', 'Jet Blue', 'DD334', '2025-01-01 02:15:00'),
('0', 'Jet Blue', 'LP234', '2025-02-27 21:30:00')
;


insert into uses
values
('Jet Blue', 'XG201', '2024-12-01 12:00:00', 'Jet blue', '0'),
('Jet Blue', 'DD334', '2025-01-01 02:15:00', 'Jet blue', '1'),
('Jet Blue', 'LP234', '2025-02-27 21:30:00', 'Jet blue', '2')
;


insert into ticket
values
('0', 'johnsmith213@gmail.com', 'John', 'Smith', '1991-02-22', 1200.23),
('1', 'alicezhang@gmail.com', 'Alice', 'Zhang', '2001-08-10', 1104.98),
('2', 'danielpark999@gmail.com', 'Daniel', 'Park', '1966-03-04', 987.09)
;


insert into purchase_ticket
values
('Jet Blue', 'XG201', '2024-12-01 12:00:00', 'johnsmith213@gmail.com', '0', 'Debit', '8617520073245274', 'John Smith', '2026-01-01', '2024-11-01 12:02:45'),
('Jet Blue', 'DD334', '2025-01-01 02:15:00', 'alicezhang@gmail.com', '1', 'Debit', '6860774079619289', 'Alice Zhang', '2030-02-01', '2024-11-06 01:02:10'),
('Jet Blue', 'LP234', '2025-02-27 21:30:00', 'danielpark999@gmail.com', '2', 'Credit', '3047881381343531', 'Daniel Park', '2029-09-01', '2024-11-03 23:58:22')
;