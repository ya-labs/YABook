'use strict';
// Extensão YABook: camada de visualização sobre os arquivos que os scripts Python do YABook geram.
const path = require('path');
const vscode = require('vscode');
const sessions = require('./lib/sessions');
const explain = require('./lib/explain');
const yabook = require('./lib/yabook');
const fs = require('fs');
const os = require('os');

function settings() {
  return vscode.workspace.getConfiguration('yabook');
}

function scriptsDir() {
  const found = yabook.findScripts(settings().get('scriptsDir'), sessions.listSessions(base()));
  if (!found) {
    vscode.window.showErrorMessage('YABook: scripts do plugin não encontrados. Defina yabook.scriptsDir.');
  }
  return found;
}

function configFile() {
  return process.env.YABOOK_CONFIG || path.join(os.homedir(), '.config', 'yabook', 'config.json');
}

// Servidor local em terminal próprio: fica visível e fecha com o terminal. Reaproveita o que já responde.
async function openServer(name, port, args) {
  const url = `http://127.0.0.1:${port}/`;
  if (!(await yabook.serving(port))) {
    const scripts = scriptsDir();
    if (!scripts) return;
    let terminal = vscode.window.terminals.find((t) => t.name === name);
    if (terminal) terminal.dispose();
    terminal = vscode.window.createTerminal({ name, cwd: scripts, shellPath: settings().get('python') || 'python3', shellArgs: args(scripts) });
    const ready = await vscode.window.withProgress(
      { location: vscode.ProgressLocation.Notification, title: `YABook: iniciando ${name}…` },
      () => yabook.waitServing(port)
    );
    if (!ready) {
      terminal.show();
      vscode.window.showErrorMessage(`YABook: ${name} não respondeu na porta ${port}; veja o terminal.`);
      return;
    }
  }
  await vscode.env.openExternal(vscode.Uri.parse(url));
}

function openMemoryMap() {
  const port = settings().get('memoryMapPort') || 8766;
  const root = yabook.memoryRoot(configFile());
  if (!root) {
    vscode.window.showErrorMessage('YABook: memory_root ausente na configuração do YABook; rode a configuração da memória.');
    return undefined;
  }
  return openServer('YABook: mapa de memória', port,
    (scripts) => [path.join(scripts, 'yabook_memory.py'), '--root', root, 'map', '--serve', '--port', String(port)]);
}

function openTasks() {
  const port = settings().get('tasksPort') || yabook.tasksPort(configFile());
  return openServer('YABook Tasks', port,
    (scripts) => [path.join(scripts, 'yabook_tasks.py'), 'board', '--serve', '--port', String(port)]);
}

async function openHelp() {
  const scripts = scriptsDir();
  const file = yabook.helpFile(scripts);
  if (file && fs.existsSync(file)) await vscode.commands.executeCommand('markdown.showPreview', vscode.Uri.file(file));
}

async function copyCommand(command) {
  await vscode.env.clipboard.writeText(`$yabook ${command}`);
  vscode.window.setStatusBarMessage(`YABook: "$yabook ${command}" copiado`, 2500);
}

class HelpTree {
  constructor() {
    this.changed = new vscode.EventEmitter();
    this.onDidChangeTreeData = this.changed.event;
  }

  refresh() {
    this.changed.fire();
  }

  getTreeItem(node) {
    return node.item;
  }

  action(label, icon, command, tooltip) {
    const item = new vscode.TreeItem(label, vscode.TreeItemCollapsibleState.None);
    item.iconPath = new vscode.ThemeIcon(icon);
    item.command = { command, title: label };
    item.tooltip = tooltip;
    return { item };
  }

  getChildren(node) {
    if (node && node.group) {
      return node.group.comandos.map((command) => {
        const item = new vscode.TreeItem(`$yabook ${command}`, vscode.TreeItemCollapsibleState.None);
        item.iconPath = new vscode.ThemeIcon('terminal');
        item.tooltip = 'Clique para copiar';
        item.command = { command: 'yabook.ajuda.copiar', title: 'Copiar', arguments: [command] };
        return { item };
      });
    }
    if (node) return [];
    const actions = [
      this.action('Ver alterações da última sessão', 'diff-multiple', 'yabook.diff.abrir', 'Aba única com as alterações do agente'),
      this.action('Abrir YABook Tasks no navegador', 'checklist', 'yabook.tasks.site', 'Inicia o site do Tasks, se preciso'),
      this.action('Abrir mapa de memória no navegador', 'type-hierarchy', 'yabook.memoria.mapa', 'Inicia o mapa de memória, se preciso'),
      this.action('Abrir ajuda completa', 'book', 'yabook.ajuda.abrir', 'help.md da versão instalada'),
    ];
    const file = yabook.helpFile(yabook.findScripts(settings().get('scriptsDir'), sessions.listSessions(base())));
    const groups = file && fs.existsSync(file) ? yabook.parseHelp(fs.readFileSync(file, 'utf8')) : [];
    return actions.concat(groups.map((group) => {
      const item = new vscode.TreeItem(group.grupo, vscode.TreeItemCollapsibleState.Collapsed);
      item.iconPath = new vscode.ThemeIcon('symbol-namespace');
      item.description = `${group.comandos.length}`;
      return { item, group };
    }));
  }
}

