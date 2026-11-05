const fs = require('fs');

const path = 'frontend/index.html';
let html = fs.readFileSync(path, 'utf8');

// Helper to replace text inside tag or add attribute
function tagAttr(pattern, replacement) {
  if (html.includes(pattern)) {
    html = html.replace(pattern, replacement);
  }
}

// 1. Navigation links
tagAttr('<a href="#overview">Overview</a>', '<a href="#overview" data-i18n="navOverview">Overview</a>');
tagAttr('<a href="#visual-stories">Awareness</a>', '<a href="#visual-stories" data-i18n="navAwareness">Awareness</a>');
tagAttr('<a href="#platform-personas">Personas</a>', '<a href="#platform-personas" data-i18n="navRoles">Personas</a>');
tagAttr('<a href="#official-helplines">Helplines</a>', '<a href="#official-helplines" data-i18n="navHelplines">Helplines</a>');
tagAttr('<button type="button" class="btn-landing-register" id="btnNavRegister">Register Free</button>', '<button type="button" class="btn-landing-register" id="btnNavRegister" data-i18n="navRegister">Register Free</button>');
tagAttr('<button type="button" class="btn-landing-signin" id="btnNavSignIn">Sign In &rarr;</button>', '<button type="button" class="btn-landing-signin" id="btnNavSignIn" data-i18n="navSignIn">Sign In &rarr;</button>');

// 2. Hero elements
tagAttr('<p class="hero-tagline">See the risk. Stay prepared.</p>', '<p class="hero-tagline" data-i18n="heroTagline">See the risk. Stay prepared.</p>');
tagAttr('<h1 class="hero-headline">When nature changes, be prepared.</h1>', '<h1 class="hero-headline" data-i18n="heroHeadline">When nature changes, be prepared.</h1>');
tagAttr('<p class="hero-supporting-statement">Understand disasters. Protect communities. Connect people to help across the Lower Godavari Basin.</p>', '<p class="hero-supporting-statement" data-i18n="heroStatement">Understand disasters. Protect communities. Connect people to help across the Lower Godavari Basin.</p>');
tagAttr('<button type="button" class="btn-hero-primary" id="btnHeroExplore">', '<button type="button" class="btn-hero-primary" id="btnHeroExplore" data-i18n="btnExplore">');
tagAttr('<button type="button" class="btn-hero-register" id="btnHeroRegister">', '<button type="button" class="btn-hero-register" id="btnHeroRegister" data-i18n="btnCreateAccount">');
tagAttr('<button type="button" class="btn-hero-secondary" id="btnHeroSignIn">', '<button type="button" class="btn-hero-secondary" id="btnHeroSignIn" data-i18n="btnSignIn">');

// 3. Login page headers and labels
tagAttr('<h2>Welcome back</h2>', '<h2 data-i18n="signInTitle">Welcome back</h2>');
tagAttr('<p>Sign in to access your monitoring workspace and emergency operations.</p>', '<p data-i18n="signInDesc">Sign in to access your monitoring workspace and emergency operations.</p>');
tagAttr('<label for="dedicatedEmail">Email Address</label>', '<label for="dedicatedEmail" data-i18n="emailLabel">Email Address</label>');
tagAttr('<label for="dedicatedPassword">Password</label>', '<label for="dedicatedPassword" data-i18n="passwordLabel">Password</label>');
tagAttr('<span>Remember me on this device</span>', '<span data-i18n="rememberMe">Remember me on this device</span>');
tagAttr('Forgot password?</a>', '<span data-i18n="forgotPassword">Forgot password?</span></a>');
tagAttr('<span>Don\'t have an account?</span>', '<span data-i18n="noAccountText">Don\'t have an account?</span>');
tagAttr('<a href="javascript:void(0)" onclick="navigateTo(\'register\')">Create a free account &#8594;</a>', '<a href="javascript:void(0)" onclick="navigateTo(\'register\')" data-i18n="createAccountLink">Create a free account &#8594;</a>');
tagAttr('<a href="javascript:void(0)" onclick="navigateTo(\'welcome\')">&#8592; Back to Welcome</a>', '<a href="javascript:void(0)" onclick="navigateTo(\'welcome\')" data-i18n="backToWelcome">&#8592; Back to Welcome</a>');

// 4. Registration page headers and labels
tagAttr('<h2>Create your account</h2>', '<h2 data-i18n="registerTitle">Create your account</h2>');
tagAttr('<p>Register as a resident to receive local disaster alerts and emergency assistance.</p>', '<p data-i18n="registerDesc">Register as a resident to receive local disaster alerts and emergency assistance.</p>');
tagAttr('<label for="regFullName">Full Name</label>', '<label for="regFullName" data-i18n="fullNameLabel">Full Name</label>');
tagAttr('<label for="regEmail">Email Address</label>', '<label for="regEmail" data-i18n="regEmailLabel">Email Address</label>');
tagAttr('<label for="regPassword">Password <span class="auth-label-hint">(min 8 characters)</span></label>', '<label for="regPassword" data-i18n="regPasswordLabel">Password (min 8 chars)</label>');
tagAttr('<label for="regConfirmPassword">Confirm Password</label>', '<label for="regConfirmPassword" data-i18n="confirmPasswordLabel">Confirm Password</label>');
tagAttr('<label for="regDistrict">District</label>', '<label for="regDistrict" data-i18n="districtLabel">District</label>');
tagAttr('<label for="regMandal">Mandal</label>', '<label for="regMandal" data-i18n="mandalLabel">Mandal</label>');
tagAttr('<span>Already have an account?</span>', '<span data-i18n="haveAccountText">Already have an account?</span>');
tagAttr('<a href="javascript:void(0)" onclick="navigateTo(\'login\')">Sign In &#8594;</a>', '<a href="javascript:void(0)" onclick="navigateTo(\'login\')" data-i18n="signInLink">Sign In &#8594;</a>');

// 5. Buttons
tagAttr('Sign In to Account &rarr;</button>', '<span data-i18n="btnSignInSubmit">Sign In to Account &rarr;</span></button>');
tagAttr('Create Account &amp; Proceed &rarr;</button>', '<span data-i18n="btnRegisterSubmit">Create Account &amp; Proceed &rarr;</span></button>');

// 6. Role Selection
tagAttr('Choose Your Operational Role</h2>', '<span data-i18n="roleSelectTitle">Choose Your Operational Role</span></h2>');

// 7. Location Onboarding
tagAttr('Confirm Your Location</h2>', '<span data-i18n="onboardingTitle">Confirm Your Location</span></h2>');
tagAttr('Save Location &amp; Enter Platform &rarr;</button>', '<span data-i18n="btnSaveOnboarding">Save Location &amp; Enter Platform &rarr;</span></button>');

// 8. Situation Awareness Home
tagAttr('Situation Awareness Home</h2>', '<span data-i18n="sitHomeTitle">Situation Awareness Home</span></h2>');
tagAttr('<button type="button" class="btn-home-signout" id="btnSituationHomeSignOut">Sign Out</button>', '<button type="button" class="btn-home-signout" id="btnSituationHomeSignOut" data-i18n="signOut">Sign Out</button>');

fs.writeFileSync(path, html, 'utf8');
console.log('SUCCESS: index.html tagged with data-i18n attributes');
