with open('frontend/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace the triple closing tag with double closing tag
old_block = """                  <div class="legend-row"><span class="swatch" style="background:#38bdf8;"></span> Mandal Boundaries</div>
                </div>
              </div>
              </div>"""

new_block = """                  <div class="legend-row"><span class="swatch" style="background:#38bdf8;"></span> Mandal Boundaries</div>
                </div>
              </div>"""

c = c.replace(old_block, new_block)

with open('frontend/index.html', 'w', encoding='utf-8') as f:
    f.write(c)

# Also ensure app.js queries '.workspace' everywhere
with open('frontend/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

app_js = app_js.replace("document.querySelectorAll('.workspaces-container .workspace')", "document.querySelectorAll('.workspace')")

with open('frontend/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Fixed extra div and updated app.js workspace selector successfully.")
