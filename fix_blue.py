import os

def replace_in_file(filepath, replacements):
    with open(filepath, 'r') as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(filepath, 'w') as f:
        f.write(content)

# 1. index.css
index_replacements = [
    ('--accent-blue: #00e5ff;', '--accent-blue: #D4AF37;'),
    ('--accent-blue-glow: rgba(0, 229, 255, 0.4);', '--accent-blue-glow: rgba(212, 175, 55, 0.4);'),
    ('rgba(0, 229, 255, 0.2)', 'rgba(212, 175, 55, 0.2)'),
    ('rgba(0, 229, 255, 0.4)', 'rgba(212, 175, 55, 0.4)'),
]
replace_in_file('web_app/src/index.css', index_replacements)

# 2. PowerRankings.jsx
pr_replacements = [
    ("background: 'linear-gradient(90deg, var(--accent-blue), #00ffcc)'", "background: 'linear-gradient(90deg, #D4AF37, #FFDF73)'"),
    ("rgba(0, 229, 255, 0.5)", "rgba(212, 175, 55, 0.5)"),
    ("var(--accent-blue)", "var(--accent-gold)"),
]
replace_in_file('web_app/src/components/PowerRankings.jsx', pr_replacements)

# 3. BracketSimulator.jsx
bs_replacements = [
    ("'#00e5ff'", "'#111111'"),
    ("var(--accent-blue)", "var(--accent-gold)"),
    ("background: isSimulating ? '#555' : 'linear-gradient(90deg, var(--accent-gold), #00ffcc)'", "background: isSimulating ? '#555' : 'linear-gradient(90deg, #D4AF37, #FFDF73)'"),
    ("background: isSimulating ? '#555' : 'linear-gradient(90deg, var(--accent-blue), #00ffcc)'", "background: isSimulating ? '#555' : 'linear-gradient(90deg, #D4AF37, #FFDF73)'"),
    ("rgba(0, 229, 255, 0.3)", "rgba(212, 175, 55, 0.3)"),
]
replace_in_file('web_app/src/components/BracketSimulator.jsx', bs_replacements)

# 4. Spotlight.jsx
sl_replacements = [
    ('text-blue', 'text-gold'),
]
replace_in_file('web_app/src/components/Spotlight.jsx', sl_replacements)

print("Replaced icy blue with gold/black across files.")
