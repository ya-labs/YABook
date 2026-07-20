use serde::Serialize;

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct AppStatus {
    name: String,
    version: String,
}

#[tauri::command]
fn get_app_status() -> AppStatus {
    AppStatus {
        name: "YABook Desktop".into(),
        version: env!("CARGO_PKG_VERSION").into(),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![get_app_status])
        .run(tauri::generate_context!())
        .expect("error while running YABook Desktop");
}
