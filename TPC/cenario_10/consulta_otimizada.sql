select
	c.c_custkey,
	c.c_name,
	sum(l.l_extendedprice * (1 - l.l_discount)) as revenue,
	c.c_acctbal,
	n.n_name,
	c.c_address,
	c.c_phone,
	c.c_comment
from
	customer c
inner join orders o on c.c_custkey = o.o_custkey
inner join lineitem l on o.o_orderkey = l.l_orderkey
inner join nation n on c.c_nationkey = n.n_nationkey
where
	o.o_orderdate >= date '1993-10-01'
	and o.o_orderdate < date '1994-01-01'
	and l.l_returnflag = 'R'
group by
	c.c_custkey,
	c.c_name,
	c.c_acctbal,
	c.c_phone,
	n.n_name,
	c.c_address,
	c.c_comment
order by
	revenue desc
limit 20;