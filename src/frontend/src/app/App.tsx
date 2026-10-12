import { ChatPage } from "../features/chat/ChatPage";

/** Composição da aplicação: apenas a feature de chat nesta entrega. */
export function App() {
  return (
    <div className="app">
      <header className="app__header">
        <h1 className="app__title">Aurora</h1>
        <p className="app__subtitle">
          Protótipo local com resposta fixa. Não use com pessoas em situação de violência.
        </p>
      </header>
      <main className="app__main">
        <ChatPage />
      </main>
    </div>
  );
}
