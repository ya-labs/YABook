'use strict';
// Extensão YABook: camada de visualização sobre os arquivos que os scripts Python do YABook geram.
const path = require('path');
const vscode = require('vscode');
const sessions = require('./lib/sessions');

const EMPTY = 'yabook-vazio';

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
        item.description = session.agente || '';
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
  context.subscriptions.push(
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
