use axum::{
    routing::{get, post},
    Router,
    Json,
    http::StatusCode,
};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::net::SocketAddr;
use scraper::{Html, Selector};

// [Junior Dev Note]
// 요청 데이터 구조체입니다.
// Python의 pydantic 모델과 일치해야 합니다.
// JSON 키와 구조체 필드가 자동으로 매핑됩니다.
#[derive(Deserialize)]
struct ScrapeRequest {
    url: String,
    selectors: HashMap<String, String>, // 예: {"title": "#product-name"}
}

// [Junior Dev Note]
// 응답 데이터 구조체입니다.
#[derive(Serialize)]
struct ScrapeResponse {
    success: bool,
    data: HashMap<String, String>,
    error: Option<String>,
}

#[tokio::main]
async fn main() {
    // 로깅 초기화 (콘솔 출력용)
    tracing_subscriber::fmt::init();

    let app = Router::new()
        .route("/", get(health_check))
        .route("/scrape", post(scrape_handler));

    // 0.0.0.0으로 바인딩하여 외부(컨테이너/호스트)에서 접근 가능하게 설정
    let addr = SocketAddr::from(([0, 0, 0, 0], 3000));
    println!("Rust Scraper Engine listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn health_check() -> &'static str {
    "Rust Scraper is Ready"
}

// [Junior Dev Note]
// 핵심 핸들러 함수입니다.
// Json<ScrapeRequest>는 요청 바디를 자동으로 파싱해줍니다.
async fn scrape_handler(Json(payload): Json<ScrapeRequest>) -> (StatusCode, Json<ScrapeResponse>) {
    println!("Scraping URL: {}", payload.url);

    // 1. HTTP 요청 (Reqwest)
    // .await? 대신 match를 사용하여 에러를 명시적으로 처리합니다.
    let html_content = match fetch_url(&payload.url).await {
        Ok(content) => content,
        Err(e) => {
            return (
                StatusCode::BAD_REQUEST, // 또는 200 OK에 success: false를 담을 수도 있습니다.
                Json(ScrapeResponse {
                    success: false,
                    data: HashMap::new(),
                    error: Some(format!("Failed to fetch URL: {}", e)),
                }),
            );
        }
    };

    // 2. HTML 파싱 (Scraper)
    // CPU 집약적인 작업이므로 Rust의 성능이 빛을 발하는 구간입니다.
    let parsed_data = parse_html(&html_content, &payload.selectors);

    // 3. 결과 반환
    // 성공 시 200 OK와 함께 데이터를 보냅니다.
    (
        StatusCode::OK,
        Json(ScrapeResponse {
            success: true,
            data: parsed_data,
            error: None,
        }),
    )
}

// [Junior Dev Note: Async/Await & Result]
// 비동기 함수는 Future를 반환하며, 실행 시에는 .await가 필요합니다.
// Result<String, String>은 성공(Ok) 또는 실패(Err)를 담는 Rust의 표준 에러 처리 방식입니다.
async fn fetch_url(url: &str) -> Result<String, String> {
    // reqwest 클라이언트로 GET 요청
    let resp = reqwest::get(url)
        .await
        .map_err(|e| e.to_string())?; // 에러 발생 시 문자열로 변환하여 리턴

    // 상태 코드 확인
    if !resp.status().is_success() {
        return Err(format!("HTTP Status {}", resp.status()));
    }

    // 텍스트(HTML) 추출
    let text = resp.text().await.map_err(|e| e.to_string())?;
    Ok(text)
}

// [Junior Dev Note: Ownership & Borrowing]
// html: &str -> 문자열 전체를 복사하지 않고 참조(Reference)만 빌려옵니다(Borrowing). 메모리를 아낍니다.
// selectors: &HashMap -> 역시 참조만 빌려옵니다. 함수가 끝난 후에도 원본 데이터는 사라지지 않습니다.
fn parse_html(html: &str, selectors: &HashMap<String, String>) -> HashMap<String, String> {
    let document = Html::parse_document(html);
    let mut results = HashMap::new();

    for (key, selector_str) in selectors {
        // Selector 파싱 유효성 검사
        let selector = match Selector::parse(selector_str) {
            Ok(s) => s,
            Err(_) => {
                // 잘못된 선택자는 무시하거나 에러를 남길 수 있습니다. 여기선 에러 메시지를 값으로 넣습니다.
                results.insert(key.clone(), "Invalid CSS Selector".to_string());
                continue;
            }
        };

        // 문서에서 선택자로 요소 찾기
        // .next(): 첫 번째 요소만 가져옵니다. (단일 항목 추출)
        if let Some(element) = document.select(&selector).next() {
            // 텍스트 추출
            // collect::<Vec<_>>() 등으로 자식 노드 텍스트를 모을 수도 있습니다.
            let text = element.text().collect::<Vec<_>>().join(" ");
            results.insert(key.clone(), text.trim().to_string());
        } else {
            // 요소를 못 찾은 경우
            // 여기서 None이나 빈 문자열을 줄 수 있는데, Python 측에서 Fallback을 결정하기 위해선
            // 빈 문자열이 오면 Fallback을 하도록 로직을 짤 수 있습니다.
            results.insert(key.clone(), "".to_string());
        }
    }

    results
}
