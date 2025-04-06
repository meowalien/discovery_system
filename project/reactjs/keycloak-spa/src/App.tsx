import React, { useEffect, useState } from 'react';
import { UserManager, WebStorageStateStore, User } from 'oidc-client-ts';

// 1. Keycloak OIDC client configuration
const oidcConfig = {
  authority: 'http://localhost:8082/realms/discovery_system', // 修改為你的 realm URL
  client_id: 'demo',                                   // 修改為你的 client ID
  redirect_uri: window.location.origin,                       // 必須與 Keycloak 設定吻合
  post_logout_redirect_uri: window.location.origin,
  response_type: 'code',
  scope: 'openid profile email',
  userStore: new WebStorageStateStore({ store: window.localStorage }),
};

const userManager = new UserManager(oidcConfig);

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // 2. 檢查是否已登入或為 callback
    userManager.getUser().then((u) => {
      if (u && !u.expired) {
        setUser(u);
      } else if (window.location.search.includes('code=')) {
        // 3. 交換 code for tokens
        userManager.signinRedirectCallback()
          .then((u2) => setUser(u2))
          .catch(console.error);
      }
    });
  }, []);

  const login = () => {
    userManager.signinRedirect();
  };

  const logout = () => {
    userManager.signoutRedirect();
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      {!user && <button onClick={login}>Login with Keycloak</button>}

      {user && (
        <div>
          <h2>Access Token</h2>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{user.access_token}</pre>

          <h2>ID Token</h2>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{user.id_token}</pre>

          <button onClick={logout} style={{ marginTop: '1rem' }}>
            Logout
          </button>
        </div>
      )}
    </div>
  );
};

export default App;