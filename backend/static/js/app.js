/**
 * IdentityAI - Minimalist Frontend Controller
 */

// Application State
const state = {
  sessionId: localStorage.getItem("identity_session_id") || "",
  profile: {
    name: "",
    logo: "",
    website: "",
    description: ""
  },
  provider: {
    active: "ollama",
    model: "llama3.2",
    isLocal: true,
    connected: false,
    statusMsg: "Not configured"
  },
  currentView: "landing",
  analysisData: null,
  patentsData: [],
  sources: [],
  activeTab: "detections" // 'detections' or 'patents'
};

// Initialize App
document.addEventListener("DOMContentLoaded", async () => {
  await initSession();
  setupEventListeners();
  updateLandingCardBadges();
  await loadProviderStatus();
  await loadSources();
});

// Session Initialization
async function initSession() {
  if (!state.sessionId) {
    try {
      const res = await fetch("/api/providers/status");
      state.sessionId = res.headers.get("x-session-id") || Math.random().toString(36).substring(2, 15);
      localStorage.setItem("identity_session_id", state.sessionId);
    } catch (e) {
      state.sessionId = "session-" + Math.random().toString(36).substring(2, 9);
    }
  }
}

// Navigation & Dynamic Section Switching
function navigateTo(viewId) {
  state.currentView = viewId;
  document.querySelectorAll(".view-section").forEach(sec => sec.classList.remove("active"));
  
  const target = document.getElementById(`view-${viewId}`);
  if (target) {
    target.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  updateLandingCardBadges();

  if (viewId === "review") {
    renderReviewScreen();
  }
}

// UI State Updates for Landing Cards
function updateLandingCardBadges() {
  const nameBadge = document.getElementById("badge-card-name");
  const logoBadge = document.getElementById("badge-card-logo");
  const webBadge = document.getElementById("badge-card-web");
  const descBadge = document.getElementById("badge-card-desc");

  if (nameBadge) {
    nameBadge.textContent = state.profile.name ? "Entered" : "Required";
    nameBadge.className = `primary-card-status ${state.profile.name ? "filled" : ""}`;
  }
  if (logoBadge) {
    logoBadge.textContent = state.profile.logo ? "Uploaded" : "Optional";
    logoBadge.className = `primary-card-status ${state.profile.logo ? "filled" : ""}`;
  }
  if (webBadge) {
    webBadge.textContent = state.profile.website ? "Entered" : "Optional";
    webBadge.className = `primary-card-status ${state.profile.website ? "filled" : ""}`;
  }
  if (descBadge) {
    descBadge.textContent = state.profile.description ? "Entered" : "Optional";
    descBadge.className = `primary-card-status ${state.profile.description ? "filled" : ""}`;
  }

  // Update Start Button on Landing
  const startBtn = document.getElementById("landing-review-btn");
  if (startBtn) {
    startBtn.style.display = state.profile.name ? "flex" : "none";
  }
}

// Review Screen Rendering
function renderReviewScreen() {
  document.getElementById("review-name-val").textContent = state.profile.name || "—";
  
  const logoBox = document.getElementById("review-logo-box");
  if (state.profile.logo) {
    logoBox.innerHTML = `<img src="${state.profile.logo}" class="logo-preview-img" alt="Logo preview" />`;
  } else {
    logoBox.textContent = "None provided";
  }

  document.getElementById("review-web-val").textContent = state.profile.website || "None provided";
  document.getElementById("review-desc-val").textContent = state.profile.description || "None provided";
  document.getElementById("review-model-val").textContent = state.provider.model || "llama3.2";

  // Provider note in review
  const providerNotice = document.getElementById("review-provider-notice");
  if (providerNotice) {
    if (state.provider.isLocal) {
      providerNotice.textContent = `Running privately with local provider (${state.provider.active} - ${state.provider.model}). Data stays strictly on this device.`;
    } else {
      providerNotice.textContent = `Will be analyzed using cloud provider (${state.provider.active} - ${state.provider.model}). Cloud providers receive brand metadata under their privacy policy.`;
    }
  }
}

// Event Listeners Setup
function setupEventListeners() {
  // Landing cards clicks
  document.getElementById("card-name").addEventListener("click", () => navigateTo("name"));
  document.getElementById("card-logo").addEventListener("click", () => navigateTo("logo"));
  document.getElementById("card-web").addEventListener("click", () => navigateTo("website"));
  document.getElementById("card-desc").addEventListener("click", () => navigateTo("description"));

  // Input bindings
  const nameInput = document.getElementById("input-brand-name");
  nameInput.addEventListener("input", (e) => {
    state.profile.name = e.target.value.trim();
  });

  const webInput = document.getElementById("input-brand-web");
  webInput.addEventListener("input", (e) => {
    state.profile.website = e.target.value.trim();
  });

  const descInput = document.getElementById("input-brand-desc");
  descInput.addEventListener("input", (e) => {
    state.profile.description = e.target.value.trim();
  });

  // Logo file drag & drop + upload
  const dropzone = document.getElementById("logo-dropzone");
  const fileInput = document.getElementById("logo-file-input");

  dropzone.addEventListener("click", () => fileInput.click());
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  });
  dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
    if (e.dataTransfer.files.length) {
      handleLogoFile(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length) {
      handleLogoFile(e.target.files[0]);
    }
  });

  document.getElementById("remove-logo-btn")?.addEventListener("click", (e) => {
    e.stopPropagation();
    state.profile.logo = "";
    document.getElementById("logo-preview-container").style.display = "none";
    document.getElementById("logo-dropzone").style.display = "block";
    fileInput.value = "";
    updateLandingCardBadges();
  });

  // Modal toggles
  document.getElementById("open-settings-btn").addEventListener("click", openSettingsModal);
  document.getElementById("close-settings-btn").addEventListener("click", closeSettingsModal);
  document.getElementById("settings-modal").addEventListener("click", (e) => {
    if (e.target.id === "settings-modal") closeSettingsModal();
  });

  document.getElementById("open-sources-btn").addEventListener("click", openSourcesModal);
  document.getElementById("close-sources-btn").addEventListener("click", closeSourcesModal);
  document.getElementById("sources-modal").addEventListener("click", (e) => {
    if (e.target.id === "sources-modal") closeSourcesModal();
  });

  // Provider Settings Handlers
  document.getElementById("provider-select").addEventListener("change", handleProviderSelectChange);
  document.getElementById("test-connection-btn").addEventListener("click", testProviderConnection);
  document.getElementById("disconnect-btn").addEventListener("click", disconnectProvider);
  document.getElementById("toggle-key-visibility").addEventListener("click", toggleKeyVisibility);

  // Ollama Scanning with Explicit User Permission
  document.getElementById("ollama-scan-btn").addEventListener("click", scanLocalhostForOllama);
  document.getElementById("reset-ollama-port-btn")?.addEventListener("click", () => {
    document.getElementById("ollama-base-url").value = "http://localhost:11434";
    document.getElementById("ollama-scan-indicator").textContent = "Reset to default port 11434. Click 'Allow & Scan Localhost' to connect.";
  });
  document.getElementById("ollama-quick-connect-btn")?.addEventListener("click", () => {
    testProviderConnection();
  });

  // Custom Source Creation
  document.getElementById("add-custom-source-btn")?.addEventListener("click", handleAddCustomSource);

  // Analysis trigger
  document.getElementById("start-analysis-btn").addEventListener("click", runAnalysis);
}

