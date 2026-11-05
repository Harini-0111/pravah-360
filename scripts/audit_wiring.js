const fs = require('fs');
const appJs = fs.readFileSync('C:/major project/frontend/app.js', 'utf8');

// Button IDs that need event listeners
const buttonIds = [
  'btnLandingLangToggle', 'btnNavRegister', 'btnNavSignIn', 'btnHeroExplore',
  'btnHeroRegister', 'btnHeroSignIn', 'btnToggleDedicatedPwd', 'btnToggleRegPwd',
  'btnConfirmLocation', 'btnSituationHomeSignOut', 'navItemWelcome', 'navItemWeather',
  'navItemExplorer', 'navItemEvidence', 'navItemOperations', 'navItemImpact',
  'navItemHelp', 'navItemGlobal', 'navItemOverview', 'navItemRisk', 'navItemResearch',
  'btnReturnToSituationHome', 'btnGlobalSearch', 'btnUserAuth', 'btnLaunchTour',
  'btnResetBasinView', 'btnWelcomeExploreOverview', 'btnWelcomeStartTour',
  'btnWelcomeOpenCitizenSos', 'btnTriageYesEmergency', 'btnTriageNoSafe',
  'btnOpenFullExplorer', 'btnFitBasinExtent', 'btnToggleLegend', 'btnCloseDrawer',
  'btnToggleGlobeRotation', 'btnResetGlobeView', 'btnToggleGlobeTexture',
  'btnCloseGlobeCard', 'btnInspectFloodCrestGis', 'btnToggleDryBaseline',
  'btnToggleFloodCrest', 'btnResidentSyncMap', 'btnSosBeacon',
  'btnResidentAcknowledge', 'btnDispatchAdvisory', 'btnTriggerTestNotification',
  'btnToggleNewResourceForm', 'btnCancelNewResource', 'btnLangEn', 'btnLangTe',
  'btnCloseLoginModal', 'btnLoginSubmit', 'btnContinueGuest', 'btnCloseTourModal',
  'btnTourBack', 'btnTourSkip', 'btnTourNext', 'btnDedicatedLoginSubmit',
  'btnRegisterSubmit', 'btnSubmitSosForm', 'btnSituationHomeSignOut'
];

const results = { wired: [], unwired: [] };
buttonIds.forEach(id => {
  if (appJs.includes(`getElementById('${id}')`) || appJs.includes(`getElementById("${id}")`)) {
    results.wired.push(id);
  } else {
    results.unwired.push(id);
  }
});

console.log(`WIRED (${results.wired.length}):`, results.wired.join(', '));
console.log(`\nUNWIRED (${results.unwired.length}):`);
results.unwired.forEach(id => console.log(' -', id));
