"use strict";
(() => {
  const byId = id => document.getElementById(id);
  const form = byId("audit-form");
  const runButton = byId("run");
  const modeLabel = byId("mode");
  const summary = byId("summary");
  const output = byId("result");
  const save = byId("save");
  let apiConnected = false;
  let count = 0;
  let latest = null;

  async function checkApi() {
    try {
      const response = await fetch("./health", {cache:"no-store"});
      if (!response.ok) throw new Error("No API");
      const health = await response.json();
      apiConnected = health.service === "radiopharmaceutical-usp-825-agent";
    } catch (_) {
      apiConnected = false;
    }
    modeLabel.textContent = apiConnected ? "FastAPI backend connected" : "Local browser demonstration · no API";
  }

  function payloadFromForm() {
    const primaryText = byId("primary_metric").value.trim();
    const secondaryText = byId("secondary_metric").value.trim();
    if (primaryText === "" || secondaryText === "") throw new Error("Both metric fields are required.");
    const p = {
      task_id:byId("task_id").value.trim(),
      target_identifier:byId("target_id").value.trim(),
      primary_metric:Number(primaryText),
      secondary_metric:Number(secondaryText),
      status_descriptor:byId("status_descriptor").value.trim(),
      is_critical_flag:byId("is_critical").checked
    };
    USP825Demo.validate(p);
    return p;
  }

  form.addEventListener("submit", async event => {
    event.preventDefault();
    latest = null;
    save.disabled = true;
    try {
      if (!form.reportValidity()) return;
      const payload = payloadFromForm();
      runButton.disabled = true;
      summary.textContent = apiConnected ? "Requesting evaluation from backend…" : "Evaluating demonstration rules…";
      let result;
      if (apiConnected) {
        const response = await fetch("./api/audit", {
          method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(payload)
        });
        if (!response.ok) throw new Error("Backend returned HTTP " + response.status + ". Check input and server configuration.");
        result = await response.json();
      } else {
        result = USP825Demo.evaluate(payload);
      }
      latest = result;
      count += 1;
      byId("counter").textContent = count + (count === 1 ? " evaluation" : " evaluations") + " during this session";
      summary.textContent = result.overall_urgency + (apiConnected ? " · backend response" : " · browser demonstration only");
      output.textContent = JSON.stringify(result, null, 2);
      save.disabled = false;
    } catch (error) {
      summary.textContent = "Evaluation failed";
      output.textContent = error instanceof Error ? error.message : "Unexpected evaluation error";
    } finally {
      runButton.disabled = false;
    }
  });

  save.addEventListener("click", () => {
    if (!latest) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(latest,null,2)],{type:"application/json"}));
    const link = document.createElement("a");
    link.href = url;
    link.download = "radiopharmaceutical-demo-result.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  });
  byId("reset").addEventListener("click", () => {
    latest = null;
    summary.textContent = "Enter demonstration values and select Evaluate input.";
    output.textContent = "No result yet.";
    save.disabled = true;
  });
  checkApi();
})();
