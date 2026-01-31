import ollama

database_schema = """
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



    CREATE TABLE IF NOT EXISTS public.nation
    (
        n_nationkey integer,
        n_name character varying(50) COLLATE pg_catalog."default",
        n_regionkey integer,
        n_comment character varying(128) COLLATE pg_catalog."default"
    )



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



    CREATE TABLE IF NOT EXISTS public.part
    (
        p_partkey integer,
        p_type character varying(50) COLLATE pg_catalog."default",
        p_size integer,
        p_brand character varying(50) COLLATE pg_catalog."default",
        p_name character varying(50) COLLATE pg_catalog."default",
        p_container character varying(50) COLLATE pg_catalog."default",
        p_mfgr character varying(50) COLLATE pg_catalog."default",
        p_retailprice real,
        p_comment character varying(50) COLLATE pg_catalog."default"
    )



    CREATE TABLE IF NOT EXISTS public.partsupp
    (
        ps_partkey integer,
        ps_suppkey integer,
        ps_supplycost real,
        ps_availqty integer,
        ps_comment character varying(256) COLLATE pg_catalog."default"
    )

    CREATE TABLE IF NOT EXISTS public.region
    (
        r_regionkey integer,
        r_name character varying(50) COLLATE pg_catalog."default",
        r_comment character varying(128) COLLATE pg_catalog."default"
    )



    CREATE TABLE IF NOT EXISTS public.supplier
    (
        s_suppkey integer,
        s_nationkey integer,
        s_comment character varying(128) COLLATE pg_catalog."default",
        s_name character varying(50) COLLATE pg_catalog."default",
        s_address character varying(50) COLLATE pg_catalog."default",
        s_phone character varying(50) COLLATE pg_catalog."default",
        s_acctbal real
    )
"""

def generate_questions(database_schema):
    prompt_template = f"""
    ### INSTRUCTION
    You have the schema of a database below and you must generate three complex questions based on it.
    The questions should require joining multiple tables, aggregations, and filtering conditions to answer.

    Rules:
    1. Respond ONLY with the questions. Do not explain anything.
        
    ### DATABASE SCHEMA
    {database_schema}
   

    """
    response = ollama.chat(model='gemma3', messages=[
        {'role': 'user', 'content': prompt_template},
    ])

    return response['message']['content'].strip()

# questions = generate_questions()
# print("-" * 20)
# print(f"Questions: {questions}")
# print("-" * 20)

question_1 = "List the names of all customers who placed orders with a total price greater than $10000 and whose orders were shipped in the month of January, grouped by the customer's nation."
question_2 = "Calculate the total quantity of parts sold in each region, excluding regions where the number of distinct part types is less than 3."
question_3 = "Find the average discount percentage for line items associated with customers from the 'West' region who have a credit balance greater than $50000, ordered by the ship date in descending order."

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


question_1 = "I want to know how many customers I have in each country and order the results to display the countries with the most customers first."

sql_generated_1 = generate_sql(question_1, database_schema)

print("-" * 20)
print(f"Question 1: {question_1}")
print("-" * 20)
print(f"SQL 1:\n{sql_generated_1}")
print("-" * 20)

sql_generated_2 = generate_sql(question_2, database_schema)

print("-" * 20)
print(f"Question 2: {question_2}")
print("-" * 20)
print(f"SQL 2:\n{sql_generated_2}")
print("-" * 20)

sql_generated_3 = generate_sql(question_3, database_schema)

print("-" * 20)
print(f"Question 3: {question_3}")
print("-" * 20)
print(f"SQL 3:\n{sql_generated_3}")
print("-" * 20)