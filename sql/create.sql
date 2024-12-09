create table airline (
	name varchar(40) primary key
);


create table staff (
	username varchar(40) primary key,
    password varchar(40) not null,
    first_name varchar(20),
    last_name varchar(20),
    date_of_birth date
);


create table staff_phone (
	username varchar(40),
    phone_num varchar(15) not null,
    primary key (username, phone_num),
    foreign key (username) references staff(username)
);


create table staff_email (
	username varchar(40),
    email varchar(40) not null,
    primary key (username, email),
    foreign key (username) references staff(username)
);


create table employed_by (
	username varchar(40),
    name varchar(40),
    primary key (username, name),
    foreign key (username) references staff(username),
    foreign key (name) references airline(name)
);


create table airplane (
	airplane_id varchar(10) unique,
    name varchar(40) not null,
    num_seats int,
    manufacturer varchar(40),
    model_num varchar(40), 
    manufacture_date date,
    foreign key (name) references airline(name)
);


create table airplane_maintenance (
	airplane_id varchar(10),
    start_datetime datetime,
    end_datetime datetime,
    primary key (airplane_id, start_datetime, end_datetime),
    foreign key (airplane_id) references airplane(airplane_id)
);


create table flight (
    name varchar(40),
    flight_num varchar(40) unique,
    dep_datetime datetime unique,
    arr_datetime datetime,
    base_price numeric(8, 2),
    status varchar(10),
    foreign key (name) references airline(name)
);


create table airport (
    airport_id varchar(10) primary key,
    name varchar(40),
    city varchar(40),
    country varchar(40),
    num_terminals int,
    type varchar(20)
);


create table departs_from (
    airport_id varchar(10),
   	name varchar(40),
    flight_num varchar(40),
    dep_datetime datetime,
    primary key (airport_id, name, flight_num, dep_datetime),
    foreign key (airport_id) references airport(airport_id),
    foreign key (name) references flight(name),
    foreign key (flight_num) references flight(flight_num),
    foreign key (dep_datetime) references flight(dep_datetime)
);


create table arrives_at (
    airport_id varchar(10),
   	name varchar(40),
    flight_num varchar(40),
    dep_datetime datetime,
    primary key (airport_id, name, flight_num, dep_datetime),
    foreign key (airport_id) references airport(airport_id),
    foreign key (name) references flight(name),
    foreign key (flight_num) references flight(flight_num),
    foreign key (dep_datetime) references flight(dep_datetime)
);


create table uses (
    airline_name_flight varchar(40),
    flight_num varchar(40),
    dep_datetime datetime,
    airline_name_airplane varchar(40),
    airplane_id varchar(10),
    primary key (airline_name_flight, flight_num, dep_datetime, airline_name_airplane, airplane_id),
    foreign key (airline_name_flight) references flight(name),
    foreign key (flight_num) references flight(flight_num),
    foreign key (dep_datetime) references flight(dep_datetime),
    foreign key (airline_name_airplane) references airplane(name),
    foreign key (airplane_id) references airplane(airplane_id)
);


create table customer (
	email varchar(40) primary key,
    password varchar(40) not null,
    first_name varchar(20),
    last_name varchar(20),
    building_num varchar(5),
    street_name varchar(10),
    apt_num varchar(5),
    state varchar(20),
    zip varchar(15),
    passport_num varchar(20),
    passport_expiration date,
    passport_country varchar(20),
    date_of_birth date
);


create table ticket (
	ticket_id varchar(10) primary key,
    email varchar(40) not null,
    first_name varchar(20) not null,
    last_name varchar(20) not null,
    date_of_birth date not null,
    ticket_price numeric(8, 2)
);


create table customer_phone (
	email varchar(40),
    phone_num varchar(15) not null,
    primary key (email, phone_num),
    foreign key (email) references customer(email)
);


create table purchase_ticket (
	name varchar(40),
    flight_num varchar(40),
    dep_datetime datetime,
    email varchar(40),
    ticket_id varchar(10),
    card_type varchar(10) not null,
    card_num varchar(20) not null,
    card_name varchar(20) not null,
    exp_date date not null,
    purchase_datetime timestamp,
    foreign key (name) references flight(name),
    foreign key (flight_num) references flight(flight_num),
    foreign key (dep_datetime) references flight(dep_datetime),
    foreign key (email) references customer(email),
    foreign key (ticket_id) references ticket(ticket_id)
);


create table rates (
	name varchar(40),
    flight_num varchar(40),
    dep_datetime datetime,
    email varchar(40),
    rating numeric(2, 1),
    comment text,
    foreign key (name) references flight(name),
    foreign key (flight_num) references flight(flight_num),
    foreign key (dep_datetime) references flight(dep_datetime),
    foreign key (email) references customer(email)
);