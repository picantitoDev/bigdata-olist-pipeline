from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, DoubleType, StringType, TimestampType

ENTORNO = "gcp"

LOCAL_RAW_PATH       = "./data/olist_raw"
LOCAL_PROCESSED_PATH = "./data/olist_processed"
GCS_RAW_BUCKET       = "gs://gbucket-495719-raw-prod"
GCS_PROCESSED_BUCKET = "gs://gbucket-495719-processed-prod"

if ENTORNO == "local":
    spark = (
        SparkSession.builder
        .appName("OlistPreprocesamiento-Local")
        .master("local[*]")
        .config("spark.driver.memory", "4g")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    RAW_BASE       = LOCAL_RAW_PATH
    PROCESSED_BASE = LOCAL_PROCESSED_PATH
else:
    spark = SparkSession.builder.appName("OlistPreprocesamiento-GCP").getOrCreate()
    RAW_BASE       = f"{GCS_RAW_BUCKET}/brazilian_ecommerce"
    PROCESSED_BASE = f"{GCS_PROCESSED_BUCKET}/olist"


def leer_tabla(nombre_carpeta: str):
    ruta = f"{RAW_BASE}/{nombre_carpeta}/"
    return spark.read.parquet(ruta)

def columnas_negocio(df):
    cols_utiles = [c for c in df.columns if not c.startswith("_dlt")]
    return df.select(cols_utiles)


df_orders     = columnas_negocio(leer_tabla("orders"))
df_items      = columnas_negocio(leer_tabla("order_items"))
df_payments   = columnas_negocio(leer_tabla("order_payments"))
df_reviews    = columnas_negocio(leer_tabla("order_reviews"))
df_customers  = columnas_negocio(leer_tabla("customers"))
df_sellers    = columnas_negocio(leer_tabla("sellers"))
df_products   = columnas_negocio(leer_tabla("products"))
df_geo        = columnas_negocio(leer_tabla("geolocation"))
df_categories = columnas_negocio(leer_tabla("product_category_name_translation"))


def preprocess_orders(df):
    return (
        df
        .withColumn("order_purchase_timestamp",      F.to_timestamp("order_purchase_timestamp"))
        .withColumn("order_approved_at",             F.to_timestamp("order_approved_at"))
        .withColumn("order_delivered_carrier_date",  F.to_timestamp("order_delivered_carrier_date"))
        .withColumn("order_delivered_customer_date", F.to_timestamp("order_delivered_customer_date"))
        .withColumn("order_estimated_delivery_date", F.to_timestamp("order_estimated_delivery_date"))
        .withColumn("order_id",                      F.lower(F.col("order_id")))
        .withColumn("customer_id",                   F.lower(F.col("customer_id")))
        .withColumn("order_status",                  F.trim(F.lower(F.col("order_status"))))
        .withColumn("order_purchase_year_month",     F.date_format("order_purchase_timestamp", "yyyy-MM"))
        .withColumn("processed_at",                  F.current_timestamp())
    )

def preprocess_order_items(df):
    return (
        df
        .withColumn("order_id",            F.lower(F.col("order_id")))
        .withColumn("product_id",          F.lower(F.col("product_id")))
        .withColumn("seller_id",           F.lower(F.col("seller_id")))
        .withColumn("order_item_id",       F.col("order_item_id").cast(IntegerType()))
        .withColumn("shipping_limit_date", F.to_timestamp("shipping_limit_date"))
        .withColumn("price",               F.col("price").cast(DoubleType()))
        .withColumn("freight_value",       F.col("freight_value").cast(DoubleType()))
        .withColumn("processed_at",        F.current_timestamp())
    )

def preprocess_payments(df):
    return (
        df
        .withColumn("order_id",             F.lower(F.col("order_id")))
        .withColumn("payment_type",         F.trim(F.lower(F.col("payment_type"))))
        .withColumn("payment_sequential",   F.col("payment_sequential").cast(IntegerType()))
        .withColumn("payment_installments", F.col("payment_installments").cast(IntegerType()))
        .withColumn("payment_value",        F.col("payment_value").cast(DoubleType()))
        .withColumn("processed_at",         F.current_timestamp())
    )

def preprocess_reviews(df):
    return (
        df
        .withColumn("review_id",               F.lower(F.col("review_id")))
        .withColumn("order_id",                F.lower(F.col("order_id")))
        .withColumn("review_score",            F.col("review_score").cast(IntegerType()))
        .withColumn("review_creation_date",    F.to_timestamp("review_creation_date"))
        .withColumn("review_answer_timestamp", F.to_timestamp("review_answer_timestamp"))
        .withColumn("review_comment_title",    F.trim(F.col("review_comment_title")))
        .withColumn("review_comment_message",  F.trim(F.col("review_comment_message")))
        .withColumn("review_year_month",       F.date_format("review_creation_date", "yyyy-MM"))
        .withColumn("processed_at",            F.current_timestamp())
    )

def preprocess_customers(df):
    return (
        df
        .withColumn("customer_id",              F.lower(F.col("customer_id")))
        .withColumn("customer_unique_id",       F.lower(F.col("customer_unique_id")))
        .withColumn("customer_zip_code_prefix", F.lpad(F.col("customer_zip_code_prefix").cast(StringType()), 5, "0"))
        .withColumn("customer_city",            F.trim(F.lower(F.col("customer_city"))))
        .withColumn("customer_state",           F.upper(F.trim(F.col("customer_state"))))
        .withColumn("processed_at",             F.current_timestamp())
    )

def preprocess_sellers(df):
    return (
        df
        .withColumn("seller_id",              F.lower(F.col("seller_id")))
        .withColumn("seller_zip_code_prefix", F.lpad(F.col("seller_zip_code_prefix").cast(StringType()), 5, "0"))
        .withColumn("seller_city",            F.trim(F.lower(F.col("seller_city"))))
        .withColumn("seller_state",           F.upper(F.trim(F.col("seller_state"))))
        .withColumn("processed_at",           F.current_timestamp())
    )

def preprocess_products(df):
    return (
        df
        .withColumn("product_id",                 F.lower(F.col("product_id")))
        .withColumn("product_category_name",      F.trim(F.col("product_category_name")))
        .withColumn("product_name_lenght",        F.col("product_name_lenght").cast(IntegerType()))
        .withColumn("product_description_lenght", F.col("product_description_lenght").cast(IntegerType()))
        .withColumn("product_photos_qty",         F.col("product_photos_qty").cast(IntegerType()))
        .withColumn("product_weight_g",           F.col("product_weight_g").cast(IntegerType()))
        .withColumn("product_length_cm",          F.col("product_length_cm").cast(IntegerType()))
        .withColumn("product_height_cm",          F.col("product_height_cm").cast(IntegerType()))
        .withColumn("product_width_cm",           F.col("product_width_cm").cast(IntegerType()))
        .withColumn("processed_at",               F.current_timestamp())
    )

def preprocess_geolocation(df):
    return (
        df
        .withColumn("geolocation_zip_code_prefix", F.lpad(F.col("geolocation_zip_code_prefix").cast(StringType()), 5, "0"))
        .withColumn("geolocation_lat",             F.col("geolocation_lat").cast(DoubleType()))
        .withColumn("geolocation_lng",             F.col("geolocation_lng").cast(DoubleType()))
        .withColumn("geolocation_city",            F.trim(F.lower(F.col("geolocation_city"))))
        .withColumn("geolocation_state",           F.upper(F.trim(F.col("geolocation_state"))))
        .groupBy("geolocation_zip_code_prefix", "geolocation_city", "geolocation_state")
        .agg(
            F.round(F.avg("geolocation_lat"), 6).alias("geolocation_lat"),
            F.round(F.avg("geolocation_lng"), 6).alias("geolocation_lng"),
        )
        .withColumn("processed_at", F.current_timestamp())
    )

def preprocess_categories(df):
    return (
        df
        .withColumn("product_category_name",         F.trim(F.col("product_category_name")))
        .withColumn("product_category_name_english", F.trim(F.col("product_category_name_english")))
        .withColumn("processed_at",                  F.current_timestamp())
    )


df_orders_p     = preprocess_orders(df_orders)
df_items_p      = preprocess_order_items(df_items)
df_payments_p   = preprocess_payments(df_payments)
df_reviews_p    = preprocess_reviews(df_reviews)
df_customers_p  = preprocess_customers(df_customers)
df_sellers_p    = preprocess_sellers(df_sellers)
df_products_p   = preprocess_products(df_products)
df_geo_p        = preprocess_geolocation(df_geo)
df_categories_p = preprocess_categories(df_categories)


def escribir_processed(df, nombre_tabla: str, particion: str = None):
    ruta = f"{PROCESSED_BASE}/{nombre_tabla}/"
    writer = df.write.mode("overwrite").option("compression", "snappy")
    if particion:
        writer = writer.partitionBy(particion)
    writer.parquet(ruta)


escribir_processed(df_orders_p,     "orders",                            particion="order_purchase_year_month")
escribir_processed(df_items_p,      "order_items")
escribir_processed(df_payments_p,   "order_payments")
escribir_processed(df_reviews_p,    "order_reviews",                     particion="review_year_month")
escribir_processed(df_customers_p,  "customers")
escribir_processed(df_sellers_p,    "sellers")
escribir_processed(df_products_p,   "products")
escribir_processed(df_geo_p,        "geolocation",                       particion="geolocation_state")
escribir_processed(df_categories_p, "product_category_name_translation")