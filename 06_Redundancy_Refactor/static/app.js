const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const state = { view: "original", records: [], anomalies: null, stages: [], dependencies: [], schema: {}, stage: 0, anomaly: "insertion", dependency: 0, schemaTable: "Department", relationship: null, anomalyRows: null, highlights: { patient: true, doctor: true, dept: true } };
const escapeHtml = value => String(value ?? "").replace(/[&<>"']/g, char => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[char]));
const notice = (message, error = false) => { const element = $("#notice"); element.textContent = message; element.className = `notice show${error ? " error" : ""}`; };
const clearNotice = () => { $("#notice").textContent = ""; $("#notice").className = "notice"; };
const fetchJson = async url => { const response = await fetch(url); const data = await response.json(); if (!response.ok) throw new Error(data.error || "Unable to load laboratory data"); return data; };
const value = (row, key) => escapeHtml(row[key]);
const tableHtml = (rows, columns, compact = false) => {
  if (!rows.length) return "<p class='muted'>No rows available.</p>";
  return `<div class="table-scroll"><table><thead><tr>${columns.map(column => `<th>${escapeHtml(column)}</th>`).join("")}</tr></thead><tbody>${rows.map(row => `<tr>${columns.map(column => `<td>${compact ? escapeHtml(row[column]) : highlight(row, column)}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
};
const highlight = (row, column) => {
  const classes = { PatientID: "mark-patient", PatientName: "mark-patient", PatientPhone: "mark-patient", DoctorID: "mark-doctor", DoctorName: "mark-doctor", DepartmentID: "mark-dept", DepartmentName: "mark-dept" };
  const group = classes[column]?.replace("mark-", "");
  return `<span class="${state.highlights[group] ? classes[column] || "" : ""}">${value(row, column)}</span>`;
};
const resetAnomaly = () => { state.anomalyRows = null; renderAnomaly(); };
const renderOriginal = () => {
  const query = $("#record-search").value.trim().toLowerCase();
  const rows = state.records.filter(row => Object.values(row).join(" ").toLowerCase().includes(query));
  $("#original-body").innerHTML = rows.map(row => `<tr><td>${value(row, "AppointmentID")}</td><td>${highlight(row, "PatientID")} · ${highlight(row, "PatientName")}</td><td>${highlight(row, "PatientPhone")}</td><td>${highlight(row, "DoctorID")} · ${highlight(row, "DoctorName")}</td><td>${highlight(row, "DepartmentID")} · ${highlight(row, "DepartmentName")}</td><td>${value(row, "AppointmentDate")}</td><td>${value(row, "Treatments")}</td></tr>`).join("") || "<tr><td colspan='7'>No matching records.</td></tr>";
};
const renderAnomaly = () => {
  const key = state.anomaly;
  if (key === "insertion") {
    $("#anomaly-panel").innerHTML = `<article class="panel anomaly-card"><span class="eyebrow">Insert a fact</span><h2>New doctor, no appointment</h2><p>A hospital hires Dr Mira Sen for Neurology before a patient is booked.</p><div class="anomaly-action"><strong>Original table result</strong><span>There is no clean row for the doctor and department without inventing an appointment, patient, and treatment.</span><button class="primary" id="insert-demo">Simulate insertion</button><button class="secondary" id="reset-demo">Reset</button></div></article><article class="panel anomaly-result"><div class="result-head"><div><span class="eyebrow">Before / after</span><h2 id="anomaly-result-title">No unrelated appointment should be invented.</h2><p id="anomaly-result-copy">The normalized design stores independent master facts in Department and Doctor.</p></div></div><div id="anomaly-table">${tableHtml(state.records.slice(0, 6), ["AppointmentID", "PatientID", "DoctorID", "DepartmentID", "Treatments"])}</div></article>`;
    $("#insert-demo").onclick = () => { $("#anomaly-result-title").textContent = "Insertion blocked by the original row shape"; $("#anomaly-result-copy").textContent = "The new doctor cannot be represented without unrelated appointment data. In the normalized schema, insert Department and Doctor independently."; $("#anomaly-table").innerHTML = `<div class="callout"><strong>Missing fact</strong><span>Dr Mira Sen / Neurology has no appointment row yet. Creating a fake appointment would corrupt the meaning of the table.</span></div>`; };
    $("#reset-demo").onclick = resetAnomaly;
    return;
  }
  const source = state.anomalies[key];
  const rows = state.anomalyRows || source.rows;
  const changed = Boolean(state.anomalyRows);
  const cards = rows.map(row => `<tr>${Object.entries(row).filter(([column]) => ["AppointmentID", "PatientID", "PatientName", "PatientPhone", "DoctorID", "DoctorName", "DepartmentID", "DepartmentName"].includes(column)).map(([column, cell]) => `<td>${changed && ((key === "update" && column === "PatientPhone") || (key === "doctor" && column === "DepartmentName")) ? `<strong class="mark-doctor">${escapeHtml(cell)}</strong>` : escapeHtml(cell)}</td>`).join("")}</tr>`).join("");
  $("#anomaly-panel").innerHTML = `<article class="panel anomaly-card"><span class="eyebrow">Simulate safely</span><h2>${source.title}</h2><p>${source.explanation}</p><div class="anomaly-action"><strong>${source.field || "Delete appointment row"}</strong><span>Target: ${source.target}. A copy of the affected rows is shown.</span><button class="primary" id="run-demo">${changed ? "Simulated" : "Run simulation"}</button><button class="secondary" id="reset-demo">Reset</button></div></article><article class="panel anomaly-result"><div class="result-head"><div><span class="eyebrow">${changed ? "After simulation" : "Before state"}</span><h2 id="anomaly-result-title">${changed ? "Every redundant occurrence is visible." : "Affected redundant occurrences"}</h2><p id="anomaly-result-copy">${source.explanation}</p></div></div><div class="table-scroll"><table><thead><tr><th>Appointment</th><th>Patient</th><th>Name</th><th>Phone / Doctor</th><th>Doctor name</th><th>Department</th></tr></thead><tbody>${cards}</tbody></table></div></article>`;
  $("#run-demo").onclick = () => { if (key === "deletion") state.anomalyRows = source.rows.filter(row => row.AppointmentID !== source.target); else state.anomalyRows = source.rows.map(row => ({ ...row, [source.field]: source.after })); renderAnomaly(); };
  $("#reset-demo").onclick = resetAnomaly;
};
const renderStage = () => {
  const stage = state.stages[state.stage];
  $("#stage-count").textContent = `${state.stage + 1} / ${state.stages.length}`;
  $("#prev-stage").disabled = state.stage === 0;
  $("#next-stage").disabled = state.stage === state.stages.length - 1;
  $("#stage-tabs").innerHTML = state.stages.map((item, index) => `<button class="stage-tab ${index === state.stage ? "active" : ""}" data-stage="${index}">${item.label}</button>`).join("");
  $$(".stage-tab").forEach(button => { button.onclick = () => { state.stage = Number(button.dataset.stage); renderStage(); }; });
  const previous = state.stages[state.stage - 1];
  $("#stage-content").innerHTML = `<div class="transition-strip"><span>${previous ? `${previous.label} / Before` : "Source / Before"}</span><strong>→</strong><span>${stage.label} / After</span></div><div class="stage-summary"><article><span class="eyebrow">Current structure</span><h3>${escapeHtml(stage.title)}</h3><p>${escapeHtml(stage.problem)}</p></article><article><span class="eyebrow">Candidate key</span><h3>${escapeHtml(stage.key)}</h3><p>${escapeHtml(stage.operation)}</p></article><article><span class="eyebrow">Normal-form result</span><h3>${stage.label === "BCNF" ? "Verified" : "Next improvement"}</h3><p>${escapeHtml(stage.satisfies)}</p></article></div><div class="stage-dependencies"><span class="eyebrow">Relevant dependencies</span>${stage.dependencies.map(dependency => `<span class="dependency-chip">${escapeHtml(dependency)}</span>`).join("")}</div><div class="stage-tables">${stage.tables.map(table => `<article class="mini-table"><h3>${escapeHtml(table.name)}</h3>${tableHtml(table.rows, table.columns, true)}</article>`).join("")}</div>`;
};
const renderDependencies = () => {
  const item = state.dependencies[state.dependency];
  $("#dependency-list").innerHTML = state.dependencies.map((dependency, index) => `<button class="dependency-button ${index === state.dependency ? "active" : ""}" data-dependency="${index}">${escapeHtml(dependency.label)}</button>`).join("");
  $$(".dependency-button").forEach(button => { button.onclick = () => { state.dependency = Number(button.dataset.dependency); renderDependencies(); }; });
  $("#dependency-detail").innerHTML = `<span class="eyebrow">Selected dependency</span><h2>${escapeHtml(item.label)}</h2><div class="detail-list"><div><span>Determinant</span><strong>${escapeHtml(item.determinant)}</strong></div><div><span>Dependent</span><strong>${escapeHtml(item.dependent)}</strong></div><div><span>Classification</span><strong>${escapeHtml(item.classification)}</strong></div><div><span>Stage</span><strong>${escapeHtml(item.stage)}</strong></div></div><p>${escapeHtml(item.why)}</p>`;
};
const relationships = () => Object.entries(state.schema).flatMap(([child, table]) => table.fks.map(fk => {
  const [fromColumn, arrow, target] = fk.split(" ");
  const [parent, parentColumn] = target.split(".");
  return { id: `${child}-${fromColumn}`, child, parent, fromColumn, parentColumn, label: `${child}.${fromColumn} -> ${parent}.${parentColumn}`, cardinality: "N:1" };
}));
const relatedTables = name => relationships().filter(item => item.child === name || item.parent === name).flatMap(item => [item.child, item.parent]);
const edgePoint = (rect, target, bounds) => {
  const cx = rect.left - bounds.left + rect.width / 2;
  const cy = rect.top - bounds.top + rect.height / 2;
  const tx = target.left - bounds.left + target.width / 2;
  const ty = target.top - bounds.top + target.height / 2;
  const dx = tx - cx;
  const dy = ty - cy;
  const scale = 1 / Math.max(Math.abs(dx) / (rect.width / 2), Math.abs(dy) / (rect.height / 2));
  return { x: cx + dx * scale, y: cy + dy * scale };
};
const drawLinks = () => {
  const svg = $("#schema-links");
  const canvas = $(".schema-visual");
  if (!svg || !canvas) return;
  const bounds = canvas.getBoundingClientRect();
  if (!bounds.width || !bounds.height) return;
  svg.setAttribute("viewBox", `0 0 ${bounds.width} ${bounds.height}`);
  svg.innerHTML = relationships().map(link => {
    const from = document.querySelector(`[data-table="${link.child}"]`);
    const to = document.querySelector(`[data-table="${link.parent}"]`);
    if (!from || !to) return "";
    const a = from.getBoundingClientRect();
    const b = to.getBoundingClientRect();
    const start = edgePoint(a, b, bounds);
    const end = edgePoint(b, a, bounds);
    const x1 = start.x;
    const y1 = start.y;
    const x2 = end.x;
    const y2 = end.y;
    const active = state.relationship === link.id || (state.schemaTable && relatedTables(state.schemaTable).includes(link.child) && relatedTables(state.schemaTable).includes(link.parent));
    return `<g class="schema-link ${active ? "active" : ""}" data-relationship="${link.id}" tabindex="0" role="button" aria-label="${escapeHtml(link.label)}"><line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"></line><circle cx="${x1}" cy="${y1}" r="4"></circle><circle cx="${x2}" cy="${y2}" r="4"></circle><text x="${(x1 + x2) / 2}" y="${(y1 + y2) / 2 - 5}">${link.cardinality}</text></g>`;
  }).join("");
  $$(".schema-link").forEach(link => {
    link.onclick = () => { state.relationship = link.dataset.relationship; state.schemaTable = null; renderSchema(); };
    link.onkeydown = event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); link.click(); } };
  });
};
const renderSchemaDetail = () => {
  const link = relationships().find(item => item.id === state.relationship);
  if (link) {
    const parent = state.schema[link.parent];
    const child = state.schema[link.child];
    $("#schema-selection").textContent = link.label;
    $("#schema-detail").innerHTML = `<span class="eyebrow">Selected relationship</span><h2>${link.child} to ${link.parent}</h2><p>${escapeHtml(child.purpose)} The foreign key connects each referencing row to one referenced master row.</p><div class="detail-list"><div><span>Referencing</span><strong>${link.child}.${link.fromColumn}</strong></div><div><span>Referenced</span><strong>${link.parent}.${link.parentColumn}</strong></div><div><span>Cardinality</span><strong>${link.cardinality}: one ${link.parent} to many ${link.child} rows</strong></div></div><h3 class="preview-title">Referenced data preview</h3>${tableHtml(parent.preview, parent.columns, true)}`;
    return;
  }
  const table = state.schema[state.schemaTable] || state.schema.Department;
  $("#schema-selection").textContent = state.schemaTable ? `Selected table: ${state.schemaTable}` : "Select a table or relationship";
  $("#schema-detail").innerHTML = `<span class="eyebrow">Selected table</span><h2>${state.schemaTable || "Department"}</h2><p>${escapeHtml(table.purpose)}</p><div class="detail-list"><div><span>Columns</span><strong>${table.columns.map(column => `${column} (${table.types[column]})`).join(", ")}</strong></div><div><span>Primary key</span><strong>${table.pk.join(", ")}</strong></div><div><span>Foreign keys</span><strong>${table.fks.join("; ") || "None"}</strong></div><div><span>Related tables</span><strong>${relationships().filter(item => item.child === state.schemaTable || item.parent === state.schemaTable).map(item => `${item.child} ${item.cardinality} ${item.parent}`).join("; ") || "None"}</strong></div></div><h3 class="preview-title">Actual data preview</h3>${tableHtml(table.preview, table.columns, true)}`;
};
const renderSchema = () => {
  const activeLink = relationships().find(item => item.id === state.relationship);
  const connected = activeLink ? [activeLink.child, activeLink.parent] : state.schemaTable ? [state.schemaTable, ...relatedTables(state.schemaTable)] : [];
  $("#schema-canvas").innerHTML = Object.entries(state.schema).map(([name, table]) => `<button class="schema-table ${connected.includes(name) ? "active" : ""} ${connected.length && !connected.includes(name) ? "dimmed" : ""}" data-table="${name}" aria-label="Inspect ${name} table"><strong>${name}</strong><ul>${table.columns.map(column => `<li class="${table.pk.includes(column) ? "pk" : ""} ${table.fks.some(fk => fk.startsWith(column + " ")) ? "fk" : ""}">${table.pk.includes(column) ? "PK " : ""}${table.fks.some(fk => fk.startsWith(column + " ")) ? "FK " : ""}${column}<small>${table.types[column]}</small></li>`).join("")}</ul></button>`).join("");
  $$(".schema-table").forEach(card => { card.onclick = () => { state.schemaTable = card.dataset.table; state.relationship = null; renderSchema(); }; });
  renderSchemaDetail();
  requestAnimationFrame(drawLinks);
  setTimeout(drawLinks, 80);
};
const setView = view => { state.view = view; $$(".nav-item").forEach(item => { const active = item.dataset.view === view; item.classList.toggle("active", active); item.setAttribute("aria-current", active ? "page" : "false"); }); $$(".view").forEach(section => section.classList.toggle("active", section.id === view)); clearNotice(); if (view === "anomalies") renderAnomaly(); if (view === "explorer") renderStage(); if (view === "dependencies") renderDependencies(); if (view === "schema") renderSchema(); };
const load = async () => { try { const [overview, anomalies, stages, dependencies, schema] = await Promise.all([fetchJson("/api/overview"), fetchJson("/api/anomalies"), fetchJson("/api/stages"), fetchJson("/api/dependencies"), fetchJson("/api/schema")]); state.records = overview.records; state.anomalies = anomalies; state.stages = stages; state.dependencies = dependencies; state.schema = schema; $("#record-count").textContent = overview.count; $("#patient-count").textContent = overview.patient_count; $("#doctor-count").textContent = overview.doctor_count; $("#overview-record-count").textContent = overview.count; $("#overview-patient-count").textContent = overview.patient_count; $("#overview-treatment-count").textContent = overview.treatment_line_count; renderOriginal(); renderStage(); renderDependencies(); renderSchema(); } catch (error) { notice(error.message, true); } };
$$(".nav-item").forEach(item => { item.onclick = () => setView(item.dataset.view); });
$$("[data-jump]").forEach(button => { button.onclick = () => setView(button.dataset.jump); });
$$(".highlight-toggle").forEach(button => { button.onclick = () => { const group = button.dataset.highlight; state.highlights[group] = !state.highlights[group]; button.classList.toggle("active", state.highlights[group]); button.setAttribute("aria-pressed", String(state.highlights[group])); renderOriginal(); }; });
$$(".segmented button").forEach(button => { button.onclick = () => { state.anomaly = button.dataset.anomaly; state.anomalyRows = null; $$(".segmented button").forEach(item => item.classList.toggle("active", item === button)); renderAnomaly(); }; });
$("#record-search").oninput = renderOriginal;
$("#prev-stage").onclick = () => { if (state.stage > 0) { state.stage -= 1; renderStage(); } };
$("#next-stage").onclick = () => { if (state.stage < state.stages.length - 1) { state.stage += 1; renderStage(); } };
$("#reset-schema").onclick = () => { state.schemaTable = "Department"; state.relationship = null; renderSchema(); };
$("#fit-schema").onclick = () => { state.schemaTable = null; state.relationship = null; renderSchema(); };
window.addEventListener("resize", drawLinks);
setView("overview");
load();
