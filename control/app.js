const $ = (id) => document.getElementById(id);
const labels = {overview:"Overview",installation:"Installation",updates:"Updates",usage:"Usage & evidence",design:"Design system",start:"Start here"};

function showPage(name) {
  if (!labels[name]) return;
  document.querySelectorAll(".page").forEach((page) => {
    const selected = page.id === `page-${name}`;
    page.hidden = !selected;
    page.classList.toggle("active", selected);
  });
  document.querySelectorAll(".nav-item").forEach((button) => {
    const selected = button.dataset.page === name;
    button.classList.toggle("active", selected);
    if (selected) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
  });
  $("pageTitle").textContent = labels[name];
  if (location.hash !== `#${name}`) history.replaceState(null, "", `#${name}`);
  window.scrollTo({top:0,behavior:"smooth"});
}

document.querySelectorAll(".nav-item").forEach((button) => button.addEventListener("click", () => showPage(button.dataset.page)));
document.querySelectorAll("[data-go]").forEach((button) => button.addEventListener("click", () => showPage(button.dataset.go)));
document.querySelector(".brand").addEventListener("click", (event) => {
  event.preventDefault();
  showPage("overview");
});
$("refreshButton").addEventListener("click", loadState);
const workflowRouteElement = $("workflowRoutes");
const capabilitySearch = $("capabilitySearch");
const capabilityTypeFilter = $("capabilityTypeFilter");
const capabilityDecisionElement = $("capabilityDecisions");
const capabilityResultElement = $("capabilityResults");
let capabilityRegistry = null;

function mark(element, kind) {
  if (!element) return;
  element.classList.remove("good", "unknown", "attention");
  element.classList.add(kind);
}

function display(value, fallback="Unknown") {
  return value === null || value === undefined ? fallback : String(value);
}

function populateAssets(assets) {
  const rows = $("assetRows");
  rows.replaceChildren();
  const names = {agents:"AGENTS",skills:"SKILLS",commands:"COMMANDS"};
  let total = 0;
  Object.entries(names).forEach(([key,label]) => {
    const count = Number(assets[key] || 0);
    total += count;
    const card = document.createElement("div");
    card.className = "capability";
    const title = document.createElement("span");
    title.textContent = label;
    const value = document.createElement("strong");
    value.textContent = count;
    card.append(title,value);
    rows.append(card);
  });
  $("assetCount").textContent = `${total} files in this checkout`;
}

function populateProgress(items) {
  const rows = $("progressRows");
  rows.replaceChildren();
  if (!Array.isArray(items) || items.length === 0) {
    const empty = document.createElement("p");
    empty.className = "footnote";
    empty.textContent = "No milestone evidence is available.";
    rows.append(empty);
    return;
  }
  items.forEach((item) => {
    const row = document.createElement("article");
    row.className = "progress-row";
    const copy = document.createElement("div");
    const title = document.createElement("h3");
    title.textContent = display(item.title);
    const detail = document.createElement("p");
    detail.textContent = display(item.detail);
    const state = document.createElement("span");
    state.className = "progress-state";
    state.textContent = display(item.status).replaceAll("_", " ");
    copy.append(title, detail);
    row.append(copy, state);
    rows.append(row);
  });
}

function populateInstall(installation, assets) {
  const stateLabels = {
    NOT_CHECKED:"Not checked",TARGET_NOT_FOUND:"Target not found",INSTALL_INCOMPLETE:"Needs installation",
    LOCAL_CHANGES_NEED_REVIEW:"Local changes need review",IN_SYNC_WITH_CHECKOUT:"In sync with checkout"
  };
  const state = stateLabels[installation.state] || "Unknown";
  const markKind = installation.state === "IN_SYNC_WITH_CHECKOUT" ? "good" : "unknown";
  $("installValue").textContent = state;
  $("installDetail").textContent = installation.target_configured
    ? `${display(installation.same,0)} matching; ${display(installation.missing,0)} missing; ${display(installation.changed,0)} changed.`
    : "Provide an existing OpenCode config directory.";
  mark($("installMark"),markKind);
  $("installationPill").textContent = state.toUpperCase();
  $("installationSummary").textContent = installation.target_configured
    ? `${display(installation.same,0)} matching · ${display(installation.missing,0)} missing · ${display(installation.changed,0)} changed`
    : "No target has been scanned";
  $("targetState").textContent = installation.state === "TARGET_NOT_FOUND" ? "Supplied path not found" : installation.target_configured ? "Explicit target supplied" : "Target not supplied";
  const body = $("installationRows");
  body.replaceChildren();
  if (!installation.target_configured || !installation.groups || !Object.keys(installation.groups).length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 5;
    cell.textContent = installation.state === "TARGET_NOT_FOUND" ? "The supplied path was not found or is not a directory." : "Provide an existing OpenCode config directory to compare.";
    row.append(cell); body.append(row); return;
  }
  Object.entries({agents:"Agents",skills:"Skills",commands:"Commands"}).forEach(([key,label]) => {
    const values = installation.groups[key] || {};
    const row = document.createElement("tr");
    [label,values.same,values.missing,values.changed,assets[key]].forEach((value) => {
      const cell = document.createElement("td"); cell.textContent = display(value,0); row.append(cell);
    });
    body.append(row);
  });
}

