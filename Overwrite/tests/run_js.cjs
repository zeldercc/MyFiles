const fs = require('node:fs');
const vm = require('node:vm');
const [scriptFile, baseFile] = process.argv.slice(2);
const context = vm.createContext({});
vm.runInContext(fs.readFileSync(scriptFile, 'utf8'), context, {timeout: 1000});
context.config = JSON.parse(fs.readFileSync(baseFile, 'utf8'));
const result = vm.runInContext('main(config)', context, {timeout: 1000});
process.stdout.write(JSON.stringify(result));
