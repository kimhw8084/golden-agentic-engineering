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

function render(data) {
  const {product,repository,assets,installation,updates,integrity,activity,runtime,progress} = data;
  $("releaseVersion").textContent = product.version;
  $("qualificationState").textContent = product.qualification.replaceAll("_"," ");
  $("checkoutVersion").textContent = product.version;
  $("checkoutQualification").textContent = `Qualification: ${product.qualification.replaceAll("_"," ")}. This is not an approved company release.`;
  populateAssets(assets);
  populateProgress(progress);
  populateInstall(installation,assets);
  populateEvidence(activity);

  $("updateValue").textContent = "Feed not configured";
  $("updateDetail").textContent = updates.available_from_checkout === null
    ? "No approved release feed is connected."
    : `${updates.available_from_checkout} file(s) differ from this checkout; approval is not implied.`;
  $("feedPill").textContent = "FEED NOT CONFIGURED";
  $("assetSyncState").textContent = installation.state.replaceAll("_"," ");
  $("checkoutUpdateCount").textContent = updates.available_from_checkout === null ? "Unknown" : display(updates.available_from_checkout,0);

  $("runtimeValue").textContent = runtime.company_agent_skill_mcp_inventory === "NOT_RUN" ? "Not inspected" : runtime.company_agent_skill_mcp_inventory;
  $("runtimeDetail").textContent = runtime.opencode_binary_detected ? "OpenCode executable detected; agent, skill, and MCP discovery still needs a company-machine run." : "OpenCode executable not found on this process PATH; company runtime is unverified.";
  $("integrityHeading").textContent = integrity.state === "VERIFIED" ? "Source checksums match" : "Source checksum mismatch";
  $("integrityDetail").textContent = `${integrity.checked} file(s) checked · ${integrity.missing} missing · ${integrity.altered} altered.`;
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
