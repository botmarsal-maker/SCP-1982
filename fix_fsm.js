const fs = require('fs');

function fix(fname) {
    let content = fs.readFileSync(fname, 'utf-8');
    
    const handlerPattern = /@router\.message\([\w\.]*State\.[^\)]+\)\nasync def[^\(]+\(message:\s*Message,\s*state:\s*FSMContext\):/g;
    
    let match;
    let offset = 0;
    while ((match = handlerPattern.exec(content)) !== null) {
        let endIndex = match.index + match[0].length;
        
        // Skip if it's process_admin_pin or process_broadcast which might be already handled or different
        if (match[0].includes('process_admin_pin')) continue;
        if (match[0].includes('process_broadcast')) continue; // because broadcast can accept photos
        
        let existingCheck = content.substring(endIndex, endIndex + 100);
        if (existingCheck.includes('if not message.text:')) continue;
        
        let insert = `\n    if not message.text:\n        await message.answer("❌ Harap kirimkan pesan teks.")\n        return\n`;
        content = content.substring(0, endIndex) + insert + content.substring(endIndex);
        
        // Adjust regex index since string length changed
        handlerPattern.lastIndex += insert.length;
    }
    
    fs.writeFileSync(fname, content);
}

fix("telegram_bot/handlers/admin.py");
fix("telegram_bot/handlers/clone_admin.py");
