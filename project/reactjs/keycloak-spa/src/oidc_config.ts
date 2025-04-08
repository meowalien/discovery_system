const oidcConfig = {
  authority: 'http://localhost:8082/realms/discovery_system', // 修改為你的 realm URL
  client_id: 'demo',                                   // 修改為你的 client ID
  redirect_uri: window.location.origin,                       // 必須與 Keycloak 設定吻合
  post_logout_redirect_uri: window.location.origin,

  // —— 关键配置 ——
  // response_type: 'code',
  // scope: 'openid profile email',
  // // scope: 'openid profile email offline_access',  // 加上 offline_access 拿到 refresh token
  // automaticSilentRenew: true,                     // 开启自动静默刷新
  // silent_redirect_uri: window.location.origin + '/silent-renew.html',  // 静默刷新的回调页
  // accessTokenExpiringNotificationTime: 60,       // 在过期前 60 秒触发 expiring 事件
};

export default oidcConfig;