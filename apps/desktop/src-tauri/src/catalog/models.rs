use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
pub struct Organization {
    pub id: i64,
    pub display_name: String,
    pub handbook_root_id: Option<i64>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct Project {
    pub id: i64,
    pub organization_id: Option<i64>,
    pub display_name: String,
    pub source_path: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct DocumentationRoot {
    pub id: i64,
    pub project_id: i64,
    pub display_name: String,
    pub relative_path: String,
    pub initial_document_path: Option<String>,
    pub position: i64,
}
