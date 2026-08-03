use std::{
    path::Path,
    sync::{Mutex, MutexGuard},
};

use rusqlite::{params, Connection, OptionalExtension, Result};

use super::models::{DocumentationRoot, DocumentationRootDraft, Organization, Project};

pub struct CatalogDatabase {
    connection: Mutex<Connection>,
}

impl CatalogDatabase {
    pub fn open(path: impl AsRef<Path>) -> Result<Self> {
        let connection = Connection::open(path)?;

        connection.execute_batch(
            "
            PRAGMA foreign_keys = ON;
            PRAGMA journal_mode = WAL;
            ",
        )?;
        migrate(&connection)?;

        Ok(Self {
            connection: Mutex::new(connection),
        })
    }

    pub fn schema_version(&self) -> Result<u32> {
        let connection = self.connection();

        connection.pragma_query_value(None, "user_version", |row| row.get::<_, u32>(0))
    }

    pub fn create_organization(&self, display_name: &str) -> Result<Organization> {
        let connection = self.connection();

        connection.execute(
            "INSERT INTO organizations (display_name) VALUES (?1)",
            [display_name],
        )?;

        Ok(Organization {
            id: connection.last_insert_rowid(),
            display_name: display_name.into(),
            handbook_root_id: None,
        })
    }

    pub fn list_organizations(&self) -> Result<Vec<Organization>> {
        let connection = self.connection();
        let mut statement = connection.prepare(
            "
            SELECT id, display_name, handbook_root_id
            FROM organizations
            ORDER BY display_name COLLATE NOCASE, id
            ",
        )?;
        let organizations = statement
            .query_map([], |row| {
                Ok(Organization {
                    id: row.get(0)?,
                    display_name: row.get(1)?,
                    handbook_root_id: row.get(2)?,
                })
            })?
            .collect::<Result<Vec<_>>>()?;

        Ok(organizations)
    }

    pub fn organization_exists(&self, organization_id: i64) -> Result<bool> {
        let connection = self.connection();
        let id = connection
            .query_row(
                "SELECT id FROM organizations WHERE id = ?1",
                [organization_id],
                |row| row.get::<_, i64>(0),
            )
            .optional()?;

        Ok(id.is_some())
    }

    pub fn create_project(
        &self,
        organization_id: Option<i64>,
        display_name: &str,
        source_path: &str,
    ) -> Result<Project> {
        let connection = self.connection();

        connection.execute(
            "
            INSERT INTO projects (organization_id, display_name, source_path)
            VALUES (?1, ?2, ?3)
            ",
            params![organization_id, display_name, source_path],
        )?;

        Ok(Project {
            id: connection.last_insert_rowid(),
            organization_id,
            display_name: display_name.into(),
            source_path: source_path.into(),
        })
    }

    pub fn list_projects(&self) -> Result<Vec<Project>> {
        let connection = self.connection();
        let mut statement = connection.prepare(
            "
            SELECT id, organization_id, display_name, source_path
            FROM projects
            ORDER BY display_name COLLATE NOCASE, id
            ",
        )?;
        let projects = statement
            .query_map([], |row| {
                Ok(Project {
                    id: row.get(0)?,
                    organization_id: row.get(1)?,
                    display_name: row.get(2)?,
                    source_path: row.get(3)?,
                })
            })?
            .collect::<Result<Vec<_>>>()?;

        Ok(projects)
    }

    pub fn project(&self, project_id: i64) -> Result<Option<Project>> {
        let connection = self.connection();

        connection
            .query_row(
                "
                SELECT id, organization_id, display_name, source_path
                FROM projects
                WHERE id = ?1
                ",
                [project_id],
                |row| {
                    Ok(Project {
                        id: row.get(0)?,
                        organization_id: row.get(1)?,
                        display_name: row.get(2)?,
                        source_path: row.get(3)?,
                    })
                },
            )
            .optional()
    }

    pub fn replace_documentation_roots(
        &self,
        project_id: i64,
        roots: &[DocumentationRootDraft],
    ) -> Result<Vec<DocumentationRoot>> {
        let mut connection = self.connection();
        let transaction = connection.transaction()?;

        transaction.execute(
            "DELETE FROM documentation_roots WHERE project_id = ?1",
            [project_id],
        )?;

        for root in roots {
            transaction.execute(
                "
                INSERT INTO documentation_roots (
                    project_id,
                    display_name,
                    relative_path,
                    initial_document_path,
                    position
                )
                VALUES (?1, ?2, ?3, ?4, ?5)
                ",
                params![
                    project_id,
                    root.display_name,
                    root.relative_path,
                    root.initial_document_path,
                    root.position
                ],
            )?;
        }

        let mut statement = transaction.prepare(
            "
            SELECT id, project_id, display_name, relative_path, initial_document_path, position
            FROM documentation_roots
            WHERE project_id = ?1
            ORDER BY position, display_name COLLATE NOCASE, id
            ",
        )?;
        let roots = statement
            .query_map([project_id], |row| {
                Ok(DocumentationRoot {
                    id: row.get(0)?,
                    project_id: row.get(1)?,
                    display_name: row.get(2)?,
                    relative_path: row.get(3)?,
                    initial_document_path: row.get(4)?,
                    position: row.get(5)?,
                })
            })?
            .collect::<Result<Vec<_>>>()?;

        drop(statement);
        transaction.commit()?;

        Ok(roots)
    }

