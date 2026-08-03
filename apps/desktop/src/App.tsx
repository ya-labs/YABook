import { invoke } from "@tauri-apps/api/core";
import { FormEvent, useEffect, useState } from "react";
import "./App.css";

type AppStatus = {
  name: string;
  version: string;
};

type Organization = {
  id: number;
  displayName: string;
};

type Project = {
  id: number;
  organizationId: number | null;
  displayName: string;
  sourcePath: string;
};

type DocumentationRoot = {
  id: number;
  displayName: string;
  relativePath: string;
  initialDocumentPath: string | null;
};

type ProjectForm = {
  displayName: string;
  sourcePath: string;
  organizationId: string;
};

const emptyProjectForm: ProjectForm = {
  displayName: "",
  sourcePath: "",
  organizationId: "",
};

function App() {
  const [status, setStatus] = useState<AppStatus>();
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [roots, setRoots] = useState<DocumentationRoot[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number>();
  const [organizationName, setOrganizationName] = useState("");
  const [projectForm, setProjectForm] = useState<ProjectForm>(emptyProjectForm);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<string>();
  const [error, setError] = useState<string>();

  useEffect(() => {
    void loadLibrary();
  }, []);

  async function loadLibrary(preferredProjectId?: number) {
    setIsLoading(true);
    setError(undefined);

    try {
      const [appStatus, savedOrganizations, savedProjects] = await Promise.all([
        invoke<AppStatus>("get_app_status"),
        invoke<Organization[]>("list_organizations"),
        invoke<Project[]>("list_projects"),
      ]);

      setStatus(appStatus);
      setOrganizations(savedOrganizations);
      setProjects(savedProjects);
      const nextProjectId = preferredProjectId
        ?? (savedProjects.some((project) => project.id === selectedProjectId)
          ? selectedProjectId
          : savedProjects[0]?.id);
      setSelectedProjectId(nextProjectId);

      if (nextProjectId) {
        setRoots(await invoke<DocumentationRoot[]>("discover_documentation_roots", { projectId: nextProjectId }));
      } else {
        setRoots([]);
      }
    } catch (reason) {
      setError(messageFrom(reason));
    } finally {
      setIsLoading(false);
    }
  }

  async function createOrganization(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(undefined);

    try {
      await invoke("create_organization", {
        input: { display_name: organizationName },
      });
      setOrganizationName("");
      setMessage("Organização cadastrada na biblioteca local.");
      await loadLibrary();
    } catch (reason) {
      setError(messageFrom(reason));
    } finally {
      setIsSaving(false);
    }
  }

  async function createProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setError(undefined);

    try {
      const project = await invoke<Project>("create_project", {
        input: {
          display_name: projectForm.displayName,
          source_path: projectForm.sourcePath,
          organization_id: projectForm.organizationId
            ? Number(projectForm.organizationId)
            : null,
        },
      });
      const discoveredRoots = await invoke<DocumentationRoot[]>(
        "discover_documentation_roots",
        { projectId: project.id },
      );

      setProjectForm(emptyProjectForm);
      setSelectedProjectId(project.id);
      setRoots(discoveredRoots);
      setMessage(
        discoveredRoots.length > 0
          ? "Projeto cadastrado e documentação descoberta."
          : "Projeto cadastrado. Nenhuma raiz documental foi encontrada.",
      );
      await loadLibrary(project.id);
    } catch (reason) {
      setError(messageFrom(reason));
    } finally {
      setIsSaving(false);
    }
  }

  async function selectProject(projectId: number) {
    setSelectedProjectId(projectId);
    setError(undefined);

    try {
      const discoveredRoots = await invoke<DocumentationRoot[]>(
        "discover_documentation_roots",
        { projectId },
      );
      setRoots(discoveredRoots);
    } catch (reason) {
      setError(messageFrom(reason));
    }
  }

  const selectedProject = projects.find((project) => project.id === selectedProjectId);

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Biblioteca local</p>
          <h1>YABook Desktop</h1>
        </div>
        {status && <span className="status">{status.name} {status.version}</span>}
      </header>

      {error && <p className="feedback error" role="alert">{error}</p>}
      {message && <p className="feedback success">{message}</p>}

      <section className="library-grid" aria-busy={isLoading}>
        <aside className="sidebar">
          <section>
            <h2>Organizações</h2>
            <ul className="item-list">
              {organizations.map((organization) => (
                <li key={organization.id}>{organization.displayName}</li>
              ))}
              {!isLoading && organizations.length === 0 && <li className="empty">Nenhuma cadastrada.</li>}
            </ul>
            <form onSubmit={createOrganization} className="compact-form">
              <label htmlFor="organization-name">Nova organização</label>
              <input
                id="organization-name"
                value={organizationName}
                onChange={(event) => setOrganizationName(event.target.value)}
                placeholder="Ex.: YA LABS"
                required
              />
              <button type="submit" disabled={isSaving}>Adicionar</button>
            </form>
          </section>

          <section>
            <h2>Projetos</h2>
            <ul className="project-list">
              {projects.map((project) => (
                <li key={project.id}>
                  <button
                    type="button"
                    className={project.id === selectedProjectId ? "project active" : "project"}
                    onClick={() => void selectProject(project.id)}
                  >
                    <strong>{project.displayName}</strong>
                    <span>{project.sourcePath}</span>
                  </button>
                </li>
              ))}
              {!isLoading && projects.length === 0 && <li className="empty">Nenhum projeto cadastrado.</li>}
            </ul>
          </section>
        </aside>

        <section className="content">
          <section className="panel">
            <p className="eyebrow">Cadastrar fonte local</p>
            <h2>Adicionar projeto</h2>
            <form onSubmit={createProject} className="project-form">
              <label htmlFor="project-name">Nome de exibição</label>
              <input
                id="project-name"
                value={projectForm.displayName}
                onChange={(event) => setProjectForm({ ...projectForm, displayName: event.target.value })}
                placeholder="Ex.: YABook"
                required
              />
              <label htmlFor="project-path">Caminho do diretório</label>
              <input
                id="project-path"
                value={projectForm.sourcePath}
                onChange={(event) => setProjectForm({ ...projectForm, sourcePath: event.target.value })}
                placeholder="/home/pessoa/Documentos/projeto"
                required
              />
              <label htmlFor="project-organization">Organização <span>(opcional)</span></label>
              <select
                id="project-organization"
                value={projectForm.organizationId}
                onChange={(event) => setProjectForm({ ...projectForm, organizationId: event.target.value })}
              >
                <option value="">Projeto avulso</option>
                {organizations.map((organization) => (
                  <option key={organization.id} value={organization.id}>{organization.displayName}</option>
                ))}
              </select>
              <button type="submit" disabled={isSaving}>Cadastrar e descobrir</button>
            </form>
          </section>

          <section className="panel roots-panel">
            <p className="eyebrow">Documentação encontrada</p>
            <h2>{selectedProject ? selectedProject.displayName : "Selecione um projeto"}</h2>
            {selectedProject && roots.length > 0 && (
              <ul className="roots-list">
                {roots.map((root) => (
                  <li key={root.id}>
                    <strong>{root.displayName}</strong>
                    <span>{root.relativePath === "." ? "Raiz do projeto" : root.relativePath}</span>
                    {root.initialDocumentPath && <small>Documento inicial: {root.initialDocumentPath}</small>}
                  </li>
                ))}
              </ul>
            )}
            {selectedProject && roots.length === 0 && (
              <p className="empty">Não foram encontrados `README.md` na raiz nem uma pasta `docs/`.</p>
            )}
            {!selectedProject && <p className="empty">Cadastre ou selecione uma fonte local para ver a documentação descoberta.</p>}
          </section>
        </section>
      </section>
    </main>
  );
}

function messageFrom(reason: unknown) {
  return reason instanceof Error ? reason.message : String(reason);
}

export default App;