function populateEvidence(activity) {
  const usage = activity.golden_evidence;
  const trace = activity.invocation_trace || {};
  const connected = usage.status === "CONNECTED";
  $("reportCount").textContent = connected ? display(usage.reports,0) : "Not connected";
  $("fastCount").textContent = connected ? display(usage.fast,0) : "Unknown";
  $("fullCount").textContent = connected ? display(usage.full,0) : "Unknown";
  $("evidenceState").textContent = {
    NOT_CONNECTED:"No evidence directory supplied",DIRECTORY_NOT_FOUND:"Evidence directory not found",NO_EVIDENCE_FILES:"No Golden evidence files found",CONNECTED:"Local evidence summaries loaded"
  }[usage.status] || "Evidence state unknown";
  $("evidenceDetail").textContent = connected
    ? `${usage.reports} report summaries read locally${usage.partial ? " (first 1,000 reports only)" : ""}. Report contents and paths are not shown.`
    : "Pass a local directory of Golden evidence JSON reports when starting the dashboard. No report means unknown activity, not zero use.";
  $("lastReport").textContent = usage.last_report_utc ? new Date(usage.last_report_utc).toLocaleString() : "Unknown";
  $("qualifiedReports").textContent = connected ? display(usage.release_qualified,0) : "Unknown";
  $("unqualifiedReports").textContent = connected ? display(usage.not_qualified,0) : "Unknown";
  $("activityValue").textContent = connected ? `${usage.reports} local reports` : "No evidence source";
  $("activityDetail").textContent = connected ? "Summary counts only; report content stays local." : "Golden check reports are optional local inputs.";
  mark($("activityMark"),connected ? "good" : "unknown");
  $("traceProvenance").textContent = display(trace.status,"NOT_INSTRUMENTED").replaceAll("_"," ");
  $("traceDetail").textContent = trace.source === "NONE"
    ? "No trusted OpenCode runtime event source is connected. Model/operator self-reports are not verified traces."
    : "Invocation source and provenance require validation before counts are shown.";
}