const EMPTY = 'yabook-vazio';
let comments;
let threads = [];

function clearExplanations() {
  threads.forEach((thread) => thread.dispose());
  threads = [];
}

// Explicações como comentários somente leitura ancorados em cada bloco; valem no diff e no editor comum.
function showExplanations(session) {
  clearExplanations();
  for (const row of explain.anchors(session)) {
    const markdown = new vscode.MarkdownString(row.markdown);
    const comment = { body: markdown, mode: vscode.CommentMode.Preview, author: { name: 'YABook' } };
    const range = new vscode.Range(row.start, 0, row.end, 0);
    const thread = comments.createCommentThread(vscode.Uri.file(row.file), range, [comment]);
    thread.canReply = false;
    thread.label = `Explicação ${row.id}`;
    thread.collapsibleState = vscode.CommentThreadCollapsibleState.Expanded;
    threads.push(thread);
  }
  return threads.length;
}

async function browseExplanations() {
  const [session] = workspaceSessions();
  const rows = session ? explain.anchors(session) : [];
  if (!rows.length) {
    vscode.window.showInformationMessage('YABook: a sessão mais recente não tem explicações. Peça `$yabook diff explain` ao agente.');
    return;
  }
  showExplanations(session);
  const choice = await vscode.window.showQuickPick(
    rows.map((row) => ({ label: `${row.id} · ${row.arquivo}:${row.start + 1}`, detail: row.texto, row })),
    { placeHolder: 'Explicação do bloco', matchOnDetail: true }
  );
  if (!choice) return;
  const change = sessions.changes(session).find((c) => c.caminho === choice.row.arquivo);
  if (change) await openFile(session, change);
  const editor = vscode.window.activeTextEditor;
  if (editor) {
    const range = new vscode.Range(choice.row.start, 0, choice.row.end, 0);
    editor.revealRange(range, vscode.TextEditorRevealType.InCenterIfOutsideViewport);
    editor.selection = new vscode.Selection(range.start, range.start);
  }
}

function base() {
  return sessions.defaultBase(vscode.workspace.getConfiguration('yabook').get('diffsDir'));
}

function folders() {
  return (vscode.workspace.workspaceFolders || []).map((f) => f.uri.fsPath);
}

function workspaceSessions() {
  const all = sessions.listSessions(base());
  const own = sessions.forWorkspace(all, folders());
  return own.length || !folders().length ? own : [];
}

function emptyUri(rel) {
  return vscode.Uri.from({ scheme: EMPTY, path: '/' + rel });
}

async function openSession(session) {
  const files = sessions.changes(session);
  if (!files.length) {
    vscode.window.showInformationMessage('YABook: nenhuma alteração pendente nesta sessão.');
    return;
  }
  const resources = files.map((c) => {
    const current = vscode.Uri.file(c.depois || sessions.target(session, c.caminho));
    return [current, c.antes ? vscode.Uri.file(c.antes) : undefined, c.depois ? vscode.Uri.file(c.depois) : undefined];
  });
  const title = `YABook: ${path.basename(session.projeto)} (${files.length} arquivo${files.length > 1 ? 's' : ''})`;
  await vscode.commands.executeCommand('vscode.changes', title, resources);
  showExplanations(session);
}

async function openFile(session, change) {
  const left = change.antes ? vscode.Uri.file(change.antes) : emptyUri(change.caminho);
  const right = change.depois ? vscode.Uri.file(change.depois) : emptyUri(change.caminho);
  await vscode.commands.executeCommand('vscode.diff', left, right, `${change.caminho} (YABook: antes ↔ agora)`);
}

class SessionsTree {
  constructor() {
    this.changed = new vscode.EventEmitter();
    this.onDidChangeTreeData = this.changed.event;
  }

  refresh() {
    this.changed.fire();
  }

  getTreeItem(node) {
    return node.item;
  }

