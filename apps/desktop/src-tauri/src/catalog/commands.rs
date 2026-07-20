use std::path::Path;

use tauri::State;

use super::{
    models::{CreateOrganizationInput, CreateProjectInput, Organization, Project},
    CatalogDatabase,
};

#[tauri::command]
pub fn create_organization(
    input: CreateOrganizationInput,
    catalog: State<'_, CatalogDatabase>,
) -> Result<Organization, String> {
    let display_name = required_name(&input.display_name, "O nome da organização")?;

    catalog
        .create_organization(&display_name)
        .map_err(|error| format!("Não foi possível cadastrar a organização: {error}"))
}

#[tauri::command]
pub fn list_organizations(
    catalog: State<'_, CatalogDatabase>,
) -> Result<Vec<Organization>, String> {
    catalog
        .list_organizations()
        .map_err(|error| format!("Não foi possível consultar as organizações: {error}"))
}

#[tauri::command]
pub fn create_project(
    input: CreateProjectInput,
    catalog: State<'_, CatalogDatabase>,
) -> Result<Project, String> {
    let display_name = required_name(&input.display_name, "O nome do projeto")?;
    let source_path = canonical_directory(&input.source_path)?;

    if let Some(organization_id) = input.organization_id {
        let exists = catalog
            .organization_exists(organization_id)
            .map_err(|error| format!("Não foi possível validar a organização: {error}"))?;

        if !exists {
            return Err("A organização selecionada não existe mais.".into());
        }
    }

    catalog
        .create_project(input.organization_id, &display_name, &source_path)
        .map_err(|error| format!("Não foi possível cadastrar o projeto: {error}"))
}

#[tauri::command]
pub fn list_projects(catalog: State<'_, CatalogDatabase>) -> Result<Vec<Project>, String> {
    catalog
        .list_projects()
        .map_err(|error| format!("Não foi possível consultar os projetos: {error}"))
}

fn required_name(value: &str, subject: &str) -> Result<String, String> {
    let value = value.trim();

    if value.is_empty() {
        return Err(format!("{subject} é obrigatório."));
    }

    Ok(value.to_owned())
}

fn canonical_directory(value: &str) -> Result<String, String> {
    let path = std::fs::canonicalize(Path::new(value))
        .map_err(|_| "O diretório selecionado não existe ou não está acessível.".to_string())?;

    if !path.is_dir() {
        return Err("A fonte cadastrada precisa ser um diretório.".into());
    }

    path.to_str()
        .map(str::to_owned)
        .ok_or_else(|| "O caminho do projeto precisa usar UTF-8.".into())
}

#[cfg(test)]
mod tests {
    use super::required_name;

    #[test]
    fn rejects_an_empty_display_name() {
        assert!(required_name("   ", "O nome do projeto").is_err());
    }
}