// Logo Handling
function handleLogoFile(file) {
  if (!file.type.startsWith("image/")) {
    alert("Please upload an image file (PNG, SVG, or JPG).");
    return;
  }
  const reader = new FileReader();
  reader.onload = (e) => {
    state.profile.logo = e.target.result;
    document.getElementById("logo-preview-img").src = state.profile.logo;
    document.getElementById("logo-preview-container").style.display = "flex";
    document.getElementById("logo-dropzone").style.display = "none";
    updateLandingCardBadges();
  };
  reader.readAsDataURL(file);
}

// AI Settings Operations
async function loadProviderStatus() {
  try {
    const res = await fetch("/api/providers/status", {
      headers: { "x-session-id": state.sessionId }
    });
    if (res.ok) {
      const data = await res.json();
      state.provider.active = data.provider;
      state.provider.model = data.model;
      state.provider.isLocal = data.is_local;
      state.provider.connected = data.connected;
      state.provider.statusMsg = data.message;
      updateHeaderPill();
    }
  } catch (err) {
    console.error("Provider status load failed", err);
  }
}

function updateHeaderPill() {
  const pill = document.getElementById("provider-status-pill");
  if (!pill) return;
  const isLocal = state.provider.isLocal;
  pill.textContent = `${state.provider.active.toUpperCase()}: ${state.provider.model} (${isLocal ? "Local" : "Cloud"})`;
}

