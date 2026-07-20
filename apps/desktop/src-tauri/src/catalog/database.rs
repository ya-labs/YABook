use std::{path::Path, sync::Mutex};

use rusqlite::{Connection, Result};

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
        let connection = self
            .connection
            .lock()
            .expect("banco do catálogo disponível");

        connection.pragma_query_value(None, "user_version", |row| row.get::<_, u32>(0))
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

    use super::migrate;

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
}
