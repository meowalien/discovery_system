// App.tsx
import React, { useState } from 'react';
import { useKeycloak } from '@react-keycloak/web';

const App: React.FC = () => {
  const { keycloak, initialized } = useKeycloak();
  // 使用 state 儲存 log 訊息（可選）
  const [log, setLog] = useState('');

  // 幫助函式：新增日誌訊息
  const logToTextarea = (message: string) => {
    const now = new Date();
    const timestamp = now.toLocaleString();
    console.log(message);
    setLog(prevLog => prevLog + `[${timestamp}] ${message}\n`);
  };

  // 按鈕點擊處理函式
  const handleLogin = () => {
    logToTextarea('Login button clicked');
    keycloak.login();
  };

  const handleLogout = () => {
    logToTextarea('Logout button clicked');
    keycloak.logout();
  };

  const handleIsLoggedIn = () => {
    const message = keycloak.authenticated ? 'User is logged in' : 'User is not logged in';
    logToTextarea(`Is Logged In button clicked: ${message}`);
    alert(message);
  };

  const handleAccessToken = () => {
    if (keycloak.authenticated) {
      logToTextarea(`Access Token button clicked: ${keycloak.token}`);
      alert('Access Token: ' + keycloak.token);
    } else {
      const message = 'User is not logged in';
      logToTextarea(`Access Token button clicked: ${message}`);
      alert(message);
    }
  };

  const handleShowParsedToken = () => {
    if (keycloak.authenticated) {
      const formattedToken = JSON.stringify(keycloak.tokenParsed, null, 2);
      logToTextarea(`Show Parsed Access Token button clicked: ${formattedToken}`);
      alert('Parsed Access Token: ' + formattedToken);
    } else {
      const message = 'User is not logged in';
      logToTextarea(`Show Parsed Access Token button clicked: ${message}`);
      alert(message);
    }
  };

  const handleCallApi = () => {
    logToTextarea('Call API button clicked');
    if (keycloak.authenticated) {
      fetch('https://4b215443be964e33bc1ef0373940400c.api.mockbin.io/', {
        headers: {
          'Authorization': 'Bearer ' + keycloak.token,
        },
      })
        .then(response => response.json())
        .then(data => {
          logToTextarea('API call successful: ' + JSON.stringify(data));
          console.log(data);
        })
        .catch(error => {
          logToTextarea('API call failed: ' + error);
          console.error('Error:', error);
        });
    } else {
      const message = 'User is not logged in';
      logToTextarea('API call failed: ' + message);
      alert(message);
    }
  };

  // 如果 Keycloak 尚未初始化，可以顯示 loading 畫面（可選）
  if (!initialized) {
    return <div>Loading...</div>;
  }

  return (
    <div className="container">
      <div className="jumbotron mt-4">
        <h1 className="display-4">
          Keycloak - Javascript Integration (React with react-keycloak)
        </h1>
        <p className="lead">A React web app using react-keycloak for authentication</p>
        <div className="mt-4">
          <button id="loginBtn" className="btn btn-primary mr-2" onClick={handleLogin}>
            Login
          </button>
          <button id="logoutBtn" className="btn btn-secondary mr-2" onClick={handleLogout}>
            Logout
          </button>
          <button id="isLoggedInBtn" className="btn btn-info mr-2" onClick={handleIsLoggedIn}>
            Is Logged In
          </button>
          <button id="accessTokenBtn" className="btn btn-warning mr-2" onClick={handleAccessToken}>
            Access Token
          </button>
          <button id="showParsedTokenBtn" className="btn btn-dark mr-2" onClick={handleShowParsedToken}>
            Show Parsed Access Token
          </button>
          <button id="callApiBtn" className="btn btn-success mr-2" onClick={handleCallApi}>
            Call API
          </button>
        </div>
        <div className="mt-4">
          <textarea
            id="output"
            className="form-control"
            rows={5}
            value={log}
            readOnly
            placeholder="Output will be displayed here..."
          />
        </div>
      </div>
    </div>
  );
};

export default App;