function openSettingsModal() {
  document.getElementById("settings-modal").classList.add("active");
  document.getElementById("provider-select").value = state.provider.active;
  document.getElementById("custom-model-input").value = state.provider.model || "";
  handleProviderSelectChange();
}

function closeSettingsModal() {
  document.getElementById("settings-modal").classList.remove("active");
}

function handleProviderSelectChange() {
  const prov = document.getElementById("provider-select").value;
  const keyGroup = document.getElementById("api-key-group");
  const localNotice = document.getElementById("local-processing-notice");
  const cloudNotice = document.getElementById("cloud-processing-notice");
  const ollamaEndpoint = document.getElementById("ollama-endpoint-group");
  const ollamaScanSection = document.getElementById("ollama-scan-section");

  if (prov === "ollama") {
    keyGroup.style.display = "none";
    ollamaEndpoint.style.display = "block";
    ollamaScanSection.style.display = "block";
    localNotice.style.display = "block";
    cloudNotice.style.display = "none";
  } else {
    keyGroup.style.display = "block";
    ollamaEndpoint.style.display = "none";
    ollamaScanSection.style.display = "none";
    localNotice.style.display = "none";
    cloudNotice.style.display = "block";
  }

  loadModelOptions(prov);
}

async function loadModelOptions(provider) {
  const modelSelect = document.getElementById("model-select");
  modelSelect.innerHTML = "<option>Loading models...</option>";
  try {
    const res = await fetch(`/api/providers/models?provider=${provider}`);
    if (res.ok) {
      const data = await res.json();
      modelSelect.innerHTML = "";
      data.models.forEach(m => {
        const opt = document.createElement("option");
        opt.value = m;
        opt.textContent = m;
        modelSelect.appendChild(opt);
      });
      // Add custom option
      const customOpt = document.createElement("option");
      customOpt.value = "custom";
      customOpt.textContent = "+ Custom model (specified below)";
      modelSelect.appendChild(customOpt);
    }
  } catch (e) {
    modelSelect.innerHTML = "<option value='default'>Standard</option>";
  }
}

