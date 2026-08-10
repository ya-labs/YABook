use std::{fs, path::{Path, PathBuf}};

use tauri::State;

use super::{
    models::{
        CreateOrganizationInput, CreateProjectInput, DocumentationRoot, DocumentationRootDraft,
        DocumentContent, DocumentTreeEntry, Organization, Project,
    },
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

#[tauri::command]
pub fn discover_documentation_roots(
    project_id: i64,
    catalog: State<'_, CatalogDatabase>,
) -> Result<Vec<DocumentationRoot>, String> {
    let project = catalog
        .project(project_id)
        .map_err(|error| format!("Não foi possível consultar o projeto: {error}"))?
        .ok_or_else(|| "O projeto selecionado não existe mais.".to_string())?;
    let roots = discover_root_drafts(Path::new(&project.source_path))?;

    catalog
        .replace_documentation_roots(project.id, &roots)
        .map_err(|error| format!("Não foi possível registrar as raízes documentais: {error}"))
}

#[tauri::command]
pub fn list_document_tree(
    root_id: i64,
    catalog: State<'_, CatalogDatabase>,
) -> Result<Vec<DocumentTreeEntry>, String> {
    let root = catalog.documentation_root(root_id)
        .map_err(|error| format!("Não foi possível consultar a raiz documental: {error}"))?
        .ok_or_else(|| "A raiz documental selecionada não existe mais.".to_string())?;
    let project = catalog.project(root.project_id)
        .map_err(|error| format!("Não foi possível consultar o projeto: {error}"))?
        .ok_or_else(|| "O projeto da raiz documental não existe mais.".to_string())?;
    let base = accessible_root(Path::new(&project.source_path), &root.relative_path)?;

    read_tree(&base, &base)
}

#[tauri::command]
pub fn read_document(
    root_id: i64,
    relative_path: String,
    catalog: State<'_, CatalogDatabase>,
) -> Result<DocumentContent, String> {
    let root = catalog.documentation_root(root_id)
        .map_err(|error| format!("Não foi possível consultar a raiz documental: {error}"))?
        .ok_or_else(|| "A raiz documental selecionada não existe mais.".to_string())?;
    let project = catalog.project(root.project_id)
        .map_err(|error| format!("Não foi possível consultar o projeto: {error}"))?
        .ok_or_else(|| "O projeto da raiz documental não existe mais.".to_string())?;
    let base = accessible_root(Path::new(&project.source_path), &root.relative_path)?;
    let path = resolve_document(&base, &relative_path)?;
    let content = fs::read_to_string(&path)
        .map_err(|_| "O documento não está mais disponível ou não pôde ser lido.".to_string())?;

    Ok(DocumentContent {
        project_id: project.id,
        root_id,
        relative_path: relative_path.replace('\\', "/"),
        absolute_path: path.to_string_lossy().into_owned(),
        content,
    })
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

fn discover_root_drafts(source_path: &Path) -> Result<Vec<DocumentationRootDraft>, String> {
    if !source_path.is_dir() {
        return Err("A fonte do projeto não existe mais ou não está acessível.".into());
    }

    let mut roots = Vec::new();
    let readme_path = source_path.join("README.md");

    if readme_path.is_file() {
        roots.push(DocumentationRootDraft {
            display_name: "Início".into(),
            relative_path: ".".into(),
            initial_document_path: Some("README.md".into()),
            position: 0,
        });
    }

    let docs_path = source_path.join("docs");

    if docs_path.is_dir() {
        roots.push(DocumentationRootDraft {
            display_name: "Documentação".into(),
            relative_path: "docs".into(),
            initial_document_path: docs_path
                .join("README.md")
                .is_file()
                .then(|| "README.md".into()),
            position: 10,
        });
    }

    Ok(roots)
}

fn accessible_root(source_path: &Path, relative_path: &str) -> Result<PathBuf, String> {
    let source = fs::canonicalize(source_path)
        .map_err(|_| "A fonte do projeto não existe mais ou não está acessível.".to_string())?;
    let root = fs::canonicalize(source.join(relative_path))
        .map_err(|_| "A raiz documental não está mais disponível.".to_string())?;
    if !root.is_dir() || !root.starts_with(&source) {
        return Err("A raiz documental não está acessível com segurança.".into());
    }
    Ok(root)
}

fn resolve_document(base: &Path, relative_path: &str) -> Result<PathBuf, String> {
    let requested = Path::new(relative_path);
    if requested.is_absolute() || requested.components().any(|part| matches!(part, std::path::Component::ParentDir)) {
        return Err("O caminho do documento é inválido.".into());
    }
    let path = fs::canonicalize(base.join(requested))
        .map_err(|_| "O documento não está mais disponível.".to_string())?;
    if !path.is_file() || !path.starts_with(base) || path.extension().and_then(|item| item.to_str()) != Some("md") {
        return Err("O item selecionado não é um documento Markdown disponível nesta raiz.".into());
    }
    Ok(path)
}

fn read_tree(base: &Path, current: &Path) -> Result<Vec<DocumentTreeEntry>, String> {
    let mut entries = fs::read_dir(current)
        .map_err(|_| "A raiz documental não está mais disponível.".to_string())?
        .filter_map(Result::ok)
        .filter_map(|entry| {
            let path = entry.path();
            let metadata = entry.metadata().ok()?;
            if metadata.is_dir() || path.extension().and_then(|item| item.to_str()) == Some("md") { Some((entry, metadata.is_dir())) } else { None }
        })
        .collect::<Vec<_>>();
    entries.sort_by_key(|(entry, is_directory)| (!is_directory, entry.file_name().to_string_lossy().to_lowercase()));
    entries.into_iter().map(|(entry, is_directory)| {
        let path = entry.path();
        let relative = path.strip_prefix(base).map_err(|_| "Não foi possível montar a árvore documental.".to_string())?
            .to_string_lossy().replace('\\', "/");
        Ok(DocumentTreeEntry { path: relative, name: entry.file_name().to_string_lossy().into_owned(), is_directory, children: if is_directory { read_tree(base, &path)? } else { Vec::new() } })
    }).collect()
}

#[cfg(test)]
mod tests {
    use std::{
        fs::{self, File},
        time::{SystemTime, UNIX_EPOCH},
    };

    use super::{discover_root_drafts, required_name};

    #[test]
    fn rejects_an_empty_display_name() {
        assert!(required_name("   ", "O nome do projeto").is_err());
    }

    #[test]
    fn discovers_the_project_readme_and_docs_directory() {
        let path = std::env::temp_dir().join(format!(
            "yabook-discovery-{}",
            SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .expect("lê relógio")
                .as_nanos()
        ));
        fs::create_dir_all(path.join("docs")).expect("cria diretório de teste");
        File::create(path.join("README.md")).expect("cria readme do projeto");
        File::create(path.join("docs/README.md")).expect("cria readme da documentação");

        let roots = discover_root_drafts(&path).expect("descobre raízes");

        assert_eq!(roots.len(), 2);
        assert_eq!(roots[0].relative_path, ".");
        assert_eq!(roots[0].initial_document_path.as_deref(), Some("README.md"));
        assert_eq!(roots[1].relative_path, "docs");
        assert_eq!(roots[1].initial_document_path.as_deref(), Some("README.md"));

        fs::remove_dir_all(path).expect("remove diretório de teste");
    }
}
