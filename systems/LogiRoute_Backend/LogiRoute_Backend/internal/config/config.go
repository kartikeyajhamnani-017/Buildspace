package config

import (
	"os"
)

type Config struct {
	Port string
	MongoURI string
	DbName string
	JWTsecret string
}

func LoadConfig() (*Config, error) {
	return &Config{
		Port: getEnv("PORT", "8080"),
		MongoURI: getEnv("MONGO_URI", "mongodb://localhost:27017"),
		DbName: getEnv("DB_NAME", "logiroute"),
		JWTsecret: getEnv("JWT_SECRET", "your_jwt_secret_key"),
	}, nil
}

func getEnv(key, defaultValue string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultValue
}