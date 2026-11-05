"""
Fix step 6 in frontend/index.html using exact string matching.
"""
INDEX_PATH = r"C:\major project\frontend\index.html"

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

incoming_audit_html = '''
                    <!-- Live Incoming Resident Assistance Requests -->
                    <div class="ops-card" style="margin-top:16px;">
                      <div class="card-header">
                        <span class="card-icon">🆘</span>
                        <h3>Incoming Resident Assistance Requests</h3>
                        <span class="count-pill" id="residentRequestsCount">1 Active</span>
                      </div>
                      <div class="table-responsive">
                        <table class="data-table" id="residentHelpRequestsTable">
                          <thead>
                            <tr>
                              <th>Req ID</th>
                              <th>Resident</th>
                              <th>Phone</th>
                              <th>Mandal</th>
                              <th>Need</th>
                              <th>Persons</th>
                              <th>Status</th>
                              <th>Action</th>
                            </tr>
                          </thead>
                          <tbody id="residentHelpRequestsTbody">
                            <!-- Populated dynamically -->
                          </tbody>
                        </table>
                      </div>
                    </div>

                    <!-- Multi-Channel Notification Dispatch & Audit Log -->
                    <div class="ops-card" style="margin-top:16px;">
                      <div class="card-header">
                        <span class="card-icon">📨</span>
                        <h3>Emergency Notification Dispatch &amp; Delivery Audit Log</h3>
                        <span class="badge-pill info">SMTP / SMS Gateway / In-App</span>
                      </div>
                      <div class="notification-dispatch-toolbar" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                        <button type="button" class="btn-sm btn-action-primary" id="btnTriggerTestNotification">
                          ⚡ Dispatch Safe-Test Broadcast Verification
                        </button>
                        <span class="notif-dispatch-status" id="notifDispatchStatusText" style="font-size:12px; color:var(--text-secondary);"></span>
                      </div>
                      <div class="table-responsive">
                        <table class="data-table" id="notificationDeliveryLogTable">
                          <thead>
                            <tr>
                              <th>Dispatch ID</th>
                              <th>Recipient</th>
                              <th>Channel</th>
                              <th>Status</th>
                              <th>Provider</th>
                              <th>Timestamp</th>
                            </tr>
                          </thead>
                          <tbody id="notificationDeliveryLogTbody">
                            <!-- Populated dynamically via /api/v1/notifications/history -->
                          </tbody>
                        </table>
                      </div>
                    </div>
'''

target_tag = '</table>\n                      </div>\n                    </div>\n                  </div>\n                </div>\n              </div>\n\n              <!-- ============================================================= -->\n              <!-- ROLE 3: DISTRICT ADMINISTRATOR VIEW -->'

if 'id="residentHelpRequestsTable"' not in content:
    idx = content.find('id="mandalAdvisoriesTable"')
    if idx != -1:
        # Find closing card for this table
        closing_div = content.find('</div>\n                    </div>\n                  </div>\n                </div>', idx)
        if closing_div != -1:
            closing_point = closing_div + len('</div>\n                    </div>')
            content = content[:closing_point] + '\n' + incoming_audit_html + content[closing_point:]
            print("Successfully inserted incoming help requests and notification audit tables!")
        else:
            print("Could not find closing point.")
    else:
        print("mandalAdvisoriesTable not found.")

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("Done updating index.html.")
