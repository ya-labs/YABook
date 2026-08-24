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

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct DocumentationConfiguration {
    pub version: u32,
    pub project: Option<DocumentationProjectConfiguration>,
    pub documentation: DocumentationConfigurationSection,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct DocumentationProjectConfiguration {
    pub id: Option<String>,
    pub name: Option<String>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct DocumentationConfigurationSection {
    pub roots: Vec<DocumentationConfigurationRoot>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct DocumentationConfigurationRoot {
    pub id: String,
    pub label: Option<String>,
    pub path: String,
    pub entry: Option<String>,
    pub order: Option<i64>,
    #[serde(default)]
    pub overrides: Vec<DocumentationConfigurationOverride>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct DocumentationConfigurationOverride {
    pub path: String,
    pub label: Option<String>,
    pub order: Option<i64>,
    #[serde(default)]
    pub hidden: bool,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct DocumentationDiscovery {
    pub roots: Vec<DocumentationRoot>,
    pub configuration: Option<DocumentationConfiguration>,
    pub configuration_error: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct SaveDocumentationConfigurationInput {
    pub configuration: DocumentationConfiguration,
    pub confirmed: bool,
}

#[derive(Debug, Serialize)]
pub struct DocumentationConfigurationPreview {
    pub content: String,
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
