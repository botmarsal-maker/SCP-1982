const { spawnSync } = require('child_process');
const fs = require('fs');
const res = spawnSync('python3', ['test_dp.py'], {cwd: './telegram_bot', encoding: 'utf-8'});
console.log("OUT:", res.stdout);
console.log("ERR:", res.stderr);
