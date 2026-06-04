const fs = require('fs');
let css = fs.readFileSync('src/index.css', 'utf8');

// Replace left pair after
css = css.replace(/right: -20px;\n\s+top: 25%;\n\s+bottom: 25%;\n\s+width: 20px;/g, 'right: -15px;\n  top: 25%;\n  bottom: 25%;\n  width: 15px;');
// Replace left line
css = css.replace(/right: -40px;\n\s+top: 50%;\n\s+width: 20px;/g, 'right: -30px;\n  top: 50%;\n  width: 15px;');

// Replace right pair after
css = css.replace(/left: -20px;\n\s+top: 25%;\n\s+bottom: 25%;\n\s+width: 20px;/g, 'left: -15px;\n  top: 25%;\n  bottom: 25%;\n  width: 15px;');
// Replace right line
css = css.replace(/left: -40px;\n\s+top: 50%;\n\s+width: 20px;/g, 'left: -30px;\n  top: 50%;\n  width: 15px;');

fs.writeFileSync('src/index.css', css);
