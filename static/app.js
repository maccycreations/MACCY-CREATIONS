const $ = (id) => document.getElementById(id);
const json = async (url, options = {}) => (await fetch(url, {headers: {'Content-Type': 'application/json'}, ...options})).json();

document.querySelectorAll('[data-tab]').forEach(button => button.onclick = () => {
  document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
  $(button.dataset.tab).classList.add('active');
});

async function load() {
  const dashboard = await json('/api/local/dashboard');
  $('stats').innerHTML = Object.entries(dashboard).filter(([k]) => k !== 'top_skills').map(([key, value]) => `<article class="stat-box"><span>${key}</span><strong>${value}</strong></article>`).join('');
  for (const [endpoint, target, fields] of [['skills','skills-list',['name','category','progress']],['careers','careers-list',['title','level','skills']],['roadmaps','roadmaps-list',['title','target_role','steps']],['applications','applications-list',['company','title','status']]]) {
    const rows = await json(`/api/local/${endpoint}`);
    $(target).innerHTML = rows.map(row => `<article class="panel"><h3>${row[fields[0]]}</h3><p>${fields.slice(1).map(field => `${field}: ${row[field] || ''}`).join('<br>')}</p></article>`).join('') || '<p>No records yet.</p>';
  }
}
$('job-search').onclick = async () => {
  const rows = await json(`/api/product/jobs/search?q=${encodeURIComponent($('job-query').value)}`);
  $('jobs-list').innerHTML = rows.map(job => `<article class="panel"><h3><a href="${job.url || '#'}" target="_blank">${job.title}</a></h3><p>${job.company} · ${job.location} · ${job.source}</p></article>`).join('') || '<p>No matching public listings.</p>';
};
$('ats-button').onclick = async () => {
  const result = await json('/api/product/ats/analyze', {method:'POST', body: JSON.stringify({resume_text:$('resume-text').value, job_description:$('job-text').value})});
  $('ats-result').textContent = JSON.stringify(result, null, 2);
};
$('ai-button').onclick = async () => {
  const result = await json('/api/product/ai/complete', {method:'POST', body: JSON.stringify({provider:$('ai-provider').value, prompt:$('ai-prompt').value})});
  $('ai-result').textContent = JSON.stringify(result, null, 2);
};
load();
