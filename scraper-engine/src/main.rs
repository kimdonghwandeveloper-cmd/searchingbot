use axum::{
    routing::{get, post},
    Router,
    Json,
};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;

// [Junior Dev Note]
// This struct defines the input data we expect from Python.
// Derive(Deserialize) automatically converts JSON -> Rust Struct.
#[derive(Deserialize)]
struct ScrapeRequest {
    url: String,
    selectors: serde_json::Value, // Dynamic JSON object for selectors
}

#[tokio::main]
async fn main() {
    // Initialize tracing (logging)
    tracing_subscriber::fmt::init();

    // Define routes
    let app = Router::new()
        .route("/", get(health_check))
        .route("/scrape", post(scrape_handler));

    // Address to listen on (0.0.0.0:3000)
    let addr = SocketAddr::from(([0, 0, 0, 0], 3000));
    println!("listening on {}", addr);
    
    // Start the server
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn health_check() -> &'static str {
    "Rust Scraper Engine is Ready!"
}

async fn scrape_handler(Json(payload): Json<ScrapeRequest>) -> Json<serde_json::Value> {
    // Placeholder logic for now
    println!("Received scrape request for: {}", payload.url);
    
    Json(serde_json::json!({
        "success": true,
        "message": "Scraping logic will be implemented here"
    }))
}
