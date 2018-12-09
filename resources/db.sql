create table stations(
  id bigserial primary key ,
  name varchar(30),
  company_id bigint,
  address text,
  cost80 money,
  cost92 money,
  cost95 money,
  cost98 money
);

create type fuelType as enum('80','92','95','98');


create table users(
  id bigserial primary key,
  model varchar(30),
  AvgConsumption int,
  fuel fuelType
);

insert into users (model, AvgConsumption, fuel) values ('bmw', 10,'80');