function populateWorkflows(rows) {
  if (!workflowRouteElement) return;
  workflowRouteElement.replaceChildren();
  rows.forEach((item) => {
    const card = document.createElement('article');
    card.className = 'workflow-card';
    const heading = document.createElement('h3'); heading.textContent = display(item.id).replaceAll('-', ' ');
    const summary = document.createElement('p'); summary.textContent = display(item.entry);
    const skills = Array.isArray(item.skills) ? item.skills.join(' / ') : 'skill unavailable';
    const primary = item.resolved_primary_agent
      ? `${item.resolved_primary_agent} (${display(item.primary_agent)})`
      : display(item.primary_agent);
    const route = document.createElement('p'); route.className = 'workflow-route'; route.textContent = `${primary} · ${skills} · ${display(item.pattern)} · ${display(item.complexity)} complexity`;
    const mcp = document.createElement('p'); mcp.className = 'workflow-route';
    const candidates = Array.isArray(item.mcp_candidates) ? item.mcp_candidates : [];
    mcp.textContent = candidates.length ? `MCP evaluation candidates only: ${candidates.join(', ')}; no connection is enabled by this route.` : 'No MCP candidate selected for this route.';
    const capability = document.createElement('p'); capability.className = 'workflow-route';
    const capabilityCandidates = Array.isArray(item.capability_candidates) ? item.capability_candidates : [];
    capability.textContent = capabilityCandidates.length
      ? `Capability candidates require separate review: ${capabilityCandidates.join(', ')}.`
      : 'No additional capability candidate listed.';
    const accept = document.createElement('p'); accept.className = 'workflow-acceptance'; accept.textContent = `Done when: ${display(item.acceptance)}`;
    const details = document.createElement('details'); details.className = 'workflow-details';
    const detailsSummary = document.createElement('summary'); detailsSummary.textContent = 'Full route details';
    const detailGrid = document.createElement('div'); detailGrid.className = 'workflow-details-grid';
    const addDetail = (label, value) => {
      const block = document.createElement('section'); block.className = 'workflow-detail';
      const title = document.createElement('h4'); title.textContent = label;
      block.append(title);
      if (Array.isArray(value)) {
        const list = document.createElement('ul');
        const entries = value.map((entry) => typeof entry === 'string' ? entry : `${display(entry.agent)} — ${display(entry.when)}`);
        (entries.length ? entries : ['Not specified']).forEach((entry) => {
          const row = document.createElement('li'); row.textContent = entry; list.append(row);
        });
        block.append(list);
      } else {
        const text = document.createElement('p'); text.textContent = display(value, 'Not specified'); block.append(text);
      }
      detailGrid.append(block);
    };
    addDetail('Context to load', item.context);
    addDetail('Deterministic checks', item.deterministic_tools);
    addDetail('Conditional specialists', item.specialists);
    addDetail('Trust boundary', item.trust);
    addDetail('No-AI fallback', item.no_ai);
    addDetail('Expected outputs', item.outputs);
    addDetail('MCP policy', item.mcp_policy);
    details.append(detailsSummary, detailGrid);
    card.append(heading, summary, route, mcp, capability, accept, details);
    workflowRouteElement.append(card);
  });
}

async function loadWorkflows() {
  if (!workflowRouteElement) return;
  try {
    const response = await fetch('/api/workflows', {cache: 'no-store'});
    if (!response.ok) throw new Error('Local route source unavailable');
    const payload = await response.json();
    populateWorkflows(payload.workflows);
  } catch (_error) {
    workflowRouteElement.textContent = 'Local task routing is unavailable.';
  }
}

function textNode(tag, className, text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  element.textContent = text;
  return element;
}

function capabilityMatches(item, query, type) {
  return (!type || item.capability_type === type)
    && (!query || JSON.stringify(item).toLowerCase().includes(query));
}

function populateCapabilities(payload) {
  if (!payload || !Array.isArray(payload.candidates) || !Array.isArray(payload.task_decisions)) {
    throw new Error('Capability registry has an unsupported shape');
  }
  capabilityRegistry = payload;
  const types = [...new Set(payload.candidates.map((item) => item.capability_type).filter(Boolean))].sort();
  capabilityTypeFilter.replaceChildren(textNode('option', '', 'All capability types'));
  capabilityTypeFilter.firstElementChild.value = '';
  types.forEach((type) => {
    const option = textNode('option', '', type.replaceAll('_', ' '));
    option.value = type;
    capabilityTypeFilter.append(option);
  });
  renderCapabilities();
}

