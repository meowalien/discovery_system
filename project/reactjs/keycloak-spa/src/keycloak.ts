// @ts-ignore
import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({
  url: 'http://localhost:8082',
  realm: 'discovery_system',
  clientId: 'demo',
});

// 使用一個變數來追蹤是否已經初始化過
let hasInitialized = false;
const originalInit = keycloak.init.bind(keycloak);

// 覆寫 init 方法，如果已經初始化過，直接回傳 Promise.resolve(keycloak.authenticated)
keycloak.init = (initOptions?: Keycloak.KeycloakInitOptions) => {
  if (hasInitialized) {
    // 已初始化過，直接回傳目前的登入狀態
    return Promise.resolve(keycloak.authenticated);
  }
  hasInitialized = true;
  return originalInit(initOptions);
};

export default keycloak;