drop table if exists tbl_users;
create table tbl_users(
  username text primary key not null,
  password text not null
);
drop table if exists quiz;
create table quiz(
  question text,
  op1 text,
  op2 text,
  op3 text,
  op4 text,
  answer integer
);
