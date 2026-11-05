"""
Update frontend/app.js payload
"""
APP_JS_PATH = r"C:\major project\frontend\app.js"

with open(APP_JS_PATH, "r", encoding="utf-8") as f:
    text = f.read()

target = """        const payload = {
          resident_name: document.getElementById('helpResidentName').value.trim(),
          contact_phone: document.getElementById('helpContactPhone').value.trim(),
          mandal: document.getElementById('helpMandal').value,
          specific_location: document.getElementById('helpSpecificLocation').value.trim(),
          required_assistance: document.getElementById('helpRequiredAssistance').value,
          number_of_persons: parseInt(document.getElementById('helpFamilyCount').value, 10) || 1,
          urgency: 'CRITICAL'
        };"""

replacement = """        const rName = document.getElementById('helpResidentName').value.trim();
        const rLoc = document.getElementById('helpSpecificLocation').value.trim();
        const rAssist = document.getElementById('helpRequiredAssistance').value;
        const rCount = parseInt(document.getElementById('helpFamilyCount').value, 10) || 1;
        const payload = {
          contact_name: rName,
          resident_name: rName,
          contact_phone: document.getElementById('helpContactPhone').value.trim(),
          mandal: document.getElementById('helpMandal').value,
          district: 'East Godavari',
          location_description: rLoc,
          specific_location: rLoc,
          assistance_type: rAssist,
          required_assistance: rAssist,
          num_persons_affected: rCount,
          number_of_persons: rCount,
          urgency: 'CRITICAL',
          situation_notes: 'Urgent emergency assistance requested via citizen portal.'
        };"""

# Normalize \r\n and \n
text = text.replace(target, replacement)
with open(APP_JS_PATH, "w", encoding="utf-8") as f:
    f.write(text)

print("Updated app.js payload.")
