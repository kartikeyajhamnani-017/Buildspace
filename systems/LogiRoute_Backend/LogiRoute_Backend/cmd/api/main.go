package main

import (
	"context"
	"log"
	"logiroute/internal/config"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	
)

func main(){
	cfg, cfgerror := config.LoadConfig()
	if cfgerror != nil {
		log.Fatalf("Failed to load config: %v", cfgerror)
	}

	client, db, err := config.ConnectDB(cfg)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}

	defer func(){
		ctx, cancel:=  context.WithTimeout(context.Background(),5*time.Second)
		defer cancel()
		if err:= client.Disconnect(ctx); err != nil {
			log.Fatal("Failed to disconnect MongoDB client: %v", err)
		}
	}()

	router := gin.Default()

	router.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{"status": "operational", "timestamp": time.Now().Format(time.RFC3339), "database": db.Name()})

	})

	log.Printf("Starting server on port %s", cfg.Port)
	if err := router.Run(":" + cfg.Port); err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}