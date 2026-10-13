/* Rule-based demonstrations only. Values are not regulatory or clinical thresholds. */
(function (root) {
  "use strict";
  const idPattern = /^[A-Za-z0-9._-]{1,128}$/;
  const keywords = ["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"];

  function validate(p) {
    if (!p || !idPattern.test(p.task_id) || !idPattern.test(p.target_identifier)) {
      throw new Error("Task ID and sample ID must use 1–128 letters, numbers, dots, dashes, or underscores.");
    }
    for (const field of ["primary_metric", "secondary_metric"]) {
      if (typeof p[field] !== "number" || !Number.isFinite(p[field]) || Math.abs(p[field]) > 1000000) {
        throw new Error(field + " must be a finite number between -1,000,000 and 1,000,000.");
      }
    }
    if (typeof p.status_descriptor !== "string" || p.status_descriptor.length > 128) {
      throw new Error("Status descriptor must be at most 128 characters.");
    }
    if (typeof p.is_critical_flag !== "boolean") {
      throw new Error("Critical flag must be boolean.");
    }
  }

  function evaluate(p) {
    validate(p);
    const alerts = [];
    if (p.primary_metric > 25) {
      alerts.push({origin_worker:"InvariantQCWorker", urgency:"ELEVATED_RISK", summary:"Primary metric exceeds demonstration threshold 25"});
    }
    if (p.is_critical_flag || p.secondary_metric > 12) {
      alerts.push({origin_worker:"SafetyEscalationWorker", urgency:p.is_critical_flag ? "CRITICAL_STAT_PANIC":"ELEVATED_RISK", summary:"Critical flag or secondary demonstration threshold 12 triggered"});
    }
    if (keywords.some(k => p.status_descriptor.toUpperCase().includes(k))) {
      alerts.push({origin_worker:"ProtocolConformanceWorker", urgency:"ELEVATED_RISK", summary:"Configured anomaly keyword matched"});
    }
    const critical = alerts.filter(a=>a.urgency==="CRITICAL_STAT_PANIC").length;
    const urgency = critical ? "CRITICAL_STAT_PANIC" : alerts.length ? "ELEVATED_RISK":"ROUTINE";
    return {
      mode:"BROWSER_DEMONSTRATION", task_id:p.task_id, target_identifier:p.target_identifier,
      overall_urgency:urgency,
      integrity_status:critical ? "RECALIBRATION_REQUIRED" : alerts.length ? "DISCORDANT_ANOMALY" : "VALIDATED_OPTIMAL",
      total_alerts:alerts.length, critical_alerts_count:critical, alerts,
      disclaimer:"Demo screening only. No USP <825> compliance assessment, cryptographic signing, or clinical validation."
    };
  }
  const api = Object.freeze({evaluate, validate});
  root.USP825Demo = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
