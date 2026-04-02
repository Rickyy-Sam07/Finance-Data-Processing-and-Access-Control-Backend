const state = {
  token: localStorage.getItem("token") || "",
  user: null,
  recordsMeta: null,
};

const loginSection = document.getElementById("loginSection");
const dashboardSection = document.getElementById("dashboardSection");
const roleBadge = document.getElementById("roleBadge");
const recordsSection = document.getElementById("recordsSection");
const usersSection = document.getElementById("usersSection");
const adminCreateBox = document.getElementById("adminCreateBox");

function formatCurrency(value) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value || 0);
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (state.token) headers.Authorization = `Bearer ${state.token}`;

  const response = await fetch(path, { ...options, headers });
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Request failed");
  }

  if (response.status === 204) return null;
  return response.json();
}

function showDashboard() {
  loginSection.classList.add("hidden");
  dashboardSection.classList.remove("hidden");
}

function showLogin() {
  dashboardSection.classList.add("hidden");
  loginSection.classList.remove("hidden");
}

function applyRoleVisibility() {
  const role = state.user.role;
  roleBadge.textContent = `${role} access`;

  const canReadRecords = role === "analyst" || role === "admin";
  const isAdmin = role === "admin";

  recordsSection.classList.toggle("hidden", !canReadRecords);
  usersSection.classList.toggle("hidden", !isAdmin);
  adminCreateBox.classList.toggle("hidden", !isAdmin);
}

function renderSummaryCards(summary) {
  const cards = [
    { label: "Total Income", value: formatCurrency(summary.total_income) },
    { label: "Total Expenses", value: formatCurrency(summary.total_expenses) },
    { label: "Net Balance", value: formatCurrency(summary.net_balance) },
    { label: "Recent Activity (7d)", value: String(summary.recent_activity_count) },
  ];

  document.getElementById("summaryCards").innerHTML = cards
    .map((card) => `<article class="panel card"><div class="label">${card.label}</div><div class="value">${card.value}</div></article>`)
    .join("");
}

function renderCharts(summary) {
  renderTrendChart(summary.monthly_trends || []);
  renderCategoryBars(summary.category_totals || []);
}

