use std::{
    fs,
    path::{Path, PathBuf},
};

use tauri::State;

use super::{
    models::{
        CreateOrganizationInput, CreateProjectInput, DocumentContent, DocumentTreeEntry,
        DocumentationConfiguration, DocumentationConfigurationOverride,
        DocumentationConfigurationPreview, DocumentationConfigurationRoot, DocumentationDiscovery,
        DocumentationRoot, DocumentationRootDraft, Organization, Project,
        SaveDocumentationConfigurationInput,
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
) -> Result<DocumentationDiscovery, String> {
    let project = catalog
        .project(project_id)
        .map_err(|error| format!("Não foi possível consultar o projeto: {error}"))?
        .ok_or_else(|| "O projeto selecionado não existe mais.".to_string())?;
    let source_path = Path::new(&project.source_path);
    let fallback_roots = discover_root_drafts(source_path)?;
    let (drafts, configuration, configuration_error) = match read_shared_configuration(source_path)
    {
        Ok(Some(configuration)) => match validate_configuration(source_path, &configuration) {
            Ok(()) => (
                configuration_root_drafts(&configuration),
                Some(configuration),
                None,
            ),
            Err(error) => (fallback_roots, None, Some(error)),
        },
        Ok(None) => (fallback_roots, None, None),
        Err(error) => (fallback_roots, None, Some(error)),
    };

    let roots = catalog
        .replace_documentation_roots(project.id, &drafts)
        .map_err(|error| format!("Não foi possível registrar as raízes documentais: {error}"))?;

    Ok(DocumentationDiscovery {
        roots,
        configuration,
        configuration_error,
    })
}

#[tauri::command]
pub fn list_document_tree(
    root_id: i64,
    catalog: State<'_, CatalogDatabase>,
) -> Result<Vec<DocumentTreeEntry>, String> {
    let root = catalog
        .documentation_root(root_id)
        .map_err(|error| format!("Não foi possível consultar a raiz documental: {error}"))?
        .ok_or_else(|| "A raiz documental selecionada não existe mais.".to_string())?;
    let project = catalog
        .project(root.project_id)
        .map_err(|error| format!("Não foi possível consultar o projeto: {error}"))?
        .ok_or_else(|| "O projeto da raiz documental não existe mais.".to_string())?;
    let base = accessible_root(Path::new(&project.source_path), &root.relative_path)?;

    let mut tree = read_tree(&base, &base)?;
    if let Ok(Some(configuration)) = read_shared_configuration(Path::new(&project.source_path)) {
        if validate_configuration(Path::new(&project.source_path), &configuration).is_ok() {
            if let Some(configured_root) = configuration.documentation.roots.iter().find(|item| {
                normalize_relative_path(&item.path) == normalize_relative_path(&root.relative_path)
            }) {
                apply_overrides(&mut tree, &configured_root.overrides);
            }
        }
    }
    Ok(tree)
}

#[tauri::command]
pub fn preview_documentation_configuration(
    project_id: i64,
    configuration: DocumentationConfiguration,
    catalog: State<'_, CatalogDatabase>,
) -> Result<DocumentationConfigurationPreview, String> {
    let project = project_for_configuration(project_id, &catalog)?;
    validate_configuration(Path::new(&project.source_path), &configuration)?;
    let content = serde_json::to_string_pretty(&configuration)
        .map_err(|error| format!("Não foi possível preparar a prévia da configuração: {error}"))?;
    Ok(DocumentationConfigurationPreview {
        content: format!("{content}\n"),
    })
}

#[tauri::command]
pub fn save_documentation_configuration(
    project_id: i64,
    input: SaveDocumentationConfigurationInput,
    catalog: State<'_, CatalogDatabase>,
) -> Result<(), String> {
    if !input.confirmed {
        return Err("Confirme a gravação antes de salvar a configuração compartilhada.".into());
    }
    let project = project_for_configuration(project_id, &catalog)?;
    let source_path = Path::new(&project.source_path);
    validate_configuration(source_path, &input.configuration)?;
    let content = serde_json::to_string_pretty(&input.configuration)
        .map_err(|error| format!("Não foi possível preparar a configuração: {error}"))?;
    let config_directory = source_path.join(".yabook");
    fs::create_dir_all(&config_directory)
        .map_err(|_| "Não foi possível criar o diretório .yabook.".to_string())?;
    fs::write(config_directory.join("config.json"), format!("{content}\n"))
        .map_err(|_| "Não foi possível salvar .yabook/config.json.".to_string())
}

#[tauri::command]
pub fn read_document(
    root_id: i64,
    relative_path: String,
    catalog: State<'_, CatalogDatabase>,
) -> Result<DocumentContent, String> {
    let root = catalog
        .documentation_root(root_id)
        .map_err(|error| format!("Não foi possível consultar a raiz documental: {error}"))?
        .ok_or_else(|| "A raiz documental selecionada não existe mais.".to_string())?;
    let project = catalog
        .project(root.project_id)
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

fn read_shared_configuration(
    source_path: &Path,
) -> Result<Option<DocumentationConfiguration>, String> {
    let config_path = source_path.join(".yabook").join("config.json");

    if !config_path.exists() {
        return Ok(None);
    }

    let content = fs::read_to_string(&config_path)
        .map_err(|_| "Não foi possível ler .yabook/config.json.".to_string())?;

    serde_json::from_str(&content)
        .map(Some)
        .map_err(|error| format!("A configuração compartilhada é inválida: {error}"))
}

fn project_for_configuration(
    project_id: i64,
    catalog: &State<'_, CatalogDatabase>,
) -> Result<Project, String> {
    catalog
        .project(project_id)
        .map_err(|error| format!("Não foi possível consultar o projeto: {error}"))?
        .ok_or_else(|| "O projeto selecionado não existe mais.".to_string())
}

fn configuration_root_drafts(
    configuration: &DocumentationConfiguration,
) -> Vec<DocumentationRootDraft> {
    let mut roots = configuration
        .documentation
        .roots
        .iter()
        .map(|root| DocumentationRootDraft {
            display_name: root.label.clone().unwrap_or_else(|| root.path.clone()),
            relative_path: normalize_relative_path(&root.path),
            initial_document_path: root.entry.clone(),
            position: root.order.unwrap_or(i64::MAX),
        })
        .collect::<Vec<_>>();
    roots.sort_by(|left, right| {
        left.position.cmp(&right.position).then_with(|| {
            left.display_name
                .to_lowercase()
                .cmp(&right.display_name.to_lowercase())
        })
    });
    roots
}

fn validate_configuration(
    source_path: &Path,
    configuration: &DocumentationConfiguration,
) -> Result<(), String> {
    if configuration.version != 1 {
        return Err("A versão da configuração precisa ser 1.".into());
    }

    let source = fs::canonicalize(source_path)
        .map_err(|_| "A fonte do projeto não existe mais ou não está acessível.".to_string())?;
    let mut root_ids = std::collections::HashSet::new();
    let mut root_paths = Vec::new();

    for root in &configuration.documentation.roots {
        if root.id.trim().is_empty() || !root_ids.insert(root.id.clone()) {
            return Err("Cada raiz precisa ter um identificador único e não vazio.".into());
        }
        let root_path = resolve_relative_path(&source, &root.path, "A raiz documental")?;
        if !root_path.is_dir() {
            return Err(format!(
                "A raiz documental '{}' não é um diretório.",
                root.path
            ));
        }
        if root_paths
            .iter()
            .any(|item: &PathBuf| root_path.starts_with(item) || item.starts_with(&root_path))
        {
            return Err("As raízes documentais não podem se sobrepor.".into());
        }
        if let Some(entry) = &root.entry {
            resolve_document(&root_path, entry).map_err(|_| {
                format!(
                    "O documento inicial de '{}' não existe ou é inválido.",
                    root.path
                )
            })?;
        }
        validate_overrides(&root_path, &root.overrides)?;
        root_paths.push(root_path);
    }
    Ok(())
}

fn validate_overrides(
    base: &Path,
    overrides: &[DocumentationConfigurationOverride],
) -> Result<(), String> {
    let mut paths = std::collections::HashSet::new();
    for item in overrides {
        let path = normalize_relative_path(&item.path);
        if path == "." || !paths.insert(path.clone()) {
            return Err(
                "Cada personalização precisa apontar para um caminho único abaixo da raiz.".into(),
            );
        }
        let resolved = resolve_relative_path(base, &path, "A personalização")?;
        if !resolved.is_dir()
            && (!resolved.is_file()
                || resolved.extension().and_then(|value| value.to_str()) != Some("md"))
        {
            return Err(format!(
                "A personalização '{}' não aponta para uma pasta ou Markdown existente.",
                item.path
            ));
        }
    }
    Ok(())
}

fn resolve_relative_path(
    base: &Path,
    relative_path: &str,
    subject: &str,
) -> Result<PathBuf, String> {
    let requested = Path::new(relative_path);
    if requested.is_absolute()
        || requested
            .components()
            .any(|part| matches!(part, std::path::Component::ParentDir))
    {
        return Err(format!(
            "{subject} precisa usar um caminho relativo dentro do projeto."
        ));
    }
    let path = fs::canonicalize(base.join(requested))
        .map_err(|_| format!("{subject} não está disponível."))?;
    if !path.starts_with(base) {
        return Err(format!("{subject} precisa permanecer dentro do projeto."));
    }
    Ok(path)
}

fn normalize_relative_path(path: &str) -> String {
    let normalized = path.replace('\\', "/").trim_matches('/').to_owned();
    if normalized.is_empty() {
        ".".into()
    } else {
        normalized
    }
}

fn apply_overrides(
    entries: &mut Vec<DocumentTreeEntry>,
    overrides: &[DocumentationConfigurationOverride],
) {
    entries.retain(|entry| {
        !overrides
            .iter()
            .any(|item| item.hidden && normalize_relative_path(&item.path) == entry.path)
    });
    for entry in entries.iter_mut() {
        if let Some(override_item) = overrides
            .iter()
            .find(|item| normalize_relative_path(&item.path) == entry.path)
        {
            if let Some(label) = &override_item.label {
                entry.name = label.clone();
            }
        }
        if entry.is_directory {
            apply_overrides(&mut entry.children, overrides);
        }
    }
    entries.sort_by(|left, right| {
        let position = |entry: &DocumentTreeEntry| {
            overrides
                .iter()
                .find(|item| normalize_relative_path(&item.path) == entry.path)
                .and_then(|item| item.order)
                .unwrap_or(i64::MAX)
        };
        position(left)
            .cmp(&position(right))
            .then_with(|| (!left.is_directory).cmp(&(!right.is_directory)))
            .then_with(|| left.name.to_lowercase().cmp(&right.name.to_lowercase()))
    });
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
    if requested.is_absolute()
        || requested
            .components()
            .any(|part| matches!(part, std::path::Component::ParentDir))
    {
        return Err("O caminho do documento é inválido.".into());
    }
    let path = fs::canonicalize(base.join(requested))
        .map_err(|_| "O documento não está mais disponível.".to_string())?;
    if !path.is_file()
        || !path.starts_with(base)
        || path.extension().and_then(|item| item.to_str()) != Some("md")
    {
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
            if metadata.is_dir() || path.extension().and_then(|item| item.to_str()) == Some("md") {
                Some((entry, metadata.is_dir()))
            } else {
                None
            }
        })
        .collect::<Vec<_>>();
    entries.sort_by_key(|(entry, is_directory)| {
        (
            !is_directory,
            entry.file_name().to_string_lossy().to_lowercase(),
        )
    });
    entries
        .into_iter()
        .map(|(entry, is_directory)| {
            let path = entry.path();
            let relative = path
                .strip_prefix(base)
                .map_err(|_| "Não foi possível montar a árvore documental.".to_string())?
                .to_string_lossy()
                .replace('\\', "/");
            Ok(DocumentTreeEntry {
                path: relative,
                name: entry.file_name().to_string_lossy().into_owned(),
                is_directory,
                children: if is_directory {
                    read_tree(base, &path)?
                } else {
                    Vec::new()
                },
            })
        })
        .collect()
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