    fn connection(&self) -> MutexGuard<'_, Connection> {
        self.connection
            .lock()
            .expect("banco do catálogo disponível")
    }

    #[cfg(test)]
    fn open_in_memory() -> Result<Self> {
        let connection = Connection::open_in_memory()?;
        migrate(&connection)?;

        Ok(Self {
            connection: Mutex::new(connection),
        })
    }
}

fn migrate(connection: &Connection) -> Result<()> {
    let version =
        connection.pragma_query_value(None, "user_version", |row| row.get::<_, u32>(0))?;

    if version == 0 {
        connection.execute_batch(
            "
            BEGIN;

            CREATE TABLE organizations (
                id INTEGER PRIMARY KEY,
                display_name TEXT NOT NULL,
                handbook_root_id INTEGER REFERENCES documentation_roots(id) ON DELETE SET NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE projects (
                id INTEGER PRIMARY KEY,
                organization_id INTEGER REFERENCES organizations(id) ON DELETE SET NULL,
                display_name TEXT NOT NULL,
                source_path TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE documentation_roots (
                id INTEGER PRIMARY KEY,
                project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                display_name TEXT NOT NULL,
                relative_path TEXT NOT NULL,
                initial_document_path TEXT,
                position INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(project_id, relative_path)
            );

            CREATE TABLE preferences (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            PRAGMA user_version = 1;
            COMMIT;
            ",
        )?;
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use rusqlite::Connection;

    use super::{migrate, CatalogDatabase};

    #[test]
    fn creates_the_initial_catalog_schema() {
        let connection = Connection::open_in_memory().expect("abre banco em memória");

        migrate(&connection).expect("cria schema inicial");

        let version = connection
            .pragma_query_value(None, "user_version", |row| row.get::<_, u32>(0))
            .expect("lê versão do schema");
        let table_count: i64 = connection
            .query_row(
                "
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE type = 'table'
                  AND name IN ('organizations', 'projects', 'documentation_roots', 'preferences')
                ",
                [],
                |row| row.get(0),
            )
            .expect("consulta tabelas do catálogo");

        assert_eq!(version, 1);
        assert_eq!(table_count, 4);
    }

    #[test]
    fn persists_projects_with_or_without_an_organization() {
        let catalog = CatalogDatabase::open_in_memory().expect("abre catálogo em memória");
        let organization = catalog
            .create_organization("YA LABS")
            .expect("cria organização");

        let linked_project = catalog
            .create_project(Some(organization.id), "YABook", "/tmp/yabook")
            .expect("cria projeto vinculado");
        let standalone_project = catalog
            .create_project(None, "Projeto pessoal", "/tmp/pessoal")
            .expect("cria projeto avulso");

        let organizations = catalog.list_organizations().expect("lista organizações");
        let projects = catalog.list_projects().expect("lista projetos");

        assert_eq!(organizations.len(), 1);
        assert!(catalog
            .organization_exists(organization.id)
            .expect("valida organização"));
        assert_eq!(projects.len(), 2);
        assert_eq!(linked_project.organization_id, Some(organization.id));
        assert_eq!(standalone_project.organization_id, None);
    }

    #[test]
    fn replaces_the_documentation_roots_of_a_project() {
        let catalog = CatalogDatabase::open_in_memory().expect("abre catálogo em memória");
        let project = catalog
            .create_project(None, "YABook", "/tmp/yabook")
            .expect("cria projeto");

        let roots = catalog
            .replace_documentation_roots(
                project.id,
                &[
                    super::DocumentationRootDraft {
                        display_name: "Início".into(),
                        relative_path: ".".into(),
                        initial_document_path: Some("README.md".into()),
                        position: 0,
                    },
                    super::DocumentationRootDraft {
                        display_name: "Documentação".into(),
                        relative_path: "docs".into(),
                        initial_document_path: None,
                        position: 10,
                    },
                ],
            )
            .expect("persiste raízes");

        assert_eq!(roots.len(), 2);
        assert_eq!(roots[0].relative_path, ".");
        assert_eq!(roots[1].relative_path, "docs");
    }
}
