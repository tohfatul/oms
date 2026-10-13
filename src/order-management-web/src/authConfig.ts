import type { Configuration } from "@azure/msal-browser";

const clientId = import.meta.env.VITE_ENTRA_CLIENT_ID;
const tenantId = import.meta.env.VITE_ENTRA_TENANT_ID;
const apiClientId = import.meta.env.VITE_OMS_API_CLIENT_ID;

export const msalConfig: Configuration = {
  auth: {
    clientId,
    // authority: `https://login.microsoftonline.com/${tenantId}`,
    authority: "https://login.microsoftonline.com/common",
    redirectUri: `${window.location.origin}/auth.html`,
    postLogoutRedirectUri: `${window.location.origin}/auth.html`,
  },
  cache: {
    cacheLocation: "sessionStorage",
  },
};

export const loginRequest = {
  scopes: [`api://${apiClientId}/access_as_user`],
};
