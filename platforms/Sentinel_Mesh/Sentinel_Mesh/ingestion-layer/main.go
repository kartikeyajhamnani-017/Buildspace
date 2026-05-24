package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	

	"github.com/redis/go-redis/v9"
)

var ctx = context.Background()
var redisClient *redis.Client

// LogEntry represents the data coming in from the network

type LogEntry struct {
	SourceIP    string `json:"source_ip"`
	Timestamp   string `json:"timestamp"`
	Payload     string `json:"payload"`
	RequestType string `json:"request_type"`
}

func initRedis() {
	redisClient = redis.NewClient(&redis.Options{
		Addr:     "localhost:6379", // Address of the Docker container
		Password: "",               // No password set
		DB:       0,                // Default DB
	})

	// Test the connection
	_, err := redisClient.Ping(ctx).Result()
	if err != nil {
		log.Fatalf("❌ Failed to connect to Redis: %v", err)
	}
	fmt.Println("✅ Connected to Redis!")
}

func handleLogIngestion(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var entry LogEntry
	if err := json.NewDecoder(r.Body).Decode(&entry); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	// Marshal struct back to JSON string for storage
	data, err := json.Marshal(entry)
	if err != nil {
		http.Error(w, "Error processing data", http.StatusInternalServerError)
		return
	}

	// PUSH to Redis Queue (RPush adds to the tail of the list)
	err = redisClient.RPush(ctx, "traffic_queue", data).Err()
	if err != nil {
		log.Printf("❌ Redis Error: %v", err)
		http.Error(w, "Queue Error", http.StatusInternalServerError)
		return
	}

	// Respond to client
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "queued_persistently"})
}

func main() {
	initRedis() // Initialize connection first

	http.HandleFunc("/ingest", handleLogIngestion)

	port := ":8080"
	fmt.Println("🛡️ Sentinel Shield Active (with Redis Buffer). Listening on port " + port)
	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatal(err)
	}
	/*docker run -d --name sentinel-redis -v sentinel-data:/data -p 6379:6379 redis:7-alpine redis-server --appendonly yes*/

}