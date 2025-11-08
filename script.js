const API_BASE = "http://127.0.0.1:5000";

// 🧠 Utility: Generic API call
async function api(path, opts = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    credentials: "include", // keeps session cookie if you use Flask sessions
    ...opts,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
  return data;
}

// -------------------------------
// 👤 REGISTER
// -------------------------------
async function registerUser() {
  const name = document.getElementById("regName")?.value.trim();
  const email = document.getElementById("regEmail")?.value.trim();
  const password = document.getElementById("regPassword")?.value.trim();
  const box = document.getElementById("registerMessage");

  if (!name || !email || !password) {
    box.innerHTML = `<div class="alert alert-warning">All fields are required.</div>`;
    return;
  }

  try {
    await api("/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    });
    box.innerHTML = `<div class="alert alert-success">Registration successful! Redirecting...</div>`;
    setTimeout(() => (window.location.href = "login.html"), 1200);
  } catch (err) {
    box.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

// -------------------------------
// 🔐 LOGIN
// -------------------------------
async function loginUser() {
  const email = document.getElementById("loginEmail")?.value.trim();
  const password = document.getElementById("loginPassword")?.value.trim();
  const box = document.getElementById("loginMessage");

  if (!email || !password) {
    box.innerHTML = `<div class="alert alert-warning">Please enter both email and password.</div>`;
    return;
  }

  try {
    const data = await api("/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });

    // Save user in localStorage
    localStorage.setItem("mc_user", JSON.stringify(data));

    box.innerHTML = `<div class="alert alert-success">Welcome ${data.message || "User"}!</div>`;
    setTimeout(() => (window.location.href = "index.html"), 1000);
  } catch (err) {
    box.innerHTML = `<div class="alert alert-danger">${err.message}</div>`;
  }
}

// -------------------------------
// 🚪 LOGOUT
// -------------------------------
async function logoutUser() {
  await api("/logout");
  localStorage.removeItem("mc_user");
  window.location.href = "login.html";
}

// -------------------------------
// 🏠 CHECK USER ON INDEX PAGE
// -------------------------------
function checkLogin() {
  const user = localStorage.getItem("mc_user");
  if (!user) {
    window.location.href = "login.html";
  } else {
    const u = JSON.parse(user);
    const userNameDiv = document.getElementById("welcomeUser");
    if (userNameDiv) userNameDiv.textContent = `👋 Welcome, ${u.user?.name || "User"}`;
  }
}

// Export to HTML
window.registerUser = registerUser;
window.loginUser = loginUser;
window.logoutUser = logoutUser;
window.checkLogin = checkLogin;
