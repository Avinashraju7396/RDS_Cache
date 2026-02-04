import pymysql
import redis
import json
import sys

# Redis config
redis_client = redis.Redis(
    host='test-63iddn.serverless.use1.cache.amazonaws.com:6379',         #edit this casha endpoint
    port=6379,
    ssl=True,  # Set to True for ElastiCache with TLS
    decode_responses=True,
    socket_timeout=5
)

# RDS config
RDS_HOST = 'database-1.c8zywq2ccoms.us-east-1.rds.amazonaws.com'             # edit rds endpoint 
RDS_USER = 'admin'
RDS_PASSWORD = 'avinash1234'                                                   #edit password 
RDS_DB_NAME = 'avi'                                                            #edit db password
TABLE_NAME = 'users'                                                             #edit rds table name

def fetch_data_from_rds():
    try:
        connection = pymysql.connect(
            host=RDS_HOST,
            user=RDS_USER,
            password=RDS_PASSWORD,
            database=RDS_DB_NAME
        )
        print("🔗 Connected to RDS")

        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {TABLE_NAME} LIMIT 10;")
            rows = cursor.fetchall()
            return rows

    except Exception as e:
        print("❌ RDS Error:", e)
        return None

    finally:
        if 'connection' in locals():
            connection.close()

def main():
    cache_key = 'cached_table_data'
    bypass_cache = "--refresh" in sys.argv

    if not bypass_cache:
        cached_data = redis_client.get(cache_key)
        if cached_data:
            print("✅ Fetched from Redis cache:")
            print(json.loads(cached_data))
            return

    print("⚙️ No cache found or refresh requested. Fetching from RDS...")
    data = fetch_data_from_rds()
    if data:
        redis_client.set(cache_key, json.dumps(data), ex=90)
        print("📦 Cached in Redis:")
        print(data)
    else:
        print("⚠️ No data fetched from RDS.")

if __name__ == "__main__":
    main()
