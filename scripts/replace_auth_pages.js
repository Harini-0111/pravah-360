const fs = require('fs');
const path = require('path');

const HTML_PATH = 'C:/major project/frontend/index.html';

const LOGIN_NEW = `  <main id="page-login" class="pravah-page auth-split-page" style="display:none;">
    <div class="auth-bg-anim" aria-hidden="true">
      <div class="auth-orb auth-orb-1"></div>
      <div class="auth-orb auth-orb-2"></div>
      <div class="auth-orb auth-orb-3"></div>
    </div>
    <div class="auth-left-panel" role="complementary">
      <div class="auth-left-photo-bg auth-photo-cyclone"></div>
      <div class="auth-left-gradient-overlay"></div>
      <div class="auth-left-content">
        <div class="auth-left-brand">
          <div class="auth-left-logo-wrap">
            <img src="/static/assets/images/branding/pravah360_emblem.svg" alt="PRAVAH 360" width="48" height="48">
          </div>
          <div>
            <div class="auth-left-logo-name">PRAVAH <span>360</span></div>
            <div class="auth-left-logo-tagline">See the risk. Stay prepared.</div>
          </div>
        </div>
        <div class="auth-left-body">
          <h2 class="auth-left-headline">Geospatial Disaster<br>Intelligence Platform</h2>
          <p class="auth-left-desc">Orbital Earth observation, multi-criteria flood modelling and community emergency coordination across the Lower Godavari Basin.</p>
          <ul class="auth-left-features">
            <li><span class="auth-feat-dot" style="background:#D7A94D;"></span>Sentinel-1 SAR flood detection</li>
            <li><span class="auth-feat-dot" style="background:#4db6D7;"></span>AHP susceptibility mapping</li>
            <li><span class="auth-feat-dot" style="background:#D66B52;"></span>Citizen SOS &amp; NDRF dispatch</li>
            <li><span class="auth-feat-dot" style="background:#7bc67e;"></span>Live IMD &amp; CWC integration</li>
          </ul>
        </div>
        <div class="auth-left-footer">
          <span class="auth-status-dot"></span>
          <span>Lower Godavari Basin &bull; Andhra Pradesh Emergency Operations</span>
        </div>
      </div>
    </div>
    <div class="auth-right-panel">
      <div class="auth-form-card" id="loginFormCard">
        <div class="auth-form-logo-mobile" aria-hidden="true">
          <img src="/static/assets/images/branding/pravah360_emblem.svg" alt="" width="32" height="32">
          <span>PRAVAH <b>360</b></span>
        </div>
        <div class="auth-form-header">
          <h2>Welcome back</h2>
          <p>Sign in to access your monitoring workspace and emergency operations.</p>
        </div>
        <form id="dedicatedLoginForm" novalidate>
          <div class="auth-field-group">
            <label for="dedicatedEmail" class="auth-label">Email address</label>
            <div class="auth-input-wrap">
              <span class="auth-input-icon">&#9993;</span>
              <input type="email" id="dedicatedEmail" class="auth-input" placeholder="you@example.com" required autocomplete="username">
            </div>
          </div>
          <div class="auth-field-group">
            <label for="dedicatedPassword" class="auth-label">
              Password
              <a href="javascript:void(0)" class="auth-label-link" onclick="alert('Contact your district administrator to reset your account password.'); return false;" tabindex="-1">Forgot?</a>
            </label>
            <div class="auth-input-wrap">
              <span class="auth-input-icon">&#128274;</span>
              <input type="password" id="dedicatedPassword" class="auth-input auth-input-has-toggle" placeholder="&bull;&bull;&bull;&bull;&bull;&bull;&bull;&bull;" required autocomplete="current-password">
              <button type="button" class="auth-pwd-toggle" id="btnToggleDedicatedPwd" aria-label="Toggle password visibility">
                <svg id="eyeIconLogin" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              </button>
            </div>
          </div>
          <div class="auth-remember-row">
            <label class="auth-checkbox-label">
              <input type="checkbox" id="dedicatedRemember">
              <span class="auth-checkbox-custom"></span>
              <span>Remember me for 7 days</span>
            </label>
          </div>
          <button type="submit" class="auth-submit-btn" id="btnDedicatedLoginSubmit">
            <span class="auth-btn-text">Sign In to Account</span>
            <span class="auth-btn-arrow">&#8594;</span>
            <span class="auth-btn-spinner" aria-hidden="true"></span>
          </button>
          <div class="login-feedback" id="dedicatedLoginFeedback"></div>
        </form>
        <div class="auth-evaluator-section">
          <div class="auth-evaluator-label">Evaluator Demo Access</div>
          <div class="auth-evaluator-pills">
            <button type="button" class="auth-eval-pill btn-test-pill" data-email="citizen@pravah360.in" data-pass="Citizen@123">Resident</button>
            <button type="button" class="auth-eval-pill btn-test-pill" data-email="mandal.admin@pravah360.in" data-pass="Mandal@123">Mandal</button>
            <button type="button" class="auth-eval-pill btn-test-pill" data-email="district.collector@pravah360.in" data-pass="District@123">District</button>
            <button type="button" class="auth-eval-pill btn-test-pill" data-email="ert.commander@pravah360.in" data-pass="Responder@123">ERT Team</button>
          </div>
        </div>
        <div class="auth-switch-link">
          New to PRAVAH 360?
          <a href="javascript:void(0)" onclick="navigateTo('register')">Create a free account &#8594;</a>
        </div>
        <div class="auth-back-link">
          <a href="javascript:void(0)" onclick="navigateTo('welcome')">&#8592; Back to Welcome</a>
        </div>
      </div>
    </div>
  </main>`;

