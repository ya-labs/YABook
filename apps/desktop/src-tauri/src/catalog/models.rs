use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Organization {
    pub id: i64,
    pub display_name: String,
    pub handbook_root_id: Option<i64>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct CreateOrganizationInput {
    pub display_name: String,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Project {
    pub id: i64,
    pub organization_id: Option<i64>,
    pub display_name: String,
    pub source_path: String,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct CreateProjectInput {
    pub organization_id: Option<i64>,
    pub display_name: String,
    pub source_path: String,
}

#[derive(Debug, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DocumentationRoot {
    pub id: i64,
    pub project_id: i64,
    pub display_name: String,
    pub relative_path: String,
    pub initial_document_path: Option<String>,
    pub position: i64,
}

pub struct DocumentationRootDraft {
    pub display_name: String,
    pub relative_path: String,
    pub initial_document_path: Option<String>,
    pub position: i64,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DocumentTreeEntry {
    pub path: String,
    pub name: String,
    pub is_directory: bool,
    pub children: Vec<DocumentTreeEntry>,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DocumentContent {
    pub project_id: i64,
    pub root_id: i64,
    pub relative_path: String,
    pub absolute_path: String,
    pub content: String,
}
