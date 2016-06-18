create table keycode (
	type	varchar(10),
	name	varchar(16),
	code	varchar(8),
	primary key (type, name),
	unique (type, code)
);

insert into keycode values ('os', 'Windows', 'WIN');
insert into keycode values ('os', 'CentOS', 'CEN');
insert into keycode values ('os', 'Redhat', 'RHL');
insert into keycode values ('comp', 'VisualStudio', 'VS');
insert into keycode values ('comp', 'gcc', 'GCC');

create table os (
    name  varchar(16),
    version varchar(16),
    code varchar(9) unique,
    primary key (name, version)
);

insert into os values ('Windows', '7', 'WIN7');
insert into os values ('Windows', '10', 'WIN10');
insert into os values ('Windows', '2012', 'WIN2012');
insert into os values ('CentOS', '5', 'CEN5');
insert into os values ('CentOS', '7', 'CEN7');
insert into os values ('Redhat', '7', 'RHL7');

create table compiler (
    name  varchar(16),
    version varchar(16),
    code varchar(9) unique,
    primary key (name, version)
);

insert into compiler values ('VS', '2015', '');
insert into compiler values ('gcc', '4.7', '');



create or replace function plcode(p text, n text) returns text as
	$$
	declare
		vcode text;
		sz int;
	begin
		begin
			select code into vcode from keycode where name=p;
		exception
		    when NO_DATA_FOUND then
				vcode = p;
		end;
		sz = 9 - length(vcode);
		return vcode||lpad(trim(regexp_replace(n, '\.', '', 'g')), sz, '0');
	end;
	$$ language plpgsql;

create or replace function mkcode(p text, n text) returns text as
	$$
	select code || lpad(trim(regexp_replace(n, '\.', '', 'g')), 6, '0') as code
	from keycode
	where type=$1;
	$$ language sql;


create or replace function getcode(p text) returns table(code varchar(9)) as
	$$
	select mkcode('os', p, version) as code from os where name=p;
	$$ language sql;

mkcode('os', 'Windows', '7.2.5')