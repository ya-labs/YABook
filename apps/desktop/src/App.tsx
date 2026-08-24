import { invoke, convertFileSrc } from "@tauri-apps/api/core";
import { openPath, revealItemInDir } from "@tauri-apps/plugin-opener";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { FormEvent, useEffect, useMemo, useState } from "react";
import "./App.css";

type Organization = { id: number; displayName: string };
type Project = { id: number; displayName: string; sourcePath: string; organizationId: number | null };
type DocumentationRoot = { id: number; displayName: string; relativePath: string; initialDocumentPath: string | null };
type TreeEntry = { path: string; name: string; isDirectory: boolean; children: TreeEntry[] };
type DocumentContent = { rootId: number; relativePath: string; absolutePath: string; content: string };
type DocumentationConfiguration = { version: number; project?: { id?: string; name?: string }; documentation: { roots: { id: string; label?: string; path: string; entry?: string; order?: number; overrides?: { path: string; label?: string; order?: number; hidden?: boolean }[] }[] } };
type DocumentationDiscovery = { roots: DocumentationRoot[]; configuration: DocumentationConfiguration | null; configurationError: string | null };
type ConfigurationPreview = { content: string };
type ProjectForm = { displayName: string; sourcePath: string; organizationId: string };
const emptyProjectForm: ProjectForm = { displayName: "", sourcePath: "", organizationId: "" };

