import ollama

def generate_sql(user_question, database_schema):
    prompt_template = f"""
    ### INSTRUCTION
    You are a SQL expert.
    Your task is to generate a valid SQL query based SOLELY on the provided database schema.
        
    Rules:
    1. Respond ONLY with the SQL code. Do not explain anything.
    2. Use standard SQL syntax.
    
    ### DATABASE SCHEMA
    {database_schema}

    ### USER QUESTION
    {user_question}

    """
    response = ollama.chat(model='gemma3', messages=[
        {'role': 'user', 'content': prompt_template},
    ])

    return response['message']['content'].strip()

# QUESTION 1

my_schema_1 = """
CREATE TABLE IF NOT EXISTS public.customer
(
    c_custkey integer,
    c_mktsegment character varying(50) COLLATE pg_catalog."default",
    c_nationkey integer,
    c_name character varying(50) COLLATE pg_catalog."default",
    c_address character varying(50) COLLATE pg_catalog."default",
    c_phone character varying(50) COLLATE pg_catalog."default",
    c_acctbal real,
    c_comment character varying(128) COLLATE pg_catalog."default"
)

CREATE TABLE IF NOT EXISTS public.nation
(
    n_nationkey integer,
    n_name character varying(50) COLLATE pg_catalog."default",
    n_regionkey integer,
    n_comment character varying(128) COLLATE pg_catalog."default"
)

"""

question_1 = "I want to know how many customers I have in each country and order the results to display the countries with the most customers first."

sql_generated_1 = generate_sql(question_1, my_schema_1)

print("-" * 20)
print(f"Question 1: {question_1}")
print("-" * 20)
print(f"SQL 1:\n{sql_generated_1}")
print("-" * 20)

# QUESTION 2

my_schema_2 = """
CREATE TABLE IF NOT EXISTS public.orders
(
    o_orderdate character varying(50) COLLATE pg_catalog."default",
    o_orderkey integer,
    o_custkey integer,
    o_orderpriority character varying(50) COLLATE pg_catalog."default",
    o_shippriority integer,
    o_clerk character varying(50) COLLATE pg_catalog."default",
    o_orderstatus character varying(50) COLLATE pg_catalog."default",
    o_totalprice real,
    o_comment character varying(128) COLLATE pg_catalog."default"
)

CREATE TABLE IF NOT EXISTS public.customer
(
    c_custkey integer,
    c_mktsegment character varying(50) COLLATE pg_catalog."default",
    c_nationkey integer,
    c_name character varying(50) COLLATE pg_catalog."default",
    c_address character varying(50) COLLATE pg_catalog."default",
    c_phone character varying(50) COLLATE pg_catalog."default",
    c_acctbal real,
    c_comment character varying(128) COLLATE pg_catalog."default"
)
"""

question_2 = "Which are the top 5 customers with the highest total order value?"

sql_generated_2 = generate_sql(question_2, my_schema_2)

print("-" * 20)
print(f"Question 2: {question_2}")
print("-" * 20)
print(f"SQL 2:\n{sql_generated_2}")
print("-" * 20)

# QUESTION 3

my_schema_3 = """
CREATE TABLE IF NOT EXISTS public.lineitem
(
    l_shipdate character varying(50) COLLATE pg_catalog."default",
    l_orderkey integer,
    l_discount real,
    l_extendedprice real,
    l_suppkey integer,
    l_quantity integer,
    l_returnflag character varying(50) COLLATE pg_catalog."default",
    l_partkey integer,
    l_linestatus character varying(50) COLLATE pg_catalog."default",
    l_tax real,
    l_commitdate character varying(50) COLLATE pg_catalog."default",
    l_receiptdate character varying(50) COLLATE pg_catalog."default",
    l_shipmode character varying(50) COLLATE pg_catalog."default",
    l_linenumber integer,
    l_shipinstruct character varying(50) COLLATE pg_catalog."default",
    l_comment character varying(50) COLLATE pg_catalog."default"
)

"""

question_3 = "Which are the most repeated ship instructions?"

sql_generated_3 = generate_sql(question_3, my_schema_3)

print("-" * 20)
print(f"Question 3: {question_3}")
print("-" * 20)
print(f"SQL 3:\n{sql_generated_3}")
print("-" * 20)