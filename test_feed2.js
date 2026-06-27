const { spawnSync } = require('child_process');
const fs = require('fs');

const res = spawnSync('python3', ['test_feed.py'], {encoding: 'utf-8'});
console.log("OUT:", res.stdout);
console.log("ERR:", res.stderr);