function App() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [roots, setRoots] = useState<DocumentationRoot[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number>();
  const [selectedRoot, setSelectedRoot] = useState<DocumentationRoot>();
  const [tree, setTree] = useState<TreeEntry[]>([]);
  const [document, setDocument] = useState<DocumentContent>();
  const [history, setHistory] = useState<{ root: DocumentationRoot; path: string }[]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [favorites, setFavorites] = useState<string[]>(() => JSON.parse(localStorage.getItem("yabook-favorites") ?? "[]"));
  const [recents, setRecents] = useState<string[]>(() => JSON.parse(localStorage.getItem("yabook-recents") ?? "[]"));
  const [organizationName, setOrganizationName] = useState("");
  const [projectForm, setProjectForm] = useState<ProjectForm>(emptyProjectForm);
  const [configurationDraft, setConfigurationDraft] = useState("");
  const [configurationPreview, setConfigurationPreview] = useState("");
  const [configurationNotice, setConfigurationNotice] = useState<string>();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>();

  useEffect(() => { void loadLibrary(); }, []);
  useEffect(() => { localStorage.setItem("yabook-favorites", JSON.stringify(favorites)); }, [favorites]);
  useEffect(() => { localStorage.setItem("yabook-recents", JSON.stringify(recents)); }, [recents]);

  async function loadLibrary(preferredProjectId?: number) {
    setIsLoading(true); setError(undefined);
    try {
      const [savedOrganizations, savedProjects] = await Promise.all([invoke<Organization[]>("list_organizations"), invoke<Project[]>("list_projects")]);
      setOrganizations(savedOrganizations); setProjects(savedProjects);
      const id = preferredProjectId ?? savedProjects.find((project) => project.id === selectedProjectId)?.id ?? savedProjects[0]?.id;
      setSelectedProjectId(id);
      if (id) await selectProject(id, savedProjects);
    } catch (reason) { setError(messageFrom(reason)); } finally { setIsLoading(false); }
  }

  async function selectProject(projectId: number, source = projects) {
    setSelectedProjectId(projectId); setDocument(undefined); setTree([]); setError(undefined);
    try {
      const discovery = await invoke<DocumentationDiscovery>("discover_documentation_roots", { projectId });
      setRoots(discovery.roots);
      setConfigurationNotice(discovery.configurationError ?? undefined);
      const draftKey = configurationDraftKey(projectId);
      setConfigurationDraft(localStorage.getItem(draftKey) ?? JSON.stringify(discovery.configuration ?? configurationFromRoots(source.find((project) => project.id === projectId), discovery.roots), null, 2));
      setConfigurationPreview("");
      const root = discovery.roots[0];
      if (root) await selectRoot(root);
      else setSelectedRoot(undefined);
    } catch (reason) { setError(messageFrom(reason)); }
    void source;
  }

  async function selectRoot(root: DocumentationRoot) {
    setSelectedRoot(root); setDocument(undefined); setError(undefined);
    try {
      const nextTree = await invoke<TreeEntry[]>("list_document_tree", { rootId: root.id });
      setTree(nextTree);
      const initial = root.initialDocumentPath ?? firstDocument(nextTree)?.path;
      if (initial) await navigate(root, initial, true);
    } catch (reason) { setTree([]); setError(messageFrom(reason)); }
  }

  async function navigate(root: DocumentationRoot, path: string, pushHistory: boolean) {
    setError(undefined);
    try {
      const next = await invoke<DocumentContent>("read_document", { rootId: root.id, relativePath: path });
      setSelectedRoot(root); setDocument(next);
      const key = locationKey(root, path);
      setRecents((items) => [key, ...items.filter((item) => item !== key)].slice(0, 10));
      if (pushHistory) {
        const nextHistory = [...history.slice(0, historyIndex + 1), { root, path }];
        setHistory(nextHistory); setHistoryIndex(nextHistory.length - 1);
      }
    } catch (reason) { setError(messageFrom(reason)); }
  }

  function moveHistory(step: number) {
    const index = historyIndex + step; const item = history[index];
    if (!item) return;
    setHistoryIndex(index); void navigate(item.root, item.path, false);
  }

  async function createOrganization(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try { await invoke("create_organization", { input: { display_name: organizationName } }); setOrganizationName(""); await loadLibrary(); }
    catch (reason) { setError(messageFrom(reason)); }
  }

  async function createProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      const project = await invoke<Project>("create_project", { input: { display_name: projectForm.displayName, source_path: projectForm.sourcePath, organization_id: projectForm.organizationId ? Number(projectForm.organizationId) : null } });
      setProjectForm(emptyProjectForm); await loadLibrary(project.id);
    } catch (reason) { setError(messageFrom(reason)); }
  }

  function updateConfigurationDraft(value: string) {
    setConfigurationDraft(value);
    if (selectedProjectId) localStorage.setItem(configurationDraftKey(selectedProjectId), value);
    setConfigurationPreview("");
  }

  function parsedConfiguration() {
    try { return JSON.parse(configurationDraft) as DocumentationConfiguration; }
    catch { throw new Error("O rascunho precisa conter JSON válido antes da prévia."); }
  }

  async function previewConfiguration() {
    if (!selectedProjectId) return;
    try {
      const preview = await invoke<ConfigurationPreview>("preview_documentation_configuration", { projectId: selectedProjectId, configuration: parsedConfiguration() });
      setConfigurationPreview(preview.content); setConfigurationNotice(undefined);
    } catch (reason) { setConfigurationNotice(messageFrom(reason)); }
  }

  async function saveConfiguration() {
    if (!selectedProjectId || !window.confirm("Salvar este rascunho como .yabook/config.json do projeto?")) return;
    try {
      await invoke("save_documentation_configuration", { projectId: selectedProjectId, input: { configuration: parsedConfiguration(), confirmed: true } });
      localStorage.removeItem(configurationDraftKey(selectedProjectId));
      setConfigurationNotice("Configuração compartilhada salva.");
      await selectProject(selectedProjectId);
    } catch (reason) { setConfigurationNotice(messageFrom(reason)); }
  }

  const headings = useMemo(() => document ? Array.from(document.content.matchAll(/^(#{1,6})\s+(.+)$/gm)) : [], [document]);
  const favorite = document && favorites.includes(locationKey(selectedRoot!, document.relativePath));
  const selectedProject = projects.find((project) => project.id === selectedProjectId);
  const openRelativeLink = (href?: string) => {
    if (!href || !document || !selectedRoot || /^(https?:|mailto:|#)/.test(href)) return;
    const path = normalizePath(document.relativePath, href.split("#")[0]);
    if (path.endsWith(".md")) { void navigate(selectedRoot, path, true); }
  };

  return <main className="app-shell">
    <header className="app-header"><div><p className="eyebrow">Biblioteca local</p><h1>YABook Desktop</h1></div></header>
    {error && <p className="feedback error" role="alert">{error} <button onClick={() => selectedProjectId && void selectProject(selectedProjectId)}>Tentar novamente</button></p>}
    <section className="library-grid" aria-busy={isLoading}>
      <aside className="sidebar"><section><h2>Projetos</h2><ul className="project-list">{projects.map((project) => <li key={project.id}><button className={project.id === selectedProjectId ? "project active" : "project"} onClick={() => void selectProject(project.id)}><strong>{project.displayName}</strong><span>{project.sourcePath}</span></button></li>)}</ul></section>
      <section><h2>Raízes</h2><ul className="roots-list">{roots.map((root) => <li key={root.id}><button className="link-button" onClick={() => void selectRoot(root)}>{root.displayName} <small>{root.relativePath}</small></button></li>)}</ul>{selectedProject && !roots.length && <p className="empty">Nenhuma raiz disponível. Confira o diretório e tente novamente.</p>}</section>
      <section><h2>Árvore</h2><Tree entries={tree} current={document?.relativePath} onSelect={(path) => selectedRoot && void navigate(selectedRoot, path, true)} /></section></aside>
      <section className="content"><section className="panel reader">{document ? <>
        <nav className="toolbar" aria-label="Navegação do documento"><button disabled={historyIndex <= 0} onClick={() => moveHistory(-1)}>← Voltar</button><button disabled={historyIndex >= history.length - 1} onClick={() => moveHistory(1)}>Avançar →</button><button onClick={() => document && navigator.clipboard.writeText(document.absolutePath)}>Copiar caminho</button><button onClick={() => document && void openPath(document.absolutePath, "code").catch((reason) => setError(`Não foi possível abrir no VS Code: ${messageFrom(reason)}`))}>VS Code</button><button onClick={() => document && void revealItemInDir(document.absolutePath).catch((reason) => setError(`Não foi possível abrir o explorador: ${messageFrom(reason)}`))}>Explorador</button><button onClick={() => document && setFavorites((items) => favorite ? items.filter((item) => item !== locationKey(selectedRoot!, document.relativePath)) : [...items, locationKey(selectedRoot!, document.relativePath)])}>{favorite ? "Remover favorito" : "Favoritar"}</button></nav>
        <p className="breadcrumbs">{selectedProject?.displayName} / {selectedRoot?.displayName} / {document.relativePath}</p>
        <article className="markdown"><Markdown remarkPlugins={[remarkGfm]} components={{ a: ({ href, children }) => <a href={href} onClick={(event) => { if (href?.endsWith(".md")) { event.preventDefault(); openRelativeLink(href); } }}>{children}</a>, img: ({ src, alt }) => <img src={src?.startsWith("http") ? src : convertFileSrc(resolveAsset(document.absolutePath, src ?? ""))} alt={alt ?? ""} />, h1: ({ children }) => <h1 id={slug(children)}>{children}</h1>, h2: ({ children }) => <h2 id={slug(children)}>{children}</h2>, h3: ({ children }) => <h3 id={slug(children)}>{children}</h3>, h4: ({ children }) => <h4 id={slug(children)}>{children}</h4>, h5: ({ children }) => <h5 id={slug(children)}>{children}</h5>, h6: ({ children }) => <h6 id={slug(children)}>{children}</h6> }}>{document.content}</Markdown></article>
      </> : <p className="empty">Selecione uma raiz e um documento para começar.</p>}</section></section>
      <aside className="reader-side"><section className="panel"><h2>Índice</h2><ul className="item-list">{headings.map((item, index) => <li key={index} className={`heading-${item[1].length}`}><a href={`#${slug(item[2])}`}>{item[2]}</a></li>)}</ul></section><section className="panel"><h2>Recentes</h2><p className="compact-list">{recents.join("\n") || "Nenhum documento aberto."}</p></section><section className="panel"><h2>Favoritos</h2><p className="compact-list">{favorites.join("\n") || "Nenhum favorito."}</p></section></aside>
    </section>
    <section className="panel configuration"><h2>Personalização documental</h2><p>Este rascunho fica somente neste computador até o salvamento confirmado.</p>{configurationNotice && <p className="feedback status">{configurationNotice}</p>}<textarea aria-label="Rascunho de configuração compartilhada" value={configurationDraft} onChange={(event) => updateConfigurationDraft(event.target.value)} spellCheck={false} /><div className="toolbar"><button onClick={() => void previewConfiguration()} disabled={!selectedProjectId}>Validar e pré-visualizar</button><button onClick={() => void saveConfiguration()} disabled={!selectedProjectId || !configurationPreview}>Salvar como padrão do projeto</button><button onClick={() => selectedProjectId && updateConfigurationDraft(JSON.stringify(configurationFromRoots(selectedProject, roots), null, 2))} disabled={!selectedProjectId}>Restaurar descoberta</button></div>{configurationPreview && <pre className="configuration-preview">{configurationPreview}</pre>}</section>
    <section className="panel registration"><h2>Adicionar projeto</h2><form onSubmit={createProject} className="project-form"><input value={projectForm.displayName} onChange={(event) => setProjectForm({ ...projectForm, displayName: event.target.value })} placeholder="Nome do projeto" required /><input value={projectForm.sourcePath} onChange={(event) => setProjectForm({ ...projectForm, sourcePath: event.target.value })} placeholder="Caminho do diretório" required /><select value={projectForm.organizationId} onChange={(event) => setProjectForm({ ...projectForm, organizationId: event.target.value })}><option value="">Projeto avulso</option>{organizations.map((organization) => <option key={organization.id} value={organization.id}>{organization.displayName}</option>)}</select><button type="submit">Cadastrar</button></form><form onSubmit={createOrganization} className="compact-form"><input value={organizationName} onChange={(event) => setOrganizationName(event.target.value)} placeholder="Nova organização" required /><button type="submit">Adicionar organização</button></form></section>
  </main>;
}

function Tree({ entries, current, onSelect }: { entries: TreeEntry[]; current?: string; onSelect: (path: string) => void }) { return <ul className="tree">{entries.map((entry) => <li key={entry.path}>{entry.isDirectory ? <><strong>{entry.name}</strong><Tree entries={entry.children} current={current} onSelect={onSelect} /></> : <button className={entry.path === current ? "link-button active-doc" : "link-button"} onClick={() => onSelect(entry.path)}>{entry.name}</button>}</li>)}</ul>; }
function firstDocument(entries: TreeEntry[]): TreeEntry | undefined { for (const entry of entries) { if (!entry.isDirectory) return entry; const child = firstDocument(entry.children); if (child) return child; } }
function locationKey(root: DocumentationRoot, path: string) { return `${root.id}:${path}`; }
function configurationDraftKey(projectId: number) { return `yabook-configuration-draft-${projectId}`; }
function configurationFromRoots(project: Project | undefined, roots: DocumentationRoot[]): DocumentationConfiguration { return { version: 1, project: project ? { name: project.displayName } : undefined, documentation: { roots: roots.map((root, index) => ({ id: `root-${index + 1}`, label: root.displayName, path: root.relativePath, entry: root.initialDocumentPath ?? undefined, order: root.position })) } }; }
function normalizePath(current: string, href: string) { const base = current.split("/").slice(0, -1); for (const part of href.split("/")) { if (part === "..") base.pop(); else if (part && part !== ".") base.push(part); } return base.join("/"); }
function resolveAsset(absolutePath: string, src: string) { return normalizePath(absolutePath.replace(/\\/g, "/"), src); }
function slug(value: unknown): string { return String(value).toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, ""); }
function messageFrom(reason: unknown) { return reason instanceof Error ? reason.message : String(reason); }
export default App;
