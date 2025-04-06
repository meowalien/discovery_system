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


# http:
#   host: "0.0.0.0"
#   port:  8001
#   log_level: "debug"
http = config.get("http", {})
port = int(http.get("port", 8001))
log_level = http.get("log_level", "debug")
host = http.get("host", "0.0.0.0")