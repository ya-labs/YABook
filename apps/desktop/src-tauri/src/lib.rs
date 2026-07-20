pub mod catalog;

use tauri::Manager;

use catalog::{
    create_organization, create_project, list_organizations, list_projects, CatalogDatabase,
};
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
        .setup(|app| {
            let app_data_dir = app.path().app_data_dir()?;
            std::fs::create_dir_all(&app_data_dir)?;

            app.manage(CatalogDatabase::open(app_data_dir.join("catalog.sqlite3"))?);

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_app_status,
            create_organization,
            list_organizations,
            create_project,
            list_projects
        ])
        .run(tauri::generate_context!())
        .expect("error while running YABook Desktop");
}