function renderCapabilities() {
  if (!capabilityRegistry || !capabilityDecisionElement || !capabilityResultElement) return;
  const query = (capabilitySearch.value || '').trim().toLowerCase();
  const type = capabilityTypeFilter.value;
  const candidates = capabilityRegistry.candidates.filter((item) => capabilityMatches(item, query, type));
  const candidateById = new Map(capabilityRegistry.candidates.map((item) => [item.id, item]));
  const decisions = capabilityRegistry.task_decisions.filter((decision) => {
    const ranked = Array.isArray(decision.ranked_candidates) ? decision.ranked_candidates : [];
    const relevantCandidates = ranked.map((id) => candidateById.get(id)).filter(Boolean);
    const typeMatches = !type || relevantCandidates.some((item) => item.capability_type === type);
    const queryMatches = !query || JSON.stringify(decision).toLowerCase().includes(query)
      || relevantCandidates.some((item) => JSON.stringify(item).toLowerCase().includes(query));
    return typeMatches && queryMatches;
  });

  capabilityDecisionElement.replaceChildren();
  decisions.forEach((decision) => {
    const card = document.createElement('article');
    card.className = 'capability-decision';
    const title = textNode('h3', '', display(decision.task, 'Task decision'));
    const choice = textNode('p', 'decision-choice', `Current design choice: ${display(decision.current_choice)} · not a measured winner`);
    const reason = textNode('p', 'decision-reason', display(decision.reason));
    const ranked = Array.isArray(decision.ranked_candidates) ? decision.ranked_candidates : [];
    const list = document.createElement('ul');
    ranked.forEach((candidateId) => {
      const item = candidateById.get(candidateId);
      if (type && (!item || item.capability_type !== type)) return;
      const row = document.createElement('li');
      row.textContent = item ? `${candidateId} · ${item.capability_type} · ${display(item.decision, 'UNREVIEWED')}` : candidateId;
      list.append(row);
    });
    const rankBlock = document.createElement('div');
    rankBlock.className = 'decision-ranked';
    rankBlock.append(textNode('strong', '', 'Options considered'), list);
    const measurement = textNode('p', 'decision-measurement', `Evidence: ${display(decision.measurement, 'NOT_RECORDED')}`);
    card.append(title, choice, reason, rankBlock, measurement);
    capabilityDecisionElement.append(card);
  });

  capabilityResultElement.replaceChildren();
  candidates.forEach((item) => {
    const card = document.createElement('article');
    card.className = 'capability-candidate';
    const header = document.createElement('div');
    header.className = 'candidate-header';
    const titleGroup = document.createElement('div');
    titleGroup.append(textNode('h3', '', display(item.id, 'Unnamed candidate')));
    titleGroup.append(textNode('p', 'candidate-owner', `${display(item.capability_type)} · ${display(item.owner_repo)}`));
    header.append(titleGroup, textNode('span', 'candidate-decision', display(item.decision, 'UNREVIEWED').replaceAll('_', ' ')));
    const purpose = textNode('p', 'candidate-purpose', display(item.purpose));
    const version = textNode('p', 'candidate-version', `${display(item.version, 'Version not pinned')} · commit ${display(item.commit, 'not pinned')}`);
    const details = document.createElement('details');
    details.className = 'candidate-evidence';
    details.append(textNode('summary', '', 'License, safety, platform, and measurement evidence'));
    const grid = document.createElement('div');
    grid.className = 'candidate-evidence-grid';
    const fields = [
      ['License', item.license], ['License evidence', item.license_evidence],
      ['Dependencies', item.transitive_dependencies], ['Models and browsers', item.models_browsers],
      ['Windows and Linux', item.windows_linux], ['Offline and telemetry', item.offline_telemetry],
      ['Context cost', item.context_cost], ['Maintenance', item.maintenance],
      ['Permissions', item.permissions], ['Prompt-injection review', item.prompt_injection_security],
      ['Source review', item.source_review], ['Measured evidence', item.measured_evidence],
    ];
    fields.forEach(([label, value]) => {
      const field = document.createElement('section');
      field.className = 'candidate-evidence-field';
      field.append(textNode('h4', '', label), textNode('p', '', display(value, 'NOT_RECORDED')));
      grid.append(field);
    });
    details.append(grid);
    card.append(header, purpose, version, details);
    capabilityResultElement.append(card);
  });

  const summary = $("capabilitySummary");
  summary.textContent = `${decisions.length} of ${capabilityRegistry.task_decisions.length} task decisions · ${candidates.length} of ${capabilityRegistry.candidates.length} candidate records. All entries remain research-only; installed/runtime availability is not represented.`;
  if (!decisions.length && !candidates.length) {
    capabilityResultElement.append(textNode('p', 'capability-empty', 'No capability or task decision matches. Clear the search or choose another type.'));
  }
}

async function loadCapabilities() {
  if (!capabilityDecisionElement || !capabilityResultElement) return;
  try {
    const response = await fetch('/research/capability-selection.json', {cache: 'no-store'});
    if (!response.ok) throw new Error('Local capability registry unavailable');
    populateCapabilities(await response.json());
  } catch (_error) {
    $("capabilitySummary").textContent = 'Local capability evidence is unavailable.';
    capabilityDecisionElement.replaceChildren();
    capabilityResultElement.replaceChildren();
  }
}

capabilitySearch?.addEventListener('input', renderCapabilities);
capabilityTypeFilter?.addEventListener('change', renderCapabilities);

