import React, { useEffect, useState } from 'react';
import { UserManager, WebStorageStateStore, User } from 'oidc-client-ts';

// 1. Keycloak OIDC client configuration
const oidcConfig = {
  authority: 'http://localhost:8082/realms/discovery_system',
  client_id: 'demo',
  redirect_uri: window.location.origin,
  post_logout_redirect_uri: window.location.origin,

  // —— 关键配置 ——
  response_type: 'code',
  scope: 'openid profile email offline_access',  // 加上 offline_access 拿到 refresh token
  automaticSilentRenew: true,                     // 开启自动静默刷新
  silent_redirect_uri: window.location.origin + '/silent-renew.html',  // 静默刷新的回调页
  accessTokenExpiringNotificationTime: 60,       // 在过期前 60 秒触发 expiring 事件

  userStore: new WebStorageStateStore({ store: window.localStorage }),
};

const userManager = new UserManager(oidcConfig);

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // 初次检查
    userManager.getUser().then(u => {
      if (u && !u.expired) {
        setUser(u);
      } else if (window.location.search.includes('code=')) {
        userManager.signinRedirectCallback().then(u2 => setUser(u2));
      }
    });

    // 当 access token 快过期时触发
    const onExpiring = () => {
      console.log('Access token 即将过期，静默刷新...');
      userManager.signinSilent()
        .then(u2 => {
          console.log('静默刷新成功', u2);
          setUser(u2);
        })
        .catch(err => console.error('静默刷新失败', err));
    };
    userManager.events.addAccessTokenExpiring(onExpiring);

    // 静默刷新失败时也可捕获
    userManager.events.addSilentRenewError(err => {
      console.error('Silent renew error', err);
    });

    return () => {
      userManager.events.removeAccessTokenExpiring(onExpiring);
    };
  }, []);

  const login = () => userManager.signinRedirect();
  const logout = () => userManager.signoutRedirect();

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      {!user && <button onClick={login}>Login with Keycloak</button>}
      {user && (
        <>
          <h2>Token</h2>
          <pre style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(user)}</pre>
          <button onClick={logout} style={{ marginTop: '1rem' }}>
            Logout
          </button>
        </>
      )}
    </div>
  );
};

export default App;