const test = require("node:test");
const assert = require("node:assert/strict");
const {evaluate,validate} = require("./demo-engine.js");

const base = {
  task_id:"DEMO-001",target_identifier:"SAMPLE-1",
  primary_metric:10,secondary_metric:4,status_descriptor:"NOMINAL",is_critical_flag:false
};
test("nominal, elevated and critical paths", () => {
  assert.equal(evaluate(base).overall_urgency,"ROUTINE");
  assert.equal(evaluate({...base,primary_metric:26}).total_alerts,1);
  assert.equal(evaluate({...base,secondary_metric:13}).overall_urgency,"ELEVATED_RISK");
  assert.equal(evaluate({...base,is_critical_flag:true}).overall_urgency,"CRITICAL_STAT_PANIC");
  assert.equal(evaluate({...base,status_descriptor:"DISCORDANT"}).total_alerts,1);
});
test("threshold boundaries are exclusive", () => {
  assert.equal(evaluate({...base,primary_metric:25,secondary_metric:12}).total_alerts,0);
});
test("no forged cryptographic attestations", () => {
  assert.equal(evaluate(base).audit_hash,undefined);
  assert.equal(evaluate(base).mode,"BROWSER_DEMONSTRATION");
});
test("invalid inputs rejected", () => {
  for (const p of [
    {...base,task_id:"../../secret"}, {...base,primary_metric:NaN},
    {...base,secondary_metric:Infinity},{...base,is_critical_flag:"false"},
    {...base,status_descriptor:"X".repeat(129)}
  ]) assert.throws(()=>validate(p));
});
