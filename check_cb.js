const fs = require('fs');
const path = require('path');

const cbRegex = /callback_data=["']([^"']+)["']/g;
const handlerRegex = /@router\.callback_query\([F\.]*data\s*==\s*["']([^"']+)["']\)/g;

const defined = new Set();
const handled = new Set();

function walk(dir) {
    for (const file of fs.readdirSync(dir)) {
        const full = path.join(dir, file);
        if (fs.statSync(full).isDirectory()) {
            walk(full);
        } else if (file.endsWith('.py')) {
            const content = fs.readFileSync(full, 'utf-8');
            let m;
            while ((m = cbRegex.exec(content)) !== null) defined.add(m[1]);
            while ((m = handlerRegex.exec(content)) !== null) handled.add(m[1]);
        }
    }
}

walk('telegram_bot');

console.log("DEFINED but not HANDLED:");
for (const cb of [...defined].filter(x => !handled.has(x))) {
    console.log(cb);
}

console.log("\nHANDLED but not DEFINED:");
for (const cb of [...handled].filter(x => !defined.has(x))) {
    console.log(cb);
}
