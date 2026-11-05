const fs = require('fs');
const htmlPath = 'C:/major project/frontend/index.html';
let html = fs.readFileSync(htmlPath, 'utf8');

// 1. In Awareness Card 2 (Coastal Weather), replace bay_of_bengal_cyclone_satellite.jpg with bay_aerial_ocean_waves.jpg
const oldCard2Img = '<img src="/static/assets/images/awareness/bay_of_bengal_cyclone_satellite.jpg" alt="Satellite imagery of cyclone storm over Bay of Bengal">';
const newCard2Img = '<img src="/static/assets/images/awareness/bay_aerial_ocean_waves.jpg" alt="Aerial view of turbulent Bay of Bengal coastal waters and storm swell">';

if (html.includes(oldCard2Img)) {
  html = html.replace(oldCard2Img, newCard2Img);
  console.log("✓ Replaced Awareness Card 2 image with bay_aerial_ocean_waves.jpg");
} else {
  console.log("Card 2 image string not found directly, checking variations...");
}

// 2. In Persona Card 1 (Residents), replace residents_community.jpg with monsoon_shelter_community.jpg
const oldPersona1 = '<img src="/static/assets/residents_community.jpg" alt="Community members observing river flood levels">';
const newPersona1 = '<img src="/static/assets/images/communities/monsoon_shelter_community.jpg" alt="Community members seeking shelter during heavy monsoon rains">';

if (html.includes(oldPersona1)) {
  html = html.replace(oldPersona1, newPersona1);
  console.log("✓ Replaced Persona Card 1 image with monsoon_shelter_community.jpg");
}

// 3. In Persona Card 2 (Response Teams), replace rescue_team_boat.jpg with rescue_boat_evacuation.jpg
const oldPersona2 = '<img src="/static/assets/rescue_team_boat.jpg" alt="NDRF response team in rescue boat">';
const newPersona2 = '<img src="/static/assets/images/emergency-response/rescue_boat_evacuation.jpg" alt="Emergency response motorboat evacuation in flooded streets">';

if (html.includes(oldPersona2)) {
  html = html.replace(oldPersona2, newPersona2);
  console.log("✓ Replaced Persona Card 2 image with rescue_boat_evacuation.jpg");
}

fs.writeFileSync(htmlPath, html, 'utf8');
console.log("HTML image updates completed successfully.");
