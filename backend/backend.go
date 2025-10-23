package main

import (
"database/sql"
"encoding/json"
"errors"
"fmt"
_ "github.com/lib/pq"
"gopkg.in/yaml.v3"
"log"
"net/http"
"os"
)

// User представляет структуру пользователя
type User struct {
ID   int    `json:"id"`
Name string `json:"name"`
Age  int    `json:"age"`
}

// Config представляет конфигурацию приложения
type Config struct {
Database struct {
Host     string `yaml:"host"`
Port     string `yaml:"port"`
User     string `yaml:"user"`
Password string `yaml:"password"`
Name     string `yaml:"dbname"`
SSLMode  string `yaml:"sslmode"`
} `yaml:"database"`
}

// App представляет основное приложение
type App struct {
DB *sql.DB
}

// loadConfig загружает конфигурацию из файла
func loadConfig(path string) (*Config, error) {
if path == "" {
return nil, errors.New("config path is empty")
}

data, err := os.ReadFile(path)
if err != nil {
return nil, fmt.Errorf("failed to read config file: %w", err)
}

var cfg Config
if err := yaml.Unmarshal(data, &cfg); err != nil {
return nil, fmt.Errorf("failed to parse config: %w", err)
}

return &cfg, nil
}

// getConfigPath возвращает путь к конфигурационному файлу
func getConfigPath() string {
path := os.Getenv("CONFIG_PATH")
if path == "" {
path = "/etc/backend-api/config.yaml"
}
return path
}

// buildDSN строит строку подключения к PostgreSQL
func buildDSN(cfg *Config) string {
// Читаем из окружения, если есть
dbHost := getEnv("DB_HOST", cfg.Database.Host)
dbPort := getEnv("DB_PORT", cfg.Database.Port)
dbUser := getEnv("DB_USER", cfg.Database.User)
dbPassword := getEnv("DB_PASSWORD", cfg.Database.Password)
dbName := getEnv("DB_NAME", cfg.Database.Name)
sslMode := getEnv("DB_SSLMODE", cfg.Database.SSLMode)

if sslMode == "" {
sslMode = "disable"
}

return fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
dbHost, dbPort, dbUser, dbPassword, dbName, sslMode)
}

// getEnv возвращает значение переменной окружения или значение по умолчанию
func getEnv(key, defaultValue string) string {
value := os.Getenv(key)
if value == "" {
return defaultValue
}
return value
}

// connectDB устанавливает соединение с базой данных
func connectDB(dsn string) (*sql.DB, error) {
db, err := sql.Open("postgres", dsn)
if err != nil {
return nil, fmt.Errorf("failed to connect to database: %w", err)
}

if err := db.Ping(); err != nil {
db.Close()
return nil, fmt.Errorf("database is not available: %w", err)
}

return db, nil
}

// getUserHandler обработчик запроса пользователя
func (app *App) getUserHandler(w http.ResponseWriter, r *http.Request) {
id := r.URL.Query().Get("id")
if id == "" {
http.Error(w, "id parameter is required", http.StatusBadRequest)
return
}

row := app.DB.QueryRow("SELECT id, name, age FROM users WHERE id = $1", id)
var user User
err := row.Scan(&user.ID, &user.Name, &user.Age)

if err != nil {
if errors.Is(err, sql.ErrNoRows) {
http.Error(w, "user not found", http.StatusNotFound)
} else {
log.Printf("error scanning user row: %v", err)
http.Error(w, "internal server error", http.StatusInternalServerError)
}
return
}

w.Header().Set("Content-Type", "application/json")
json.NewEncoder(w).Encode(user)
}

// startHTTPServer запускает HTTP сервер
func (app *App) startHTTPServer() error {
log.Println("Starting HTTP server on :8080")
return http.ListenAndServe(":8080", nil)
}

// runApp запускает приложение
func runApp() error {
configPath := getConfigPath()
log.Printf("Loading config from: %s", configPath)

cfg, err := loadConfig(configPath)
if err != nil {
return fmt.Errorf("failed to load config: %w", err)
}

dsn := buildDSN(cfg)
log.Printf("Connecting to database: %s", dsn)

db, err := connectDB(dsn)
if err != nil {
return fmt.Errorf("failed to connect to database: %w", err)
}
defer db.Close()

app := &App{DB: db}

http.HandleFunc("/user", app.getUserHandler)

	return app.startHTTPServer()
}

func main() {
if err := runApp(); err != nil {
log.Fatalf("Application failed: %v", err)
}
}
>>>>>>> REPLACE