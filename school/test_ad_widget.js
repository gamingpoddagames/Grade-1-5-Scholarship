// Exercise our loader only; no vendor script, browser, network or paid impressions.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync('school/blogger_optional_adsterra_widget.html', 'utf8').match(/<script>([\s\S]*?)<\/script>/)[1];
assert.match(source, /^\s*\(function/);
assert.ok(!/[^\x00-\x7F]/.test(source), 'Keep script ASCII so Blogger cannot turn Sinhala into HTML entities');
const nodes = {};
const handlers = {};
let loads = 0;
const button = { disabled: false, attrs: {}, getAttribute(k) {return this.attrs[k];}, setAttribute(k,v) {this.attrs[k]=v;}, addEventListener(k,fn) {handlers[k]=fn;} };
const status = {textContent: ''};
const document = {
  getElementById(id) {return id==='punchi-show-ad'?button:id==='punchi-ad-status'?status:nodes[id];},
  createElement(tag) {assert.equal(tag,'script'); return {setAttribute(){},remove(){delete nodes[this.id];}};},
  body: {appendChild(node) {loads++; nodes[node.id]=node;}}
};
const context = vm.createContext({document, setTimeout(){return 1;}, clearTimeout(){}});
vm.runInContext(source, context);
assert.equal(loads,0, 'No ad request on page load');
handlers.click();
assert.equal(loads,1);
assert.equal(button.disabled,true);
assert.equal(nodes['punchi-adsterra-loader'].src,'https://bicea.org/14/3777aa5b8fbe2c3a7513a1e6dc0637c5');
nodes['punchi-adsterra-loader'].onload();
assert.ok(status.textContent.includes('පූරණය විය'));
assert.ok(!status.textContent.includes('&#'));
handlers.click();
assert.equal(loads,1,'Prevent duplicate ad loads');
nodes['punchi-adsterra-loader'].onerror();
assert.equal(button.disabled,false);
handlers.click();
assert.equal(loads,2,'Allow deliberate retry after an error');
console.log('PASS: opt-in only, one loader, readable Sinhala, failure recovery; no network calls.');