// Ollama Localhost Scanning with Explicit Permission
async function scanLocalhostForOllama() {
  const btn = document.getElementById("ollama-scan-btn");
  const indicator = document.getElementById("ollama-scan-indicator");
  const discoveredBox = document.getElementById("ollama-discovered-box");
  const tagsContainer = document.getElementById("ollama-model-tags");
  const endpoint = document.getElementById("ollama-base-url").value || "http://localhost:11434";

  btn.disabled = true;
  btn.textContent = "Scanning...";
  indicator.textContent = "Querying localhost:11434 with your consent...";

  try {
    const res = await fetch("/api/providers/ollama/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        permission_granted: true,
        base_url: endpoint
      })
    });

    const data = await res.json();
    if (data.running) {
      const activeEndpoint = data.endpoint || endpoint;
      document.getElementById("ollama-base-url").value = activeEndpoint;
      indicator.innerHTML = `<span style="color: #248a3d; font-weight: 600;">✓ Connected to Ollama on ${activeEndpoint}</span>`;
      discoveredBox.style.display = "block";
      tagsContainer.innerHTML = "";

      if (data.installed_models && data.installed_models.length > 0) {
        data.installed_models.forEach(m => {
          const pill = document.createElement("button");
          pill.className = "model-tag";
          pill.type = "button";
          pill.textContent = m;
          pill.onclick = () => {
            document.querySelectorAll(".model-tag").forEach(t => t.classList.remove("selected"));
            pill.classList.add("selected");
            document.getElementById("custom-model-input").value = m;
            document.getElementById("model-select").value = m;
          };
          tagsContainer.appendChild(pill);
        });
        // Select the first installed model by default
        tagsContainer.firstChild.click();
      } else {
        tagsContainer.innerHTML = "<span style='font-size: 12px; color: var(--text-tertiary);'>No models downloaded yet. Run 'ollama pull llama3.2' in terminal.</span>";
      }
    } else {
      indicator.innerHTML = `<span style="color: #d70015; font-weight: 500;">✗ ${data.message || "Ollama is not running on localhost."}</span>`;
      discoveredBox.style.display = "none";
    }
  } catch (err) {
    indicator.innerHTML = `<span style="color: #d70015; font-weight: 500;">✗ Could not reach local Ollama daemon.</span>`;
    discoveredBox.style.display = "none";
  } finally {
    btn.disabled = false;
    btn.textContent = "Re-Scan Localhost";
  }
}

// Test Provider Connection
async function testProviderConnection() {
  const btn = document.getElementById("test-connection-btn");
  const statusEl = document.getElementById("provider-test-status");
  const prov = document.getElementById("provider-select").value;
  const key = document.getElementById("provider-api-key").value;
  const customModel = document.getElementById("custom-model-input").value.trim();
  const dropdownModel = document.getElementById("model-select").value;
  const baseUrl = document.getElementById("ollama-base-url")?.value || "";

  // Custom model input takes priority if specified
  const effectiveModel = customModel || (dropdownModel === "custom" ? "llama3.2" : dropdownModel);

  btn.disabled = true;
  btn.innerHTML = `<span class="loading-spinner"></span> Connecting...`;
  statusEl.style.display = "none";

  try {
    const res = await fetch("/api/providers/configure", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-session-id": state.sessionId
      },
      body: JSON.stringify({
        provider: prov,
        api_key: key,
        model: effectiveModel,
        base_url: baseUrl
      })
    });

    const data = await res.json();
    if (res.ok) {
      statusEl.style.display = "block";
      statusEl.className = "input-hint badge-verified";
      if (data.base_url) {
        document.getElementById("ollama-base-url").value = data.base_url;
      }
      statusEl.textContent = `✓ ${data.message || "Connected successfully."}`;
      state.provider.active = prov;
      state.provider.model = effectiveModel;
      state.provider.connected = true;
      state.provider.isLocal = (prov === "ollama");
      updateHeaderPill();
      renderReviewScreen();
    } else {
      statusEl.style.display = "block";
      statusEl.className = "input-hint badge-possible";
      statusEl.textContent = `✗ ${data.detail || "Connection failed."}`;
    }
  } catch (err) {
    statusEl.style.display = "block";
    statusEl.className = "input-hint badge-possible";
    statusEl.textContent = "✗ Network error testing connection.";
  } finally {
    btn.disabled = false;
    btn.textContent = "Connect & Test";
  }
}

async function disconnectProvider() {
  await fetch("/api/providers/disconnect", {
    method: "POST",
    headers: { "x-session-id": state.sessionId }
  });
  document.getElementById("provider-api-key").value = "";
  const statusEl = document.getElementById("provider-test-status");
  statusEl.style.display = "block";
  statusEl.className = "input-hint";
  statusEl.textContent = "Provider credentials purged from memory.";
  await loadProviderStatus();
}