  getChildren(node) {
    if (!node) {
      return workspaceSessions().map((session) => {
        const item = new vscode.TreeItem(sessions.label(session), vscode.TreeItemCollapsibleState.Collapsed);
        const explained = explain.load(session);
        item.description = [session.agente, explained && `${explained.blocos.length} explicação(ões)`].filter(Boolean).join(' · ');
        item.tooltip = session.pasta;
        item.contextValue = 'sessao';
        item.iconPath = new vscode.ThemeIcon('history');
        return { item, session };
      });
    }
    if (!node.change) {
      return sessions.changes(node.session).map((change) => {
        const item = new vscode.TreeItem(path.basename(change.caminho), vscode.TreeItemCollapsibleState.None);
        item.description = `${change.estado} · ${path.dirname(change.caminho) === '.' ? '' : path.dirname(change.caminho)}`;
        item.tooltip = change.caminho;
        item.iconPath = new vscode.ThemeIcon(change.estado === 'novo' ? 'diff-added' : change.estado === 'removido' ? 'diff-removed' : 'diff-modified');
        item.command = { command: 'yabook.diff.abrirArquivo', title: 'Abrir diff', arguments: [node.session, change] };
        return { item, session: node.session, change };
      });
    }
    return [];
  }
}

async function pickSession() {
  const all = sessions.listSessions(base());
  const own = new Set(sessions.forWorkspace(all, folders()));
  const ordered = [...all.filter((s) => own.has(s)), ...all.filter((s) => !own.has(s))];
  if (!ordered.length) {
    vscode.window.showInformationMessage('YABook: nenhuma sessão de diff encontrada em ' + base());
    return;
  }
  const choice = await vscode.window.showQuickPick(
    ordered.map((s) => ({ label: sessions.label(s), description: s.agente || '', detail: `${s.arquivos.length} arquivo(s) · ${s.projeto}`, session: s })),
    { placeHolder: 'Sessão de diff do YABook' }
  );
  if (choice) await openSession(choice.session);
}

function activate(context) {
  const tree = new SessionsTree();
  const watcher = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(vscode.Uri.file(base()), '**/manifest.json'));
  const refresh = () => tree.refresh();
  const explanations = vscode.workspace.createFileSystemWatcher(new vscode.RelativePattern(vscode.Uri.file(base()), '**/explain.json'));
  comments = vscode.comments.createCommentController('yabook.explicacoes', 'YABook: explicações');
  const help = new HelpTree();
  context.subscriptions.push(
    vscode.window.registerTreeDataProvider('yabook.ajuda', help),
    vscode.commands.registerCommand('yabook.ajuda.abrir', openHelp),
    vscode.commands.registerCommand('yabook.ajuda.copiar', copyCommand),
    vscode.commands.registerCommand('yabook.ajuda.atualizar', () => help.refresh()),
    vscode.commands.registerCommand('yabook.memoria.mapa', openMemoryMap),
    vscode.commands.registerCommand('yabook.tasks.site', openTasks),
    comments,
    explanations,
    explanations.onDidCreate(refresh),
    explanations.onDidChange(refresh),
    vscode.commands.registerCommand('yabook.diff.explicacoes', browseExplanations),
    vscode.commands.registerCommand('yabook.diff.limparExplicacoes', clearExplanations),
    watcher,
    watcher.onDidCreate(refresh),
    watcher.onDidChange(refresh),
    watcher.onDidDelete(refresh),
    vscode.window.registerTreeDataProvider('yabook.sessoes', tree),
    vscode.workspace.registerTextDocumentContentProvider(EMPTY, { provideTextDocumentContent: () => '' }),
    vscode.commands.registerCommand('yabook.diff.abrir', async () => {
      const [latest] = workspaceSessions();
      if (latest) await openSession(latest);
      else await pickSession();
    }),
    vscode.commands.registerCommand('yabook.diff.escolher', pickSession),
    vscode.commands.registerCommand('yabook.diff.atualizar', refresh),
    vscode.commands.registerCommand('yabook.diff.abrirSessao', (node) => node && openSession(node.session)),
    vscode.commands.registerCommand('yabook.diff.abrirArquivo', openFile),
    vscode.window.registerUriHandler({
      async handleUri(uri) {
        const params = new URLSearchParams(uri.query);
        if (uri.path === '/diff' && params.get('manifest')) {
          const session = sessions.readManifest(params.get('manifest'));
          if (!session) {
            vscode.window.showErrorMessage('YABook: manifesto de diff não encontrado: ' + params.get('manifest'));
            return;
          }
          refresh();
          await openSession(session);
        }
      },
    })
  );
}

function deactivate() {}

module.exports = { activate, deactivate };
