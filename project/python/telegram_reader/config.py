import os
import yaml

# Get the configuration file path from an environment variable or default to 'config.yml'
CONFIG_FILE_PATH = os.getenv("CONFIG_FILE", "config.yml")

try:
    with open(CONFIG_FILE_PATH, "r") as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"Configuration file not found: {CONFIG_FILE_PATH}")

# Read Redis configuration from the config file, with default values as fallback
redis_config = config.get("redis", {})
REDIS_HOST = redis_config.get("host", "localhost")
REDIS_PORT = int(redis_config.get("port", 6379))
REDIS_DB = int(redis_config.get("db", 0))

# Read PostgreSQL configuration from the config file, with a default value as fallback
postgres_config = config.get("postgres", {})
POSTGRES_URL = postgres_config.get("url", "postgresql://postgres:postgres@localhost:5432/discovery_system")

http_config = config.get("http", {})
HTTP_PORT = int(http_config.get("port", 8001))


grpc_config = config.get("grpc", {})
GRPC_PORT = int(grpc_config.get("port", 50051))


keycloak_config = config.get("keycloak", {})
KEYCLOAK_OIDC_URL = keycloak_config.get("url", "http://localhost:8080")
KEYCLOAK_REALM = keycloak_config.get("realm", "discovery_system")
KEYCLOAK_CLIENT_ID = keycloak_config.get("client_id", "demo")
KEYCLOAK_DEMO_CLIENT_AUDIENCE = keycloak_config.get("demo_client_audience", "account")

# read SERVICE_NAME from environment variable or default to "auth-service"
SERVICE_NAME = os.getenv("SERVICE_NAME", "auth-service")

LOG_FILE_PATH = config.get("log_file_path",None)
if LOG_FILE_PATH is None:
    raise ValueError("LOG_FILE_PATH is not found in the configuration file.")


kafka_config = config.get("kafka", {})
KAFKA_BROKER_URLS = kafka_config.get("urls", None)
if KAFKA_BROKER_URLS is None:
    raise ValueError("KAFKA_BROKER_URLS is not found in the configuration file.")

HOSTNAME = os.getenv("HOSTNAME", "localhost")


LOG_LEVEL = config.get("log_level", "debug")