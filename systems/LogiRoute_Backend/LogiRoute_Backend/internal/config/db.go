package config

import(
	"context"
	"fmt"
	"log"
	"time"
	"go.mongodb.org/mongo-driver/v2/mongo"
	"go.mongodb.org/mongo-driver/v2/mongo/options"
)

func ConnectDB(cfg *Config) (*mongo.Client, *mongo.Database, error) {

	clientOptions := options.Client().ApplyURI(cfg.MongoURI)
	client, err := mongo.Connect( clientOptions)
	
	if err != nil {
      return nil, nil, fmt.Errorf("failed to initialize mongo client: %w", err)
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	err = client.Ping(ctx, nil)
	if err != nil {
		_= client.Disconnect(context.Background())
		return nil, nil, fmt.Errorf("failed to connect to MongoDB: %w", err)
	}
	log.Println("Connected to MongoDB successfully")
	return client, client.Database(cfg.DbName), nil
}