function toggleKeyVisibility() {
  const input = document.getElementById("provider-api-key");
  const btn = document.getElementById("toggle-key-visibility");
  if (input.type === "password") {
    input.type = "text";
    btn.textContent = "Hide";
  } else {
    input.type = "password";
    btn.textContent = "Show";
  }
}

// Sources Modal Handling
async function loadSources() {
  try {
    const res = await fetch("/api/sources");
    if (res.ok) {
      state.sources = await res.json();
      renderSourcesList();
    }
  } catch (e) {
    console.error("Sources load error", e);
  }
}

function openSourcesModal() {
  document.getElementById("sources-modal").classList.add("active");
  renderSourcesList();
}

function closeSourcesModal() {
  document.getElementById("sources-modal").classList.remove("active");
}

function renderSourcesList() {
  const container = document.getElementById("sources-list-container");
  if (!container) return;
  container.innerHTML = "";

  state.sources.forEach(s => {
    const row = document.createElement("div");
    row.className = "review-item";
    row.innerHTML = `
      <div>
        <div style="font-weight: 600; font-size: 14px;">
          ${s.name}
          ${s.id.startsWith('custom_') ? '<span class="badge badge-clean" style="margin-left: 6px;">Custom</span>' : ''}
        </div>
        <div style="font-size: 12px; color: var(--text-secondary);">${s.description}</div>
      </div>
      <div>
        <button class="pill-button ${s.enabled ? 'active' : ''}" onclick="toggleSource('${s.id}', ${!s.enabled})">
          ${s.enabled ? 'Active' : 'Disabled'}
        </button>
      </div>
    `;
    container.appendChild(row);
  });
}

window.toggleSource = async function(id, enable) {
  try {
    const res = await fetch("/api/sources/toggle", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ source_id: id, enabled: enable })
    });
    if (res.ok) {
      await loadSources();
    }
  } catch (e) {
    console.error("Toggle error", e);
  }
};

async function handleAddCustomSource() {
  const nameInput = document.getElementById("custom-src-name");
  const categoryInput = document.getElementById("custom-src-category");
  const urlInput = document.getElementById("custom-src-url");
  const descInput = document.getElementById("custom-src-desc");

  const name = nameInput.value.trim();
  const category = categoryInput.value.trim() || "Custom";
  const url = urlInput.value.trim();
  const desc = descInput.value.trim();

  if (!name || !desc) {
    alert("Please provide a Source Name and Description.");
    return;
  }

  try {
    const res = await fetch("/api/sources/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: name,
        category: category,
        url: url || null,
        description: desc
      })
    });

    if (res.ok) {
      nameInput.value = "";
      categoryInput.value = "";
      urlInput.value = "";
      descInput.value = "";
      await loadSources();
    } else {
      alert("Failed to add custom source.");
    }
  } catch (err) {
    console.error("Custom source add error", err);
  }
}

// Analysis Execution Flow
async function runAnalysis() {
  if (!state.profile.name) {
    alert("Please enter a Brand Name first.");
    navigateTo("name");
    return;
  }

  navigateTo("analyzing");
  const progressText = document.getElementById("analysis-step-text");

  // Animated Real-Step Progression
  progressText.textContent = "Preparing brand profile & cryptographic hash...";
  await new Promise(r => setTimeout(r, 600));

  progressText.textContent = "Querying authorized search & custom source connectors...";
  await new Promise(r => setTimeout(r, 700));

  progressText.textContent = `Synthesizing evidence via ${state.provider.active.toUpperCase()} (${state.provider.model})...`;

  try {
    const [analysisRes, patentsRes] = await Promise.all([
      fetch("/api/analysis", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-session-id": state.sessionId
        },
        body: JSON.stringify(state.profile)
      }),
      fetch(`/api/patents?brand=${encodeURIComponent(state.profile.name)}`)
    ]);

    if (!analysisRes.ok) {
      throw new Error("Analysis failed. Verify your AI provider settings.");
    }

    state.analysisData = await analysisRes.json();
    state.patentsData = await patentsRes.json();

    renderResults();
    navigateTo("results");
  } catch (err) {
    alert(err.message || "An unexpected error occurred during analysis.");
    navigateTo("review");
  }
}

