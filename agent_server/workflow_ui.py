"""Workflow UI — full underwriting workspace HTML page."""

WORKFLOW_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Underwriting Workspace</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
:root{--bg:#f5f6fa;--card:#fff;--border:#e2e5ec;--primary:#1a56db;--accent:#e84d31;--text:#1e293b;--muted:#64748b;--green:#16a34a;--amber:#d97706;--red:#dc2626}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);display:flex;height:100vh}

/* Sidebar */
.sidebar{width:240px;background:#1e293b;color:#fff;display:flex;flex-direction:column;flex-shrink:0}
.sidebar .brand{padding:20px;display:flex;align-items:center;gap:10px;border-bottom:1px solid #334155}
.sidebar .brand svg{width:32px;height:32px}
.sidebar .brand h2{font-size:14px;line-height:1.3}
.sidebar .brand span{color:var(--accent)}
.sidebar nav{padding:16px 12px;flex:1}
.sidebar nav a{display:block;padding:10px 14px;border-radius:8px;color:#94a3b8;font-size:13px;font-weight:500;text-decoration:none;margin-bottom:2px;cursor:pointer}
.sidebar nav a:hover,.sidebar nav a.active{background:#334155;color:#fff}
.sidebar nav .section{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:#475569;padding:16px 14px 6px;font-weight:600}
.sidebar .footer{padding:16px 20px;border-top:1px solid #334155;font-size:11px;color:#64748b}
.sidebar .footer .db-logo{color:#e84d31;font-weight:700;font-size:12px}

/* Main */
.main{flex:1;overflow-y:auto;padding:24px 32px}
.topbar{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
.topbar h1{font-size:20px;font-weight:700}
.topbar .controls{display:flex;gap:12px;align-items:center}
.topbar select{padding:8px 14px;border:1px solid var(--border);border-radius:8px;font-size:13px;background:#fff;min-width:200px}
.btn{padding:8px 18px;border:none;border-radius:8px;font-weight:600;font-size:13px;cursor:pointer;display:inline-flex;align-items:center;gap:6px}
.btn-primary{background:var(--primary);color:#fff}
.btn-accent{background:var(--accent);color:#fff}
.btn-green{background:var(--green);color:#fff}
.btn-outline{background:#fff;border:1px solid var(--border);color:var(--text)}
.btn:disabled{opacity:.5;cursor:not-allowed}

/* Cards */
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px}
.card h3{font-size:15px;font-weight:700;margin-bottom:14px;display:flex;align-items:center;justify-content:space-between}
.card-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.info-row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f1f3f5;font-size:13px}
.info-row .label{color:var(--muted);font-weight:500}
.info-row .value{font-weight:600;text-align:right}

/* Alert banner */
.alert{padding:10px 16px;border-radius:8px;font-size:13px;font-weight:600;display:flex;align-items:center;gap:8px;margin-bottom:16px}
.alert-amber{background:#fef3c7;color:#92400e;border:1px solid #fde68a}
.alert-green{background:#dcfce7;color:#166534;border:1px solid #bbf7d0}
.alert-red{background:#fee2e2;color:#991b1b;border:1px solid #fecaca}

/* Baseline scenario */
.baseline-bar{padding:12px 20px;border-radius:8px;font-size:14px;font-weight:700;margin-bottom:14px}
.baseline-green{background:#dcfce7;color:#166534}
.baseline-amber{background:#fef3c7;color:#92400e}
.baseline-red{background:#fee2e2;color:#991b1b}

/* Adjust form */
.form-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
.form-group label{display:block;font-size:11px;font-weight:600;color:var(--muted);margin-bottom:4px;text-transform:uppercase;letter-spacing:.05em}
.form-group input,.form-group select,.form-group textarea{width:100%;padding:10px 12px;border:1px solid var(--border);border-radius:8px;font-size:13px}
.form-group textarea{resize:vertical;min-height:60px}
.form-group .hint{font-size:10px;color:var(--muted);margin-top:2px}

/* AI panel */
.ai-panel{background:#f0f7ff;border:1px solid #bfdbfe;border-radius:12px;padding:20px;margin-bottom:16px}
.ai-panel h3{color:var(--primary);font-size:15px;margin-bottom:12px}
.ai-panel .ai-content{font-size:13px;line-height:1.7}
.ai-panel .ai-content h2{font-size:14px;color:var(--primary);margin:12px 0 6px;border-bottom:1px solid #bfdbfe;padding-bottom:4px}
.ai-panel .ai-content h2:first-child{margin-top:0}
.ai-panel .ai-content strong{color:#1e40af}
.ai-panel .ai-content ul,.ai-panel .ai-content ol{margin:4px 0 4px 18px}
.ai-panel .ai-content li{margin:2px 0}
.ai-panel .ai-content hr{border:none;border-top:1px solid #bfdbfe;margin:10px 0}
.ai-panel .ai-content code{background:#dbeafe;padding:1px 5px;border-radius:3px;font-size:11px}
.ai-panel .ai-content table{border-collapse:collapse;width:100%;margin:8px 0}
.ai-panel .ai-content th{background:#dbeafe;padding:6px 10px;text-align:left;font-size:11px;border:1px solid #bfdbfe}
.ai-panel .ai-content td{padding:6px 10px;border:1px solid #bfdbfe;font-size:12px}

/* Chat panel */
.chat-panel{border-top:1px solid var(--border);padding-top:16px;margin-top:16px}
.chat-input-row{display:flex;gap:8px}
.chat-input-row input{flex:1;padding:10px 14px;border:1px solid var(--border);border-radius:8px;font-size:13px}

/* Status badges */
.badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.03em}
.badge-approved{background:#dcfce7;color:#166534}
.badge-declined{background:#fee2e2;color:#991b1b}
.badge-pending,.badge-in_review,.badge-postponed{background:#fef3c7;color:#92400e}

/* Loading */
.loading{text-align:center;padding:40px;color:var(--muted)}
.spinner{display:inline-block;width:20px;height:20px;border:2px solid var(--border);border-top-color:var(--primary);border-radius:50%;animation:spin .6s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}

/* Hidden */
.hidden{display:none}
</style>
</head>
<body>

<!-- Sidebar -->
<div class="sidebar">
  <div class="brand">
    <svg viewBox="0 0 40 40" fill="none"><rect width="40" height="40" rx="8" fill="#1a56db"/><path d="M12 28V12h6l4 8 4-8h6v16h-5V19l-3.5 7h-3L17 19v9h-5z" fill="#fff"/></svg>
    <h2><span id="brand-name">Underwriting</span><br/>Agent</h2>
  </div>
  <nav>
    <div class="section">Underwriting Workflow</div>
    <a class="active" onclick="showView('workflow')">Workflow</a>
    <a onclick="showView('chat')">AI Assistant</a>
  </nav>
  <div class="footer">
    <div>Powered by</div>
    <div class="db-logo">Databricks</div>
  </div>
</div>

<!-- Main content -->
<div class="main">

  <!-- Workflow view -->
  <div id="view-workflow">
    <div class="topbar">
      <h1>Underwriting Workspace</h1>
      <div class="controls">
        <select id="sel-applicant" onchange="loadApplicantApps()">
          <option value="">Select Applicant...</option>
        </select>
        <select id="sel-application" onchange="loadApplication()" class="hidden">
          <option value="">Select Application...</option>
        </select>
        <button class="btn btn-primary" onclick="analyzeApplication()" id="btn-analyze" disabled>Analyze Application</button>
      </div>
    </div>

    <div id="app-detail" class="hidden">
      <!-- Application Info -->
      <div class="card">
        <h3>Application Information</h3>
        <div class="card-grid">
          <div>
            <h4 style="font-size:12px;color:var(--muted);margin-bottom:8px">Personal Information</h4>
            <div class="info-row"><span class="label">Applicant ID:</span><span class="value" id="v-applicant-id"></span></div>
            <div class="info-row"><span class="label">Gender:</span><span class="value" id="v-gender"></span></div>
            <div class="info-row"><span class="label">Birth Year:</span><span class="value" id="v-birth-year"></span></div>
            <div class="info-row"><span class="label">BMI Bucket:</span><span class="value" id="v-bmi"></span></div>
            <div class="info-row"><span class="label">Smoker Status:</span><span class="value" id="v-smoker"></span></div>
            <div class="info-row"><span class="label">State:</span><span class="value" id="v-state"></span></div>
          </div>
          <div>
            <h4 style="font-size:12px;color:var(--muted);margin-bottom:8px">Health & Occupation</h4>
            <div class="info-row"><span class="label">Occupation Class:</span><span class="value" id="v-occupation"></span></div>
            <div class="info-row"><span class="label">Channel:</span><span class="value" id="v-channel"></span></div>
            <div class="info-row"><span class="label">Application Date:</span><span class="value" id="v-app-date"></span></div>
            <div class="info-row"><span class="label">Status:</span><span class="value" id="v-status"></span></div>
          </div>
          <div>
            <h4 style="font-size:12px;color:var(--muted);margin-bottom:8px">Product Information</h4>
            <div class="info-row"><span class="label">Product:</span><span class="value" id="v-product"></span></div>
            <div class="info-row"><span class="label">Product Line:</span><span class="value" id="v-product-line"></span></div>
            <div class="info-row"><span class="label">Sum Assured:</span><span class="value" id="v-sa"></span></div>
            <div class="info-row"><span class="label">Max SA (product):</span><span class="value" id="v-max-sa"></span></div>
          </div>
        </div>
      </div>

      <!-- Reason alert -->
      <div id="reason-alert" class="alert alert-amber hidden"></div>

      <!-- Baseline Scenario -->
      <div class="card">
        <h3>Baseline Scenario</h3>
        <div id="baseline-bar" class="baseline-bar baseline-green"></div>
        <div class="card-grid">
          <div><div class="info-row"><span class="label">Risk Class</span><span class="value" id="v-risk-class"></span></div></div>
          <div><div class="info-row"><span class="label">Decision</span><span class="value" id="v-outcome"></span></div></div>
          <div><div class="info-row"><span class="label">Coverage Approved</span><span class="value" id="v-coverage"></span></div></div>
        </div>
      </div>

      <!-- AI Recommendation -->
      <div id="ai-panel" class="ai-panel hidden">
        <h3>AI Recommendation</h3>
        <div id="ai-content" class="ai-content"></div>
      </div>

      <!-- Underwriting Decision -->
      <div class="card">
        <h3>Underwriting Decision</h3>

        <!-- Decision action buttons -->
        <div class="decision-actions" style="display:flex;gap:10px;margin-bottom:18px;flex-wrap:wrap">
          <button class="btn decision-btn" id="dbtn-approve" onclick="selectDecision('approved')" style="background:#dcfce7;color:#166534;border:2px solid transparent;padding:12px 22px;font-size:14px">
            &#10003; Approve Application
          </button>
          <button class="btn decision-btn" id="dbtn-deny" onclick="selectDecision('declined')" style="background:#fee2e2;color:#991b1b;border:2px solid transparent;padding:12px 22px;font-size:14px">
            &#10007; Deny Application
          </button>
          <button class="btn decision-btn" id="dbtn-changes" onclick="selectDecision('approved_with_changes')" style="background:#fef3c7;color:#92400e;border:2px solid transparent;padding:12px 22px;font-size:14px">
            &#9998; Approve with Changes
          </button>
          <button class="btn decision-btn" id="dbtn-info" onclick="selectDecision('info_requested')" style="background:#e0e7ff;color:#3730a3;border:2px solid transparent;padding:12px 22px;font-size:14px">
            &#8505; Request Information
          </button>
        </div>

        <!-- Decision details (shown after selecting a decision) -->
        <div id="decision-details" class="hidden">
          <!-- Decision-specific header -->
          <div id="decision-header" class="alert" style="margin-bottom:14px"></div>

          <!-- Approve with Changes: show adjustment fields -->
          <div id="changes-fields" class="hidden">
            <div class="form-grid" style="margin-bottom:14px">
              <div class="form-group">
                <label>Risk Class Override</label>
                <select id="f-risk-class">
                  <option value="">Keep baseline</option>
                  <option value="preferred">Preferred</option>
                  <option value="standard">Standard</option>
                  <option value="substandard">Substandard</option>
                </select>
              </div>
              <div class="form-group">
                <label>Substandard Rating (1-10)</label>
                <input type="number" id="f-rating" min="1" max="10" value="1"/>
                <div class="hint">1 = lowest, 10 = highest</div>
              </div>
              <div class="form-group">
                <label>Coverage Approved (INR)</label>
                <input type="number" id="f-coverage" placeholder="Enter amount"/>
              </div>
            </div>
          </div>

          <!-- Request Information: show info request fields -->
          <div id="info-fields" class="hidden">
            <div class="form-grid" style="margin-bottom:14px">
              <div class="form-group">
                <label>Information Needed</label>
                <select id="f-info-type">
                  <option value="medical_report">Medical Examination Report</option>
                  <option value="financial_docs">Income / Financial Documents</option>
                  <option value="id_verification">ID / KYC Verification</option>
                  <option value="lab_tests">Lab Test Results (Blood, ECG, etc.)</option>
                  <option value="employer_letter">Employer Confirmation Letter</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div class="form-group">
                <label>Due Date</label>
                <input type="date" id="f-due-date"/>
              </div>
              <div class="form-group">
                <label>Priority</label>
                <select id="f-priority">
                  <option value="normal">Normal</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Deny: show reason fields -->
          <div id="deny-fields" class="hidden">
            <div class="form-grid" style="margin-bottom:14px">
              <div class="form-group">
                <label>Decline Reason</label>
                <select id="f-deny-reason">
                  <option value="R-MED-01">Medical — High risk condition</option>
                  <option value="R-MED-02">Medical — BMI outside limits</option>
                  <option value="R-FIN-01">Financial — SA exceeds limits</option>
                  <option value="R-FIN-02">Financial — Income insufficient</option>
                  <option value="R-OCC-01">Occupation — Hazardous class</option>
                  <option value="R-AGE-01">Age — Outside product range</option>
                  <option value="R-SMK-01">Smoker — Product restriction</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Common: notes + submit -->
          <div class="form-group" style="margin-bottom:14px">
            <label>Analyst Notes / Justification</label>
            <textarea id="f-notes" rows="3" placeholder="Enter justification for this decision..."></textarea>
          </div>

          <div style="display:flex;gap:10px;align-items:center">
            <button class="btn btn-primary" onclick="submitDecision()" id="btn-submit" style="padding:12px 28px;font-size:14px">
              Submit Decision
            </button>
            <button class="btn btn-outline" onclick="cancelDecision()">Cancel</button>
            <span id="decision-status" style="font-size:13px;color:var(--green);font-weight:600"></span>
          </div>
        </div>
      </div>

      <!-- Decision History -->
      <div class="card" id="history-panel" class="hidden">
        <h3>Decision History <button class="btn btn-outline" onclick="loadHistory()" style="font-size:11px;padding:4px 12px">Refresh</button></h3>
        <div id="history-content" style="font-size:13px;color:var(--muted);text-align:center;padding:12px">Select an application to see decision history</div>
      </div>
    </div>

    <div id="placeholder" style="text-align:center;padding:80px;color:var(--muted)">
      <p style="font-size:16px;margin-bottom:8px">Select an applicant to begin</p>
      <p style="font-size:13px">Choose an applicant from the dropdown, then select an application to review.</p>
    </div>
  </div>

  <!-- Confirmation modal -->
  <div id="confirm-modal" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,.5);z-index:100;justify-content:center;align-items:center">
    <div style="background:#fff;border-radius:12px;padding:28px;max-width:480px;width:90%;box-shadow:0 20px 60px rgba(0,0,0,.3)">
      <h3 id="confirm-title" style="margin-bottom:12px;font-size:16px"></h3>
      <div id="confirm-body" style="font-size:13px;color:var(--muted);margin-bottom:8px"></div>
      <div id="confirm-summary" style="background:var(--bg);border-radius:8px;padding:12px;font-size:12px;margin-bottom:18px"></div>
      <div style="display:flex;gap:10px;justify-content:flex-end">
        <button class="btn btn-outline" onclick="closeConfirm()">Cancel</button>
        <button class="btn btn-primary" id="confirm-ok" onclick="confirmSubmit()">Confirm &amp; Submit</button>
      </div>
    </div>
  </div>

  <!-- Chat view -->
  <div id="view-chat" class="hidden">
    <div class="topbar"><h1>AI Assistant</h1></div>
    <div class="card" style="height:calc(100vh - 140px);display:flex;flex-direction:column">
      <div id="chat-messages" style="flex:1;overflow-y:auto;padding:8px 0"></div>
      <div class="chat-input-row" style="padding-top:12px;border-top:1px solid var(--border)">
        <input id="chat-input" placeholder="Ask about underwriting rules, applicants, products..." onkeydown="if(event.key==='Enter')sendChat()"/>
        <button class="btn btn-primary" onclick="sendChat()">Send</button>
      </div>
    </div>
  </div>

</div>

<script>
marked.setOptions({breaks:true,gfm:true});
let currentApp = null;

function showView(v){
  document.getElementById('view-workflow').classList.toggle('hidden',v!=='workflow');
  document.getElementById('view-chat').classList.toggle('hidden',v!=='chat');
  document.querySelectorAll('.sidebar nav a').forEach(a=>a.classList.remove('active'));
  event.target.classList.add('active');
}

// Load company name + applicants on start
async function init(){
  // Fetch company name
  try{
    const cr=await fetch('/api/config');
    const cc=await cr.json();
    if(cc.company_name){
      document.getElementById('brand-name').textContent=cc.company_name;
      document.title=cc.company_name+' — Underwriting Workspace';
    }
  }catch(e){}
  const r=await fetch('/api/applicants');
  const d=await r.json();
  const sel=document.getElementById('sel-applicant');
  for(const a of d.applicants){
    const age=2026-parseInt(a.birth_year);
    const o=document.createElement('option');
    o.value=a.applicant_id;
    o.textContent=`${a.applicant_id} — ${a.gender}, age ${age}, ${a.smoker_status}, ${a.bmi_bucket}`;
    sel.appendChild(o);
  }
}

async function loadApplicantApps(){
  const aid=document.getElementById('sel-applicant').value;
  const selApp=document.getElementById('sel-application');
  selApp.innerHTML='<option value="">Select Application...</option>';
  if(!aid){selApp.classList.add('hidden');return;}
  const r=await fetch(`/api/applicant/${aid}/applications`);
  const d=await r.json();
  for(const a of d.applications){
    const o=document.createElement('option');
    o.value=a.application_id;
    o.textContent=`${a.application_id} — ${a.product_name} (${a.outcome||a.status})`;
    selApp.appendChild(o);
  }
  selApp.classList.remove('hidden');
}

async function loadApplication(){
  const appId=document.getElementById('sel-application').value;
  if(!appId){document.getElementById('app-detail').classList.add('hidden');document.getElementById('placeholder').classList.remove('hidden');return;}
  document.getElementById('btn-analyze').disabled=false;

  const r=await fetch(`/api/application/${appId}`);
  currentApp=await r.json();const a=currentApp;

  const age=2026-parseInt(a.birth_year);
  document.getElementById('v-applicant-id').textContent=a.applicant_id;
  document.getElementById('v-gender').textContent=a.gender;
  document.getElementById('v-birth-year').textContent=`${a.birth_year} (age ${age})`;
  document.getElementById('v-bmi').textContent=a.bmi_bucket;
  document.getElementById('v-smoker').textContent=a.smoker_status;
  document.getElementById('v-state').textContent=a.state_ut||'-';
  document.getElementById('v-occupation').textContent=`Class ${a.occupation_class}`;
  document.getElementById('v-channel').textContent=a.channel;
  document.getElementById('v-app-date').textContent=a.application_date;
  document.getElementById('v-status').innerHTML=`<span class="badge badge-${a.status}">${a.status}</span>`;
  document.getElementById('v-product').textContent=`${a.product_name} (${a.product_id})`;
  document.getElementById('v-product-line').textContent=a.product_line;
  document.getElementById('v-sa').textContent=a.sum_assured_inr?`INR ${Number(a.sum_assured_inr).toLocaleString('en-IN')}`:'-';
  document.getElementById('v-max-sa').textContent=a.product_max_sa?`INR ${Number(a.product_max_sa).toLocaleString('en-IN')}`:'-';

  // Reason alert
  const alert=document.getElementById('reason-alert');
  if(a.reason_code){
    alert.classList.remove('hidden');
    alert.innerHTML=`&#9888; Reason: ${a.reason_description||a.reason_code} (${a.reason_category||''})`;
    alert.className=`alert ${a.outcome==='declined'?'alert-red':'alert-amber'}`;
  } else { alert.classList.add('hidden'); }

  // Baseline
  const bar=document.getElementById('baseline-bar');
  const cls=a.approved_risk_class||'pending';
  bar.textContent=`${a.outcome?a.outcome.toUpperCase():'PENDING'} — Risk Class: ${cls}${a.sum_assured_inr?' — SA: INR '+Number(a.sum_assured_inr).toLocaleString('en-IN'):''}`;
  bar.className=`baseline-bar ${a.outcome==='approved'?'baseline-green':a.outcome==='declined'?'baseline-red':'baseline-amber'}`;
  document.getElementById('v-risk-class').textContent=cls;
  document.getElementById('v-outcome').innerHTML=`<span class="badge badge-${a.outcome||'pending'}">${a.outcome||'pending'}</span>`;
  document.getElementById('v-coverage').textContent=a.sum_assured_inr?`INR ${Number(a.sum_assured_inr).toLocaleString('en-IN')}`:'-';

  // Reset decision panel
  cancelDecision();
  document.getElementById('f-notes').value='';

  // Load workspace if exists
  const wr=await fetch(`/api/workspace/${appId}`);
  const ws=await wr.json();
  if(ws.analyst_notes) document.getElementById('f-notes').value=ws.analyst_notes;
  if(ws.ai_recommendation){
    document.getElementById('ai-content').innerHTML=marked.parse(ws.ai_recommendation);
    document.getElementById('ai-panel').classList.remove('hidden');
  } else { document.getElementById('ai-panel').classList.add('hidden'); }
  if(ws.status && ws.status!=='pending' && ws.status!=='ai_analyzed'){
    document.getElementById('decision-status').textContent='Previous decision: '+ws.status;
  } else { document.getElementById('decision-status').textContent=''; }

  document.getElementById('app-detail').classList.remove('hidden');
  document.getElementById('placeholder').classList.add('hidden');
  loadHistory();
}

async function analyzeApplication(){
  if(!currentApp) return;
  const a=currentApp;
  const btn=document.getElementById('btn-analyze');
  btn.disabled=true;btn.textContent='Analyzing...';
  const panel=document.getElementById('ai-panel');
  panel.classList.remove('hidden');
  document.getElementById('ai-content').innerHTML='<div class="loading"><div class="spinner"></div> AI is analyzing this application...</div>';

  const age=2026-parseInt(a.birth_year);
  const prompt=`Analyze this insurance application and provide underwriting recommendation:\n\n`+
    `Applicant: ${a.applicant_id}, Gender: ${a.gender}, Age: ${age}, BMI: ${a.bmi_bucket}, Smoker: ${a.smoker_status}, Occupation Class: ${a.occupation_class}, State: ${a.state_ut}\n`+
    `Product: ${a.product_name} (${a.product_id}), Product Line: ${a.product_line}\n`+
    `Sum Assured Requested: INR ${Number(a.sum_assured_inr||0).toLocaleString('en-IN')}, Max SA for product: INR ${Number(a.product_max_sa||0).toLocaleString('en-IN')}\n`+
    `Current Decision: ${a.outcome||'pending'}, Risk Class: ${a.approved_risk_class||'TBD'}\n`+
    (a.reason_code?`Reason Code: ${a.reason_code} — ${a.reason_description}\n`:'')+
    `\nPlease:\n1. Check the risk tier using the applicant's BMI bucket and smoker status\n2. Check max sum assured for this product and age\n3. Search underwriting docs for any relevant guidelines\n4. Provide a recommendation: approve / decline / refer with justification`;

  try{
    const r=await fetch('/invocations',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({input:[{role:'user',content:prompt}]})});
    const d=await r.json();
    let text='';
    for(const item of (d.output||[])){
      const c=item.content;
      if(typeof c==='string'&&c) text+=c;
      else if(Array.isArray(c)) for(const x of c){if(x.text) text+=x.text;}
    }
    document.getElementById('ai-content').innerHTML=marked.parse(text||'No recommendation returned.');
    // Auto-save AI recommendation
    await fetch('/api/workspace',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({application_id:a.application_id,ai_recommendation:text,status:'ai_analyzed'})});
  }catch(e){
    document.getElementById('ai-content').innerHTML=`<div class="alert alert-red">Error: ${e.message}</div>`;
  }
  btn.disabled=false;btn.textContent='Analyze Application';
}

// Decision handling
let selectedDecision = null;

const DECISION_CONFIG = {
  approved: {label:'Approve Application', icon:'&#10003;', alertClass:'alert-green', msg:'Application will be APPROVED as-is with the baseline scenario.'},
  declined: {label:'Deny Application', icon:'&#10007;', alertClass:'alert-red', msg:'Application will be DECLINED. Please select a reason and add justification.'},
  approved_with_changes: {label:'Approve with Changes', icon:'&#9998;', alertClass:'alert-amber', msg:'Application will be APPROVED with modifications to risk class, rating, or coverage.'},
  info_requested: {label:'Request Information', icon:'&#8505;', alertClass:'alert-amber', msg:'Application will be placed ON HOLD pending additional information from the applicant.'}
};

function selectDecision(decision){
  selectedDecision=decision;
  const cfg=DECISION_CONFIG[decision];

  // Highlight selected button
  document.querySelectorAll('.decision-btn').forEach(b=>b.style.border='2px solid transparent');
  document.getElementById('dbtn-'+{approved:'approve',declined:'deny',approved_with_changes:'changes',info_requested:'info'}[decision]).style.border='2px solid var(--primary)';

  // Show details panel
  document.getElementById('decision-details').classList.remove('hidden');
  document.getElementById('decision-header').className='alert '+cfg.alertClass;
  document.getElementById('decision-header').innerHTML=cfg.icon+' <strong>'+cfg.label+'</strong> — '+cfg.msg;

  // Show/hide decision-specific fields
  document.getElementById('changes-fields').classList.toggle('hidden',decision!=='approved_with_changes');
  document.getElementById('deny-fields').classList.toggle('hidden',decision!=='declined');
  document.getElementById('info-fields').classList.toggle('hidden',decision!=='info_requested');

  // Pre-fill coverage for changes
  if(decision==='approved_with_changes' && currentApp){
    document.getElementById('f-coverage').value=currentApp.sum_assured_inr||'';
  }
}

function cancelDecision(){
  selectedDecision=null;
  document.getElementById('decision-details').classList.add('hidden');
  document.querySelectorAll('.decision-btn').forEach(b=>b.style.border='2px solid transparent');
}

// Build the submission payload
function buildPayload(){
  let notes=document.getElementById('f-notes').value||'';
  if(selectedDecision==='declined'){
    const reason=document.getElementById('f-deny-reason');
    notes=`[DECLINE: ${reason.options[reason.selectedIndex].text}] ${notes}`;
  }
  if(selectedDecision==='info_requested'){
    const infoType=document.getElementById('f-info-type');
    const due=document.getElementById('f-due-date').value;
    const pri=document.getElementById('f-priority').value;
    notes=`[INFO REQUEST: ${infoType.options[infoType.selectedIndex].text}, Due: ${due||'TBD'}, Priority: ${pri}] ${notes}`;
  }
  return {
    application_id:currentApp.application_id,
    risk_class_override: selectedDecision==='approved_with_changes'?(document.getElementById('f-risk-class').value||null):null,
    substandard_rating: selectedDecision==='approved_with_changes'?(parseFloat(document.getElementById('f-rating').value)||null):null,
    coverage_approved_inr: selectedDecision==='approved_with_changes'?(parseInt(document.getElementById('f-coverage').value)||null):
                           selectedDecision==='approved'?(parseInt(currentApp.sum_assured_inr)||null):null,
    analyst_notes: notes,
    status: selectedDecision
  };
}

// Show confirmation modal
function submitDecision(){
  if(!currentApp||!selectedDecision) return;
  const cfg=DECISION_CONFIG[selectedDecision];
  const payload=buildPayload();

  document.getElementById('confirm-title').innerHTML=cfg.icon+' Confirm: '+cfg.label;
  document.getElementById('confirm-body').textContent=
    selectedDecision==='approved'?'This will APPROVE the application and update the underwriting decision record.':
    selectedDecision==='declined'?'This will DECLINE the application. The decision record and application status will be updated.':
    selectedDecision==='approved_with_changes'?'This will APPROVE the application with your modifications to risk class and coverage.':
    'This will place the application ON HOLD and request additional information.';

  let summary='<strong>Application:</strong> '+currentApp.application_id+'<br>';
  summary+='<strong>Decision:</strong> '+selectedDecision.replace(/_/g,' ').toUpperCase()+'<br>';
  if(payload.risk_class_override) summary+='<strong>Risk Class:</strong> '+payload.risk_class_override+'<br>';
  if(payload.coverage_approved_inr) summary+='<strong>Coverage:</strong> INR '+Number(payload.coverage_approved_inr).toLocaleString('en-IN')+'<br>';
  if(payload.analyst_notes) summary+='<strong>Notes:</strong> '+payload.analyst_notes.slice(0,120)+(payload.analyst_notes.length>120?'...':'');

  const isFinal=selectedDecision==='approved'||selectedDecision==='declined'||selectedDecision==='approved_with_changes';
  if(isFinal) summary+='<br><br><strong style="color:var(--accent)">This will update fact_underwriting_decision and fact_application tables.</strong>';

  document.getElementById('confirm-summary').innerHTML=summary;
  document.getElementById('confirm-modal').style.display='flex';
}

function closeConfirm(){document.getElementById('confirm-modal').style.display='none';}

async function confirmSubmit(){
  closeConfirm();
  const btn=document.getElementById('btn-submit');
  btn.disabled=true;btn.textContent='Saving...';
  const payload=buildPayload();

  try{
    const r=await fetch('/api/workspace',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const d=await r.json();
    document.getElementById('decision-status').textContent='Decision saved: '+selectedDecision.replace(/_/g,' ').toUpperCase();
    document.getElementById('decision-status').style.color=selectedDecision==='declined'?'var(--red)':'var(--green)';
    loadHistory();
    // Refresh the application to show updated status
    setTimeout(()=>loadApplication(),1000);
  }catch(e){
    document.getElementById('decision-status').textContent='Error: '+e.message;
    document.getElementById('decision-status').style.color='var(--red)';
  }
  btn.disabled=false;btn.textContent='Submit Decision';
}

// Decision history
async function loadHistory(){
  if(!currentApp) return;
  const r=await fetch(`/api/workspace/${currentApp.application_id}/history`);
  const d=await r.json();
  const el=document.getElementById('history-content');
  if(!d.history||d.history.length===0){el.innerHTML='<span style="color:var(--muted)">No prior decisions for this application.</span>';return;}

  const BADGE={approved:'badge-approved',declined:'badge-declined',approved_with_changes:'badge-approved',info_requested:'badge-pending',ai_analyzed:'badge-pending',pending:'badge-pending'};
  let html='<table style="width:100%;border-collapse:collapse;font-size:12px"><thead><tr>'+
    '<th style="padding:8px 10px;text-align:left;background:var(--bg);border:1px solid var(--border)">Date</th>'+
    '<th style="padding:8px 10px;text-align:left;background:var(--bg);border:1px solid var(--border)">Analyst</th>'+
    '<th style="padding:8px 10px;text-align:left;background:var(--bg);border:1px solid var(--border)">Decision</th>'+
    '<th style="padding:8px 10px;text-align:left;background:var(--bg);border:1px solid var(--border)">Risk Class</th>'+
    '<th style="padding:8px 10px;text-align:left;background:var(--bg);border:1px solid var(--border)">Coverage</th>'+
    '<th style="padding:8px 10px;text-align:left;background:var(--bg);border:1px solid var(--border)">Notes</th>'+
    '</tr></thead><tbody>';
  for(const h of d.history){
    const dt=h.created_at?h.created_at.slice(0,16).replace('T',' '):'';
    const st=(h.status||'').replace(/_/g,' ');
    const cov=h.coverage_approved_inr?'INR '+Number(h.coverage_approved_inr).toLocaleString('en-IN'):'-';
    const notes=(h.analyst_notes||'').slice(0,80)+(h.analyst_notes&&h.analyst_notes.length>80?'...':'');
    html+=`<tr>
      <td style="padding:8px 10px;border:1px solid var(--border)">${dt}</td>
      <td style="padding:8px 10px;border:1px solid var(--border)">${h.analyst_name||'-'}</td>
      <td style="padding:8px 10px;border:1px solid var(--border)"><span class="badge ${BADGE[h.status]||''}">${st}</span></td>
      <td style="padding:8px 10px;border:1px solid var(--border)">${h.risk_class_override||'-'}</td>
      <td style="padding:8px 10px;border:1px solid var(--border)">${cov}</td>
      <td style="padding:8px 10px;border:1px solid var(--border);max-width:200px;overflow:hidden;text-overflow:ellipsis">${notes||'-'}</td>
    </tr>`;
  }
  html+='</tbody></table>';
  el.innerHTML=html;
}

// Chat
async function sendChat(){
  const inp=document.getElementById('chat-input');
  const q=inp.value.trim();if(!q)return;inp.value='';
  const msgs=document.getElementById('chat-messages');
  msgs.innerHTML+=`<div style="text-align:right;margin:8px 0"><span style="background:var(--primary);color:#fff;padding:8px 14px;border-radius:12px;display:inline-block;font-size:13px">${q}</span></div>`;
  msgs.innerHTML+=`<div id="chat-loading" style="margin:8px 0;color:var(--muted);font-size:13px"><div class="spinner"></div> Thinking...</div>`;
  msgs.scrollTop=msgs.scrollHeight;
  try{
    const r=await fetch('/invocations',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({input:[{role:'user',content:q}]})});
    const d=await r.json();
    let text='';
    for(const item of (d.output||[])){
      const c=item.content;
      if(typeof c==='string'&&c)text+=c;
      else if(Array.isArray(c))for(const x of c){if(x.text)text+=x.text;}
    }
    document.getElementById('chat-loading').remove();
    msgs.innerHTML+=`<div style="margin:8px 0;background:#f0f7ff;border:1px solid #bfdbfe;padding:14px;border-radius:12px;font-size:13px;line-height:1.7">${marked.parse(text)}</div>`;
  }catch(e){
    document.getElementById('chat-loading').remove();
    msgs.innerHTML+=`<div style="margin:8px 0;color:var(--red)">Error: ${e.message}</div>`;
  }
  msgs.scrollTop=msgs.scrollHeight;
}

init();
</script>
</body>
</html>"""
