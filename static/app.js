const form = document.querySelector('#shorten-form');
const message = document.querySelector('#message');
const result = document.querySelector('#result');
const link = document.querySelector('#short-link');
const submit = document.querySelector('#submit');
form.addEventListener('submit', async (event) => {
  event.preventDefault();
  result.hidden = true;
  message.textContent = '';
  submit.disabled = true;
  submit.textContent = 'Shortening…';
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 10000);
  try {
    const response = await fetch('/api/shorten', {
      signal: controller.signal,
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({url: document.querySelector('#url').value.trim()})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to shorten this link.');
    link.href = data.short_url;
    link.textContent = data.short_url;
    result.hidden = false;
  } catch (error) {
    message.textContent = error.name === 'AbortError'
      ? 'The server is not responding. Check that the application is running, then retry.'
      : error.message || 'Connection failed. Please retry.';
  }
  finally {
    clearTimeout(timeout);
    submit.disabled = false;
    submit.textContent = 'Shorten link ↗';
  }
});
document.querySelector('#copy').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(link.textContent); message.textContent = 'Link copied!'; }
  catch { message.textContent = 'Select the short link and press Ctrl+C to copy it.'; }
});