// Render Results View
function renderResults() {
  const d = state.analysisData;
  if (!d) return;

  document.getElementById("results-brand-title").textContent = d.brand_name;
  document.getElementById("results-summary-text").textContent = d.summary;
  document.getElementById("results-provider-badge").textContent = `${d.provider_used} (${d.model_used})`;

  // Render Detections List
  renderDetectionsTab();
  renderPatentsTab();
}

function renderDetectionsTab() {
  const container = document.getElementById("detections-container");
  container.innerHTML = "";

  if (!state.analysisData.items || state.analysisData.items.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px 20px; color: var(--text-tertiary);">
        No matching candidate items found in the sources checked.
      </div>
    `;
    return;
  }

  state.analysisData.items.forEach(item => {
    const row = document.createElement("div");
    row.className = "result-row glass-panel";

    let badgeClass = "badge-review";
    if (item.status === "Verified") badgeClass = "badge-verified";
    else if (item.status === "Possible match") badgeClass = "badge-possible";
    else if (item.status === "No evidence") badgeClass = "badge-clean";

    row.innerHTML = `
      <div class="result-main">
        <div class="result-title-bar">
          <span class="badge ${badgeClass}">${item.status}</span>
          <span class="result-title">${item.title}</span>
          ${item.is_official ? '<span class="badge badge-clean">Official Asset</span>' : ''}
        </div>
        <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="result-url">
          ${item.url} ↗
        </a>
        <div class="result-reason">${item.reason}</div>
        <div class="result-meta">
          <span>Source: ${item.source_name}</span>
          <span>•</span>
          <span>Confidence: ${(item.confidence * 100).toFixed(0)}% (heuristic)</span>
          ${item.timestamp ? `<span>•</span><span>Date: ${item.timestamp}</span>` : ''}
        </div>
      </div>
    `;
    container.appendChild(row);
  });
}

function renderPatentsTab() {
  const container = document.getElementById("patents-container");
  container.innerHTML = "";

  if (!state.patentsData || state.patentsData.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 40px 20px; color: var(--text-tertiary);">
        No intellectual property filings found for this query in connected registries.
      </div>
    `;
    return;
  }

  state.patentsData.forEach(p => {
    const row = document.createElement("div");
    row.className = "result-row glass-panel";
    row.innerHTML = `
      <div class="result-main">
        <div class="result-title-bar">
          <span class="badge badge-verified">${p.record_type}</span>
          <span class="result-title">${p.title}</span>
        </div>
        <div style="font-size: 13px; font-weight: 500; color: var(--text-primary); margin: 3px 0;">
          ${p.identifier} — ${p.owner}
        </div>
        <div class="result-reason">${p.relevance_explanation}</div>
        <div class="result-meta">
          <span>Registered: ${p.registration_date}</span>
          <span>•</span>
          <a href="${p.source_url}" target="_blank" rel="noopener noreferrer" class="result-url" style="color: var(--accent);">
            Verify Record ↗
          </a>
        </div>
      </div>
    `;
    container.appendChild(row);
  });
}

// Tab Switching on Results Screen
window.switchResultsTab = function(tab) {
  state.activeTab = tab;
  document.getElementById("tab-btn-detections").className = `pill-button ${tab === 'detections' ? 'active' : ''}`;
  document.getElementById("tab-btn-patents").className = `pill-button ${tab === 'patents' ? 'active' : ''}`;

  if (tab === "detections") {
    document.getElementById("detections-container").style.display = "block";
    document.getElementById("patents-container").style.display = "none";
  } else {
    document.getElementById("detections-container").style.display = "none";
    document.getElementById("patents-container").style.display = "block";
  }
};