function render(data) {
  const {product,repository,assets,project_agent:projectAgent,installation,updates,integrity,activity,runtime,progress} = data;
  $("releaseVersion").textContent = product.version;
  $("qualificationState").textContent = product.qualification.replaceAll("_"," ");
  $("checkoutVersion").textContent = product.version;
  $("checkoutQualification").textContent = `Qualification: ${product.qualification.replaceAll("_"," ")}. This is not an approved company release.`;
  populateAssets(assets);
  populateProgress(progress);
  populateInstall(installation,assets);
  populateEvidence(activity);
  const projectAgentLabels = {
    CONFIGURED:"Golden primary configured",
    NOT_GOLDEN_DEFAULT:"Golden is not the project default",
    INVALID_CONFIG:"Project config is invalid",
    INVALID_AGENT_REFERENCE:"Golden primary reference is invalid",
    UNKNOWN:"Project config unknown"
  };
  $("projectAgentStatus").textContent = (projectAgentLabels[projectAgent.status] || "Unknown").toUpperCase();
  $("projectAgentValue").textContent = projectAgent.agent || "Not configured";
  $("projectAgentDetail").textContent = projectAgent.status === "CONFIGURED"
    ? `${projectAgent.config_path} selects golden-engineer. This is checked-in config evidence only; company OpenCode loading and compatibility are not tested.`
    : `${projectAgent.config_path} does not establish a usable Golden primary. Runtime selection remains untested.`;

  $("updateValue").textContent = "Feed not configured";
  $("updateDetail").textContent = updates.available_from_checkout === null
    ? "No approved release feed is connected."
    : `${updates.available_from_checkout} file(s) differ from this checkout; approval is not implied.`;
  $("feedPill").textContent = "FEED NOT CONFIGURED";
  $("assetSyncState").textContent = installation.state.replaceAll("_"," ");
  $("checkoutUpdateCount").textContent = updates.available_from_checkout === null ? "Unknown" : display(updates.available_from_checkout,0);

  $("runtimeValue").textContent = runtime.opencode_binary_detected ? "Executable found" : "Not found on PATH";
  $("runtimeDetail").textContent = runtime.opencode_binary_detected
    ? "An executable path is present, but its build version and company compatibility are unknown. Agent, skill, and MCP discovery has not run."
    : "No OpenCode executable is found on this process PATH; company runtime remains unverified.";
  $("integrityHeading").textContent = integrity.state === "VERIFIED" ? "Source checksums match" : "Source checksum mismatch";
  $("integrityDetail").textContent = `${integrity.checked} file(s) checked · ${integrity.missing} missing · ${integrity.altered} altered · ${integrity.unlisted || 0} unlisted.`;
  $("repoMeta").textContent = repository.status === "AVAILABLE"
    ? `Local branch ${repository.branch} · commit ${repository.commit} · ${repository.clean ? "clean worktree" : "uncommitted changes"}${repository.ahead === null ? "" : ` · ${repository.ahead} ahead / ${repository.behind} behind`}`
    : "Local Git state not available";
  $("updatedAt").textContent = `Updated ${new Date(data.generated_at_utc).toLocaleTimeString()}`;

  if (installation.state === "INSTALL_INCOMPLETE") {
    $("nextHeading").textContent = "Review the safe installation plan";
    $("nextDescription").textContent = "Golden files are missing from the supplied config directory. Dry-run the installer and resolve conflicts before applying.";
  } else if (installation.state === "LOCAL_CHANGES_NEED_REVIEW") {
    $("nextHeading").textContent = "Review local file differences";
    $("nextDescription").textContent = "Some installed files differ from this checkout. Preserve company provider settings and reconcile each changed file deliberately.";
  } else if (installation.state === "IN_SYNC_WITH_CHECKOUT") {
    $("nextHeading").textContent = "Prove the installed runtime works";
    $("nextDescription").textContent = "Matching files are only a starting point. Verify relevant agent/skill discovery and use approved MCP tools when the task needs them. Compare a CLI only when it is a plausible alternative for that operation.";
  }
}

async function loadState() {
  $("updatedAt").textContent = "Refreshing local status";
  try {
    const response = await fetch("/api/state",{cache:"no-store"});
    if (!response.ok) throw new Error("Local status source unavailable");
    render(await response.json());
  } catch (_error) {
    $("updatedAt").textContent = "Local status unavailable";
    $("releaseVersion").textContent = "Unavailable";
    $("qualificationState").textContent = "LOCAL SERVER REQUIRED";
  }
}

const initial = location.hash.slice(1);
showPage(labels[initial] ? initial : "overview");
loadState();
loadWorkflows();
loadCapabilities();