function renderTrendChart(points) {
  const container = document.getElementById("trendChart");
  if (!points.length) {
    container.innerHTML = `<p class="chart-empty">No trend data available.</p>`;
    return;
  }

  const width = 680;
  const height = 260;
  const pad = 34;
  const values = points.flatMap((p) => [p.income, p.expense]);
  const maxVal = Math.max(...values, 1);

  const x = (i) => pad + (i * (width - 2 * pad)) / Math.max(points.length - 1, 1);
  const y = (v) => height - pad - (v / maxVal) * (height - 2 * pad);

  const incomePath = points.map((p, i) => `${i === 0 ? "M" : "L"}${x(i)},${y(p.income)}`).join(" ");
  const expensePath = points.map((p, i) => `${i === 0 ? "M" : "L"}${x(i)},${y(p.expense)}`).join(" ");

  const incomeDots = points
    .map(
      (p, i) =>
        `<circle cx="${x(i)}" cy="${y(p.income)}" r="4" fill="#227f76"><title>${p.month}: Income ${p.income}</title></circle>`
    )
    .join("");
  const expenseDots = points
    .map(
      (p, i) =>
        `<circle cx="${x(i)}" cy="${y(p.expense)}" r="4" fill="#cf4f2a"><title>${p.month}: Expense ${p.expense}</title></circle>`
    )
    .join("");

  const valueLabels = points
    .map(
      (p, i) =>
        `<text x="${x(i)}" y="${Math.max(y(p.income) - 8, pad + 14)}" text-anchor="middle" font-size="10" fill="#227f76">${Math.round(p.income)}</text>
         <text x="${x(i)}" y="${Math.max(y(p.expense) - 8, pad + 14)}" text-anchor="middle" font-size="10" fill="#cf4f2a">${Math.round(p.expense)}</text>`
    )
    .join("");

  const labels = points
    .map((p, i) => `<text x="${x(i)}" y="${height - 10}" text-anchor="middle" font-size="10" fill="#5b6270">${p.month}</text>`)
    .join("");

  container.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" width="100%" height="280" role="img" aria-label="Monthly income and expense trend">
      <line x1="${pad}" y1="${pad}" x2="${pad}" y2="${height - pad}" stroke="#cfcabf" />
      <line x1="${pad}" y1="${height - pad}" x2="${width - pad}" y2="${height - pad}" stroke="#cfcabf" />
      ${labels}
      <path d="${incomePath}" fill="none" stroke="#227f76" stroke-width="3" />
      <path d="${expensePath}" fill="none" stroke="#cf4f2a" stroke-width="3" />
      ${incomeDots}
      ${expenseDots}
      ${valueLabels}
      <text x="${pad + 8}" y="${pad + 12}" font-size="11" fill="#227f76">Income</text>
      <text x="${pad + 70}" y="${pad + 12}" font-size="11" fill="#cf4f2a">Expense</text>
    </svg>`;
}

function renderCategoryBars(categories) {
  const container = document.getElementById("categoryChart");
  if (!categories.length) {
    container.innerHTML = `<p class="chart-empty">No category data available.</p>`;
    return;
  }

  const maxVal = Math.max(...categories.map((c) => c.total), 1);
  container.innerHTML = `<div class="category-bars">${categories
    .slice(0, 8)
    .map((c) => {
      const pct = Math.round((c.total / maxVal) * 100);
      return `<div class="bar-row">
        <div class="bar-label"><span>${c.category}</span><span>${formatCurrency(c.total)}</span></div>
        <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
      </div>`;
    })
    .join("")}</div>`;
}

function renderRecords(records, meta = null) {
  const body = document.getElementById("recordsTableBody");
  const totalLabel = document.getElementById("recordsMeta");
  if (totalLabel) {
    if (meta) {
      totalLabel.textContent = `Showing ${records.length} of ${meta.total} records`;
    } else {
      totalLabel.textContent = `Showing ${records.length} records`;
    }
  }

  if (!records.length) {
    body.innerHTML = `<tr><td colspan="6" class="muted">No records match your filters.</td></tr>`;
    return;
  }

  body.innerHTML = records
    .map(
      (r) => `<tr>
        <td>${r.id}</td>
        <td>${r.record_date}</td>
        <td>${r.type}</td>
        <td>${r.category}</td>
        <td>${formatCurrency(r.amount)}</td>
        <td>${r.notes || "-"}</td>
      </tr>`
    )
    .join("");
}

function renderUsers(users) {
  const body = document.getElementById("usersTableBody");
  body.innerHTML = users
    .map(
      (u) => `<tr>
        <td>${u.id}</td>
        <td>${u.email}</td>
        <td>${u.full_name}</td>
        <td>${u.role}</td>
        <td>${u.is_active ? "active" : "inactive"}</td>
      </tr>`
    )
    .join("");
}

async function loadDashboardData() {
  const summary = await api("/dashboard/summary");
  renderSummaryCards(summary);
  renderCharts(summary);

  if (state.user.role === "analyst" || state.user.role === "admin") {
    const search = document.getElementById("filterSearch").value.trim();
    const category = document.getElementById("filterCategory").value.trim();
    const type = document.getElementById("filterType").value;
    const qs = new URLSearchParams();
    if (search) qs.set("q", search);
    if (category) qs.set("category", category);
    if (type) qs.set("record_type", type);

    const recordsPayload = await api(`/records${qs.toString() ? `?${qs.toString()}` : ""}`);
    state.recordsMeta = recordsPayload;
    renderRecords(recordsPayload.items || [], recordsPayload);
  }

  if (state.user.role === "admin") {
    const users = await api("/users");
    renderUsers(users);
  }
}

async function bootstrapSession() {
  if (!state.token) {
    showLogin();
    return;
  }

  try {
    state.user = await api("/auth/me");
    applyRoleVisibility();
    showDashboard();
    await loadDashboardData();
  } catch (e) {
    localStorage.removeItem("token");
    state.token = "";
    showLogin();
  }
}

document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  document.getElementById("loginError").textContent = "";

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  try {
    const result = await api("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    state.token = result.access_token;
    localStorage.setItem("token", state.token);
    await bootstrapSession();
  } catch (err) {
    document.getElementById("loginError").textContent = err.message;
  }
});

document.getElementById("logoutBtn").addEventListener("click", () => {
  localStorage.removeItem("token");
  state.token = "";
  state.user = null;
  showLogin();
});

document.getElementById("applyFiltersBtn").addEventListener("click", async () => {
  if (!state.user) return;
  await loadDashboardData();
});

document.getElementById("createRecordForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  document.getElementById("createRecordError").textContent = "";

  try {
    await api("/records", {
      method: "POST",
      body: JSON.stringify({
        amount: Number(document.getElementById("newAmount").value),
        type: document.getElementById("newType").value,
        category: document.getElementById("newCategory").value,
        record_date: document.getElementById("newDate").value,
        notes: document.getElementById("newNotes").value,
      }),
    });
    e.target.reset();
    await loadDashboardData();
  } catch (err) {
    document.getElementById("createRecordError").textContent = err.message;
  }
});

document.getElementById("createUserForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  document.getElementById("createUserError").textContent = "";

  try {
    await api("/users", {
      method: "POST",
      body: JSON.stringify({
        email: document.getElementById("newUserEmail").value.trim(),
        full_name: document.getElementById("newUserName").value.trim(),
        password: document.getElementById("newUserPassword").value,
        role: document.getElementById("newUserRole").value,
      }),
    });
    e.target.reset();
    await loadDashboardData();
  } catch (err) {
    document.getElementById("createUserError").textContent = err.message;
  }
});

bootstrapSession();
