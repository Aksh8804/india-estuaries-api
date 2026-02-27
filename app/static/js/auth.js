const API_BASE = "http://127.0.0.1:8000";

// ================= TOKEN STORAGE =================
function setToken(token) {
    localStorage.setItem("access_token", token);
}

function getToken() {
    return localStorage.getItem("access_token");
}

function clearToken() {
    localStorage.removeItem("access_token");
}

// ================= AUTH CHECK =================
function requireAuth() {
    const token = getToken();
    if (!token) {
        window.location.href = "/login.html";
    }
}

// ================= FETCH WITH AUTH =================
async function authFetch(url, options = {}) {
    const token = getToken();

    options.headers = {
        ...(options.headers || {}),
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json"
    };

    const response = await fetch(url, options);

    if (response.status === 401) {
        clearToken();
        window.location.href = "/login.html";
    }

    return response;
}

// ================= LOGOUT =================
function logout() {
    clearToken();
    window.location.href = "/login.html";
}