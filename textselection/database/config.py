import os

# Fetch database credentials from environment variables
DATABASE_USER = os.getenv("DATABASE_USER","supertokens_user")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD","supertokens123")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")  # default to localhost if not set
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")         # default to 5432 if not set
DATABASE_NAME = os.getenv("DATABASE_NAME","supertokens")

# print(f"User: {DATABASE_USER}")
# print(f"Password: {DATABASE_PASSWORD}")
# print(f"Host: {DATABASE_HOST}")
# print(f"Port: {DATABASE_PORT}")
# print(f"Database Name: {DATABASE_NAME}")

# Construct the DATABASE_URL
DRIVER = 'postgresql+psycopg2'
DATABASE_URL = f"{DRIVER}://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
print(DATABASE_URL)