const REGISTER_NEW = `  <main id="page-register" class="pravah-page auth-split-page auth-split-register" style="display:none;">
    <div class="auth-bg-anim" aria-hidden="true">
      <div class="auth-orb auth-orb-1" style="background:rgba(214,107,82,0.12);"></div>
      <div class="auth-orb auth-orb-2" style="background:rgba(215,169,77,0.10);"></div>
      <div class="auth-orb auth-orb-3" style="background:rgba(38,77,103,0.12);"></div>
    </div>
    <div class="auth-left-panel" role="complementary">
      <div class="auth-left-photo-bg auth-photo-community"></div>
      <div class="auth-left-gradient-overlay" style="background:linear-gradient(160deg, rgba(38,77,103,0.75) 0%, rgba(12,36,32,0.90) 100%);"></div>
      <div class="auth-left-content">
        <div class="auth-left-brand">
          <div class="auth-left-logo-wrap">
            <img src="/static/assets/images/branding/pravah360_emblem.svg" alt="PRAVAH 360" width="48" height="48">
          </div>
          <div>
            <div class="auth-left-logo-name">PRAVAH <span>360</span></div>
            <div class="auth-left-logo-tagline">Protect communities. Connect people.</div>
          </div>
        </div>
        <div class="auth-left-body">
          <h2 class="auth-left-headline">Join 8.2 million<br>protected residents</h2>
          <p class="auth-left-desc">Register to receive hyper-local flood alerts, track river levels in your mandal, and activate emergency SOS when you need help most.</p>
          <ul class="auth-left-features">
            <li><span class="auth-feat-dot" style="background:#D7A94D;"></span>Local flood risk notifications</li>
            <li><span class="auth-feat-dot" style="background:#7bc67e;"></span>River gauge alerts for your mandal</li>
            <li><span class="auth-feat-dot" style="background:#D66B52;"></span>Emergency SOS beacon</li>
            <li><span class="auth-feat-dot" style="background:#4db6D7;"></span>Preparedness guides in Telugu</li>
          </ul>
        </div>
        <div class="auth-left-footer">
          <span class="auth-status-dot" style="background:#D7A94D;"></span>
          <span>Free account &bull; No credit card required</span>
        </div>
      </div>
    </div>
    <div class="auth-right-panel auth-right-panel-register">
      <div class="auth-form-card auth-form-card-wide" id="registerFormCard">
        <div class="auth-form-logo-mobile" aria-hidden="true">
          <img src="/static/assets/images/branding/pravah360_emblem.svg" alt="" width="32" height="32">
          <span>PRAVAH <b>360</b></span>
        </div>
        <div class="auth-form-header">
          <h2>Create your account</h2>
          <p>Register as a resident to receive local disaster alerts and emergency assistance.</p>
        </div>
        <form id="dedicatedRegisterForm" novalidate>
          <div class="auth-form-two-col">
            <div class="auth-field-group auth-col-full">
              <label for="regFullName" class="auth-label">Full Legal Name</label>
              <div class="auth-input-wrap">
                <span class="auth-input-icon">&#128100;</span>
                <input type="text" id="regFullName" class="auth-input" placeholder="e.g. Ramesh Varma" required autocomplete="name">
              </div>
            </div>
            <div class="auth-field-group auth-col-full">
              <label for="regEmail" class="auth-label">Email Address</label>
              <div class="auth-input-wrap">
                <span class="auth-input-icon">&#9993;</span>
                <input type="email" id="regEmail" class="auth-input" placeholder="you@example.com" required autocomplete="email">
              </div>
            </div>
            <div class="auth-field-group">
              <label for="regPassword" class="auth-label">
                Password
                <span class="auth-pwd-strength-label" id="regPwdStrengthLabel"></span>
              </label>
              <div class="auth-input-wrap">
                <span class="auth-input-icon">&#128274;</span>
                <input type="password" id="regPassword" class="auth-input auth-input-has-toggle" placeholder="Min. 8 characters" required minlength="8" autocomplete="new-password">
                <button type="button" class="auth-pwd-toggle" id="btnToggleRegPwd" aria-label="Toggle password visibility">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                </button>
              </div>
              <div class="auth-pwd-strength-bar" id="regPwdStrengthBar">
                <div class="auth-pwd-strength-fill" id="regPwdStrengthFill"></div>
              </div>
            </div>
            <div class="auth-field-group">
              <label for="regConfirmPassword" class="auth-label">Confirm Password</label>
              <div class="auth-input-wrap">
                <span class="auth-input-icon">&#128274;</span>
                <input type="password" id="regConfirmPassword" class="auth-input" placeholder="Repeat password" required minlength="8" autocomplete="new-password">
              </div>
              <div class="auth-field-hint" id="regPwdMatchHint"></div>
            </div>
            <div class="auth-field-group">
              <label for="regDistrict" class="auth-label">District</label>
              <div class="auth-input-wrap auth-select-wrap">
                <span class="auth-input-icon">&#127965;</span>
                <select id="regDistrict" class="auth-input auth-select">
                  <option value="East Godavari" selected>East Godavari</option>
                  <option value="Dr. B.R. Ambedkar Konaseema">Dr. B.R. Ambedkar Konaseema</option>
                  <option value="West Godavari">West Godavari</option>
                  <option value="Eluru">Eluru</option>
                  <option value="Kakinada">Kakinada</option>
                  <option value="Alluri Sitharama Raju">Alluri Sitharama Raju</option>
                </select>
              </div>
            </div>
            <div class="auth-field-group">
              <label for="regMandal" class="auth-label">Monitored Mandal</label>
              <div class="auth-input-wrap auth-select-wrap">
                <span class="auth-input-icon">&#127968;</span>
                <select id="regMandal" class="auth-input auth-select">
                  <option value="Rajamahendravaram Urban" selected>Rajamahendravaram Urban</option>
                  <option value="Rajamahendravaram Rural">Rajamahendravaram Rural</option>
                  <option value="Kadiam">Kadiam</option>
                  <option value="Rajanagaram">Rajanagaram</option>
                  <option value="Seethanagaram">Seethanagaram</option>
                  <option value="Korukonda">Korukonda</option>
                  <option value="Gokavaram">Gokavaram</option>
                  <option value="Kovvur">Kovvur</option>
                  <option value="Nidadavole">Nidadavole</option>
                  <option value="Amalapuram">Amalapuram</option>
                  <option value="Razole">Razole</option>
                  <option value="Mummidivaram">Mummidivaram</option>
                </select>
              </div>
            </div>
          </div>
          <button type="submit" class="auth-submit-btn auth-submit-btn-register" id="btnRegisterSubmit">
            <span class="auth-btn-text">Create Account &amp; Proceed</span>
            <span class="auth-btn-arrow">&#8594;</span>
            <span class="auth-btn-spinner" aria-hidden="true"></span>
          </button>
          <div class="login-feedback" id="dedicatedRegisterFeedback"></div>
          <div class="auth-success-overlay" id="regSuccessOverlay" aria-live="polite" style="display:none;">
            <div class="auth-success-icon">&#10003;</div>
            <div class="auth-success-title">Account Created!</div>
            <div class="auth-success-sub">Welcome to PRAVAH 360. Setting up your workspace&hellip;</div>
          </div>
        </form>
        <div class="auth-switch-link">
          Already have an account?
          <a href="javascript:void(0)" onclick="navigateTo('login')">Sign In &#8594;</a>
        </div>
        <div class="auth-back-link">
          <a href="javascript:void(0)" onclick="navigateTo('welcome')">&#8592; Back to Welcome</a>
        </div>
      </div>
    </div>
  </main>`;

let content = fs.readFileSync(HTML_PATH, 'utf8');

// Replace login page
const loginStart = content.indexOf('  <main id="page-login"');
const loginEnd = content.indexOf('\n  </main>', loginStart) + '\n  </main>'.length;
if (loginStart === -1) { console.error('Login page not found!'); process.exit(1); }
console.log(`Login: chars ${loginStart}-${loginEnd}`);
content = content.slice(0, loginStart) + LOGIN_NEW + content.slice(loginEnd);

// Replace register page
const regStart = content.indexOf('  <main id="page-register"');
const regEnd = content.indexOf('\n  </main>', regStart) + '\n  </main>'.length;
if (regStart === -1) { console.error('Register page not found!'); process.exit(1); }
console.log(`Register: chars ${regStart}-${regEnd}`);
content = content.slice(0, regStart) + REGISTER_NEW + content.slice(regEnd);

fs.writeFileSync(HTML_PATH, content, 'utf8');
console.log('SUCCESS: Auth pages replaced.');
