// Run with: node --test tests/frontend.test.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');

function page(fetch) {
  const elements = {};
  let expire;
  let cleared = false;
  for (const id of ['shorten-form', 'message', 'result', 'short-link', 'submit', 'copy', 'url']) {
    elements['#' + id] = {
      value: 'https://example.com', textContent: '', hidden: true, disabled: false,
      addEventListener(event, handler) { this[event] = handler; }
    };
  }
  vm.runInNewContext(fs.readFileSync('static/app.js', 'utf8'), {
    document: {querySelector: id => elements[id]}, fetch, AbortController,
    setTimeout(callback, milliseconds) { assert.equal(milliseconds, 10000); expire = callback; return 1; },
    clearTimeout() { cleared = true; }
  });
  return {elements, expire: () => expire(), cleared: () => cleared,
    submit: () => elements['#shorten-form'].submit({preventDefault() {}})};
}

test('unresponsive server times out and restores the button', async () => {
  const ui = page((url, {signal}) => new Promise((resolve, reject) => {
    signal.addEventListener('abort', () => reject(Object.assign(new Error(), {name: 'AbortError'})));
  }));
  const pending = ui.submit();
  assert.equal(ui.elements['#submit'].disabled, true);
  assert.equal(ui.elements['#submit'].textContent, 'Shortening…');
  ui.expire();
  await pending;
  assert.equal(ui.elements['#submit'].disabled, false);
  assert.match(ui.elements['#message'].textContent, /server is not responding/);
  assert.equal(ui.cleared(), true);
});

test('successful response displays the generated link', async () => {
  const ui = page(async () => ({ok: true, json: async () => ({short_url: 'http://localhost:8000/abc1234'})}));
  await ui.submit();
  assert.equal(ui.elements['#result'].hidden, false);
  assert.equal(ui.elements['#short-link'].href, 'http://localhost:8000/abc1234');
  assert.equal(ui.elements['#submit'].disabled, false);
  assert.equal(ui.cleared(), true);
});

test('network failure displays an error and restores the button', async () => {
  const ui = page(async () => { throw new Error('Failed to fetch'); });
  await ui.submit();
  assert.equal(ui.elements['#message'].textContent, 'Failed to fetch');
  assert.equal(ui.elements['#submit'].disabled, false);
  assert.equal(ui.elements['#result'].hidden, true);
});
