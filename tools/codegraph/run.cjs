// Run the pinned navigation tool against this checkout, with telemetry and
// implicit binary downloads disabled. The index is disposable local state.
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const root = path.resolve(__dirname, '../..');
const launcher = path.join(__dirname, 'node_modules/@colbymchenry/codegraph/npm-shim.js');
if (!fs.existsSync(launcher)) {
  process.stderr.write('Run npm ci --prefix tools/codegraph --ignore-scripts first.\n');
  process.exit(1);
}

// An empty upstream invocation launches an interactive agent installer. Help is
// the useful default here; project integration is owned by AGENTS.md instead.
const args = process.argv.length > 2 ? process.argv.slice(2) : ['--help'];
const result = spawnSync(process.execPath, [launcher, ...args], {
  cwd: root,
  env: { ...process.env, CODEGRAPH_TELEMETRY: '0', CODEGRAPH_NO_DOWNLOAD: '1' },
  stdio: 'inherit',
  windowsHide: true,
});
if (result.error) process.stderr.write(`${result.error.message}\n`);
process.exit(result.status ?? 1);
