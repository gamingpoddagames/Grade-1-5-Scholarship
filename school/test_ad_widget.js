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
// Browser-session consent: one explicit first click, then automatic loader on
// subsequent Blogger pages opened in the same tab; no automatic first-visit ads.
function simulateSession(approved) {
  const localNodes = {};
  const localHandlers = {};
  let requests = 0;
  const consentData = approved ? {'punchi-socialbar-session-consent': 'yes'} : {};
  const sessionStorage = {
    getItem(key) {return consentData[key] || null;},
    setItem(key,value) {consentData[key]=value;},
    removeItem(key) {delete consentData[key];}
  };
  const localButton = {
    disabled:false,attrs:{},
    getAttribute(key){return this.attrs[key];},
    setAttribute(key,value){this.attrs[key]=value;},
    addEventListener(key,handler){localHandlers[key]=handler;}
  };
  const localStatus = {textContent:''};
  const localDocument = {
    getElementById(id) {
      return id==='punchi-show-ad'?localButton:
             id==='punchi-ad-status'?localStatus:localNodes[id];
    },
    createElement(tag) {
      assert.equal(tag,'script');
      return {setAttribute(){},remove(){delete localNodes[this.id];}};
    },
    body:{appendChild(script){requests++;localNodes[script.id]=script;}}
  };
  const ctx = vm.createContext({document:localDocument,window:{sessionStorage},setTimeout(){return 1;},clearTimeout(){}});
  vm.runInContext(source,ctx);
  return {requests:()=>requests, click:()=>localHandlers.click(),
          current:()=>localNodes['punchi-adsterra-loader'],
          saved:()=>sessionStorage.getItem('punchi-socialbar-session-consent')};
}
const fresh = simulateSession(false);
assert.equal(fresh.requests(),0,'Do not auto-load ads before a visitor opts in');
fresh.click();
assert.equal(fresh.requests(),1);
assert.equal(fresh.saved(),'yes');
const returning = simulateSession(true);
assert.equal(returning.requests(),1,'Auto-load once on a later page in the same consented tab');
returning.click();
assert.equal(returning.requests(),1,'Never create two Adsterra scripts');
returning.current().onerror();
assert.equal(returning.saved(),null,'Remove session permission if the vendor loader fails');
console.log('PASS: explicit first opt-in, session-level auto-display on next page, single loader, failure recovery; no real ads requested.');
