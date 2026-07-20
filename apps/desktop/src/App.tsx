import { invoke } from "@tauri-apps/api/core";
import { useEffect, useState } from "react";
import "./App.css";

type AppStatus = {
  name: string;
  version: string;
};

function App() {
  const [status, setStatus] = useState<AppStatus>();
  const [statusError, setStatusError] = useState(false);

  useEffect(() => {
    void invoke<AppStatus>("get_app_status")
      .then(setStatus)
      .catch(() => setStatusError(true));
  }, []);

  return (
    <main className="app-shell">
      <h1>YABook Desktop</h1>
      {status && <p>Núcleo local disponível: {status.name} {status.version}.</p>}
      {statusError && <p>Não foi possível conectar ao núcleo local.</p>}
      {!status && !statusError && <p>Conectando ao núcleo local…</p>}
    </main>
  );
}

export default App;
