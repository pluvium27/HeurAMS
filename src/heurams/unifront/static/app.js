/* HeurAMS unifront */

const $ = (s, c) => (c || document).querySelector(s);
const $$ = (s, c) => Array.from((c || document).querySelectorAll(s));
const show = e => e.classList.remove('hidden');
const hide = e => e.classList.add('hidden');
const esc = s => { var d = document.createElement('div'); d.textContent = s; return d.innerHTML; };

const API = '/api';
const get = async p => { var r = await fetch(API + p); if (!r.ok) throw Error(r.status); return r.json(); };
const post = async (p, d) => { var r = await fetch(API + p, { method:'POST', headers:{'Content-Type':'application/json'}, body:d?JSON.stringify(d):null }); if (!r.ok) throw Error(r.status); return r.json(); };
const del = async p => { var r = await fetch(API + p, { method:'DELETE' }); if (!r.ok) throw Error(r.status); return r.json(); };
const put = async (p, d) => { var r = await fetch(API + p, { method:'PUT', headers:{'Content-Type':'application/json'}, body:JSON.stringify(d) }); if (!r.ok) throw Error(r.status); return r.json(); };

var App = { pkg:'', prep:null, ws:null, fav:false, prevAtom:'' };

/* === 主题 === */
function theme() { return localStorage.getItem('t') || 'light'; }
function setTheme(t) { document.body.setAttribute('data-theme', t); localStorage.setItem('t', t); $('#theme-btn').textContent = t === 'dark' ? '\u2600' : '\u263E'; }
function toggleTheme() { setTheme(theme() === 'dark' ? 'light' : 'dark'); }

/* === 布局 === */
function toggleSidebar() { $('#sidebar').classList.toggle('open'); }
function switchView(name) {
    var titles = { lobby:'仪表盘', prep:'仓库详情', review:'复习中', favs:'收藏夹', cache:'缓存管理', settings:'设置', about:'关于' };
    $('#nav-title').textContent = titles[name] || name;
    $$('.view').forEach(function(el) { if (el.id === 'view-' + name) show(el); else hide(el); });
    $$('.sidenav li').forEach(function(li) { li.classList.toggle('active', li.id === 'nav-' + name); });
    $('#sidebar').classList.remove('open');
    if (name === 'favs') loadFavs();
    if (name === 'cache') loadCache();
    if (name === 'settings') loadSettings();
    if (name === 'about') loadAbout();
}
function goBack() { if (App.ws) { App.ws.close(); App.ws = null; } switchView('lobby'); loadRepos(); }

/* === 启动 === */
document.addEventListener('DOMContentLoaded', async function() {
    setTheme(theme());
    try { var i = await get(''); $('#nav-version').textContent = 'v' + i.version; } catch(e) {}
    switchView('lobby'); loadRepos();
});

/* === 仪表盘 + 分析统计 === */
async function loadRepos() {
    show($('#loading-lobby')); hide($('#empty-lobby'));
    $('#repo-list').innerHTML = ''; $('#lobby-analysis').textContent = '';
    try {
        var repos = await get('/repos');
        var tot = 0, toc = 0;
        repos.forEach(function(r) { tot += r.total; toc += r.touched; });
        $('#lobby-stats').innerHTML =
            '<div class="stat-card"><div class="n">' + repos.length + '</div><div class="l">单元集</div></div>' +
            '<div class="stat-card"><div class="n">' + tot + '</div><div class="l">总单元</div></div>' +
            '<div class="stat-card"><div class="n">' + toc + '</div><div class="l">已学习</div></div>';

        // 分析统计
        try {
            var ana = await get('/analysis');
            var parts = [];
            if (ana.total_puzzles > 0) {
                parts.push('处理 ' + ana.total_puzzles + ' 个谜题');
                if (ana.accuracy_pct !== null) parts.push('正确率 ' + ana.accuracy_pct + '%');
                if (ana.speed_pps !== null) parts.push('速度 ' + ana.speed_pps + ' 个/秒');
            } else { parts.push('暂无复习数据'); }
            $('#lobby-analysis').textContent = parts.join(' | ');
        } catch(e) {}

        if (!repos.length) { hide($('#loading-lobby')); show($('#empty-lobby')); return; }

        repos.forEach(function(r) {
            var p = r.total > 0 ? Math.round(r.touched / r.total * 100) : 0;
            var c = document.createElement('div');
            c.className = 'repo-card';
            c.innerHTML =
                '<div style="cursor:pointer" onclick="openPrep(\'' + r.package + '\')">' +
                '<div class="title">' + esc(r.title) + '</div>' +
                '<div class="meta">' + esc(r.author) + ' &middot; ' + esc(r.package) + '</div>' +
                (r.desc ? '<div class="meta">' + esc(r.desc) + '</div>' : '') +
                '<div class="bar-wrap" style="margin:4px 0"><div class="bar-fill" style="width:' + p + '%"></div></div>' +
                '<div style="font-size:11px;color:var(--dim)">' + r.touched + '/' + r.total + ' (' + p + '%)</div></div>' +
                '<button class="btn sm pri" style="margin-top:6px" onclick="event.stopPropagation();quickStart(\'' + r.package + '\')">直接复习</button>';
            $('#repo-list').appendChild(c);
        });
        hide($('#loading-lobby'));
    } catch(e) { hide($('#loading-lobby')); $('#repo-list').innerHTML = '<div class="err-msg">加载失败</div>'; }
}

function quickStart(pkg) { openReview(pkg, 10); }

/* === 仓库详情 === */
async function openPrep(pkg) {
    App.pkg = pkg; switchView('prep');
    show($('#loading-prep')); hide($('#prep-content')); $('#prep-list').innerHTML = '';
    try {
        var d = await get('/repos/' + pkg + '/prepare');
        App.prep = d;
        var r = d.repo, p = d.progress, v = d.preview;
        var pct = p.total > 0 ? Math.round(p.touched / p.total * 100) : 0;
        $('#prep-title').textContent = r.title;
        $('#prep-meta').innerHTML = esc(r.author) + ' &middot; ' + esc(r.package) + '<br>算法: ' + esc(r.algorithm) + ' &middot; 路径: ' + esc(r.source || '');
        $('#prep-summary').innerHTML =
            '<div class="stat-card"><div class="n">' + p.total + '</div><div class="l">总单元</div></div>' +
            '<div class="stat-card"><div class="n">' + p.touched + '</div><div class="l">已学习</div></div>' +
            '<div class="stat-card"><div class="n">' + v.review + '</div><div class="l">待复习</div></div>' +
            '<div class="stat-card"><div class="n">' + v.new + '</div><div class="l">新识记</div></div>';
        $('#prep-bar').style.width = pct + '%';
        $('#prep-pct').textContent = '学习完成度: ' + p.touched + '/' + p.total + ' (' + pct + '%)';
        $('#prep-num').value = r.scheduled_num || 10;
        d.atoms.forEach(function(a) {
            var el = document.createElement('div');
            el.className = 'a-item';
            el.innerHTML = '<span class="chip chip-' + a.status + '">' + a.status + '</span><span class="id">' + esc(a.content || a.ident) + '</span><span class="r">' + (a.rept || 0) + '</span>';
            $('#prep-list').appendChild(el);
        });
        hide($('#loading-prep')); show($('#prep-content'));
    } catch(e) { hide($('#loading-prep')); $('#prep-content').innerHTML = '<div class="err-msg">加载失败</div>'; }
}
function startReviewFromPrep() { openReview(App.pkg, parseInt($('#prep-num').value) || 10); }

/* === 复习 === */
function openReview(pkg, num) {
    App.pkg = pkg; App.prevAtom = '';
    switchView('review');
    show($('#screen-start')); hide($('#screen-puzzle')); hide($('#screen-finished'));
    $('#error-box').classList.remove('show');
    $('#review-bar').style.width = '0%'; $('#review-pos').textContent = '';
    $('#review-phase').textContent = ''; setStatus('断开');
    App.fav = false; $('#fav-btn').textContent = '\u2606'; $('#fav-btn').classList.remove('faved');
    $('#tts-btn').style.display = 'none';
    $('#review-repo').textContent = (App.prep && App.prep.repo) ? App.prep.repo.title : pkg;
    var proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
    connectWS(proto + '//' + location.host + '/api/review/' + pkg, num);
}

function connectWS(url, num) {
    if (App.ws) App.ws.close();
    App.ws = new WebSocket(url);
    App.ws.onopen = function() {
        setStatus('已连接');
        App.ws.send(JSON.stringify({ action:'start', scheduled_num:num }));
        hide($('#screen-start')); show($('#screen-puzzle')); buildR();
    };
    App.ws.onclose = function() { setStatus('断开'); };
    App.ws.onerror = function() { setStatus('错误'); };
    App.ws.onmessage = function(ev) {
        try { var m = JSON.parse(ev.data); switch(m.type) {
            case 'progress': onProgress(m.data); break;
            case 'puzzle':   onPuzzle(m.data); break;
            case 'finished': onFinished(m.data); break;
            case 'error':    showError(m.message); break;
        }} catch(e) {}
    };
}

function setStatus(l) { var el = $('#review-status'); el.textContent = l; el.className = 'tag'; if (l === '已连接') el.className = 'tag pri'; }
function showError(m) { var b = $('#error-box'); b.textContent = m; b.classList.add('show'); setTimeout(function(){ b.classList.remove('show'); }, 5000); }

function onProgress(d) {
    var ls = { unsure:'准备', quick_review:'快速复习', recognition:'新记忆', final_review:'总复习', finished:'完成' };
    if (d.phase) $('#review-phase').textContent = ls[d.phase] || d.phase;
    if (d.total > 0) { $('#review-bar').style.width = Math.round(d.current / d.total * 100) + '%'; $('#review-pos').textContent = d.current + '/' + d.total; }
}

function buildR() {
    var g = $('#rating-group'); g.innerHTML = '';
    for (var i = 0; i <= 5; i++) { var b = document.createElement('button'); b.className = 'rt-btn'; b.textContent = i; b.onclick = function(){ rate(parseInt(this.textContent)); }; g.appendChild(b); }
}
function rate(r) { $$('.rt-btn').forEach(function(b){b.disabled=true;}); if (App.ws && App.ws.readyState === WebSocket.OPEN) App.ws.send(JSON.stringify({ action:'rate', rating:r })); }
function quickPass() { rate(5); }
function quickFail() { rate(2); }

/* TTS 朗读 */
function playTTS() {
    var el = $('#puzzle-card .pz-ident');
    var text = el ? el.textContent : '';
    if (!text) return;
    var audio = new Audio(API + '/tts?text=' + encodeURIComponent(text));
    audio.play().catch(function() {});
}

/* 收藏 */
function toggleFav() {
    var id = ''; var el = $('#puzzle-card .pz-ident'); if (el) id = el.textContent;
    if (!App.pkg || !id) return;
    post('/repos/' + App.pkg + '/atoms/' + encodeURIComponent(id) + '/favorite').then(function(r) {
        App.fav = r.favorited; var b = $('#fav-btn'); b.textContent = r.favorited ? '\u2605' : '\u2606';
        if (r.favorited) b.classList.add('faved'); else b.classList.remove('faved');
    }).catch(function(){});
}
function checkFav(id) {
    if (!App.pkg || !id) return;
    get('/repos/' + App.pkg + '/atoms/' + encodeURIComponent(id) + '/favorite').then(function(r) {
        App.fav = r.favorited; var b = $('#fav-btn'); b.textContent = r.favorited ? '\u2605' : '\u2606';
        if (r.favorited) b.classList.add('faved'); else b.classList.remove('faved');
    }).catch(function(){});
}

function onPuzzle(d) {
    $$('.rt-btn').forEach(function(b){b.disabled=false;});
    var card = $('#puzzle-card'); card.innerHTML = '';

    if (d.phase) { var e = document.createElement('div'); e.className = 'pz-phase'; e.textContent = d.phase; card.appendChild(e); }

    // 上一个原子（客户端追踪）
    if (App.prevAtom) {
        var e = document.createElement('div'); e.className = 'dim sm'; e.style.marginBottom = '6px';
        e.textContent = '上一个: ' + esc(App.prevAtom); card.appendChild(e);
    }

    if (d.atom_ident) {
        var e = document.createElement('div'); e.className = 'pz-ident'; e.textContent = d.atom_ident;
        card.appendChild(e); checkFav(d.atom_ident);
        $('#tts-btn').style.display = 'inline';
        App.prevAtom = d.atom_ident;
    }

    var pz = d.puzzle || {};
    if (pz.primary) { var e = document.createElement('div'); e.className = 'pz-primary'; e.textContent = pz.primary; card.appendChild(e); }
    var w = wd(pz); if (w) { var e = document.createElement('div'); e.className = 'pz-wording'; e.textContent = w; card.appendChild(e); }
    if (pz.options && Array.isArray(pz.options)) {
        var od = document.createElement('div'); od.id = 'pz-options'; var ans = Array.isArray(pz.answer) ? pz.answer : [pz.answer];
        pz.options.forEach(function(opts, qi) {
            if (!Array.isArray(opts)) return; var c = ans[qi] || ans[0];
            opts.forEach(function(opt) {
                var b = document.createElement('button'); b.className = 'pz-opt'; b.textContent = opt;
                b.onclick = function() {
                    $$('.pz-opt', od).forEach(function(x){x.classList.remove('correct','wrong');});
                    if (opt === c) { b.classList.add('correct'); } else { b.classList.add('wrong'); $$('.pz-opt', od).forEach(function(x){if(x.textContent===c)x.classList.add('correct');}); }
                    var a = card.querySelector('.pz-answer'); if (a) a.classList.add('show');
                };
                od.appendChild(b);
            });
        });
        card.appendChild(od);
    }
    var at = aw(pz); if (at) { var e = document.createElement('div'); e.className = 'pz-answer'; e.innerHTML = '<strong>正确答案: </strong>' + esc(at); card.appendChild(e); if (!pz.options || !pz.options.length) e.classList.add('show'); }
}
function wd(pz) { if (!pz.wording) return ''; return Array.isArray(pz.wording) ? pz.wording.join('\n') : String(pz.wording); }
function aw(pz) { if (!pz.answer) return ''; return Array.isArray(pz.answer) ? pz.answer.join(' | ') : String(pz.answer); }

function onFinished(d) { hide($('#screen-puzzle')); show($('#screen-finished')); $('#finish-info').textContent = '共复习 ' + (d.total_atoms || 0) + ' 个原子'; $('#finish-saved').textContent = '算法数据已保存'; if (App.ws) { App.ws.close(); App.ws = null; } }

/* === 收藏夹 === */
async function loadFavs() {
    show($('#loading-favs')); hide($('#empty-favs')); $('#favs-list').innerHTML = '';
    try {
        var items = await get('/favorites');
        if (!items.length) { hide($('#loading-favs')); show($('#empty-favs')); return; }
        items.forEach(function(f) {
            var d = new Date(f.added * 1000);
            var ts = d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0') + ' ' + String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0');
            var c = document.createElement('div'); c.className = 'fav-item';
            c.innerHTML = '<div class="fav-body"><div class="fav-ident">' + esc(f.ident) + '</div><div class="fav-meta">' + esc(f.repo_path) + ' &middot; ' + ts + '</div></div><button class="btn sm err" onclick="removeFav(\'' + esc(f.repo_path) + '\',\'' + esc(f.ident) + '\',this)">移除</button>';
            $('#favs-list').appendChild(c);
        });
        hide($('#loading-favs'));
    } catch(e) { hide($('#loading-favs')); $('#favs-list').innerHTML = '<div class="err-msg">加载失败</div>'; }
}
async function removeFav(rp, id, btn) { btn.disabled = true; try { await del('/favorites/' + encodeURIComponent(rp) + '/' + encodeURIComponent(id)); btn.parentElement.remove(); if (!$('#favs-list').children.length) show($('#empty-favs')); } catch(e) { showError('移除失败'); btn.disabled = false; } }

/* === 缓存管理 === */
async function loadCache() { show($('#loading-cache')); hide($('#cache-content')); $('#cache-msg').textContent = ''; try { var d = await get('/cache'); $('#cache-path').textContent = '路径: ' + esc(d.path); $('#cache-stats-cards').innerHTML = '<div class="stat-card"><div class="n">' + d.file_count + '</div><div class="l">缓存文件</div></div><div class="stat-card"><div class="n">' + d.human_size + '</div><div class="l">总大小</div></div>'; hide($('#loading-cache')); show($('#cache-content')); } catch(e) { hide($('#loading-cache')); $('#cache-content').innerHTML = '<div class="err-msg">加载失败</div>'; } }
async function clearCache() { if (!confirm('确定清空所有语音缓存？')) return; var btn = $('#cache-clear-btn'); btn.disabled = true; btn.textContent = '清空中...'; try { var r = await del('/cache'); $('#cache-msg').textContent = '已删除 ' + r.removed + ' 个缓存文件'; loadCache(); } catch(e) { $('#cache-msg').textContent = '清空失败'; } btn.disabled = false; btn.textContent = '清空缓存'; }
async function startPrecache() { var btn = $('#cache-precache-btn'); btn.disabled = true; btn.textContent = '生成中...'; try { var r = await post('/cache/precache'); $('#cache-msg').textContent = r.message; } catch(e) { $('#cache-msg').textContent = '启动失败'; } btn.disabled = false; btn.textContent = '生成缓存'; }

/* === 设置 === */
async function loadSettings() { show($('#loading-settings')); hide($('#settings-content')); var root = $('#settings-content'); root.innerHTML = ''; try { var tree = await get('/config'); renderSettingsTree(tree, root, 0); hide($('#loading-settings')); show($('#settings-content')); } catch(e) { hide($('#loading-settings')); root.innerHTML = '<div class="err-msg">加载失败</div>'; } }
function renderSettingsTree(nodes, parent, depth) {
    nodes.forEach(function(node) {
        if (node.type === 'branch') {
            var sec = document.createElement('div'); sec.className = 'settings-section';
            var display = depth < 2 ? 'block' : 'none';
            sec.innerHTML = '<div class="settings-section-title" onclick="toggleSec(this)">' + esc(node.key) + ' <span class="arrow">' + (display === 'block' ? '\u25BC' : '\u25B6') + '</span></div><div class="settings-section-body" style="display:' + display + '"></div>';
            parent.appendChild(sec); renderSettingsTree(node.children || [], sec.querySelector('.settings-section-body'), depth + 1);
        } else {
            var row = document.createElement('div'); row.className = 'settings-item'; var path = node.key; var val = node.value; var typ = node.type;
            var label = '<div class="settings-label">' + esc(lastKey(node.key)) + '</div>';
            if (node.desc) label += '<div class="settings-desc">' + esc(node.desc).replace(/\n/g,'<br>') + '</div>';
            var inp = '';
            if (node.candidates) {
                inp = '<select class="settings-select" data-path="' + path + '">';
                var cand = node.candidates;
                if (Array.isArray(cand)) { cand.forEach(function(c){ inp += '<option value="' + esc(String(c)) + '"' + (String(c)===String(val)?' selected':'') + '>' + esc(c) + '</option>'; }); }
                else if (typeof cand === 'object') { Object.keys(cand).forEach(function(k){ inp += '<option value="' + esc(k) + '"' + (String(k)===String(val)?' selected':'') + '>' + esc(cand[k]) + '</option>'; }); }
                inp += '</select>';
            } else if (typ === 'bool') { inp = '<label class="switch-label"><input type="checkbox" class="settings-checkbox" data-path="' + path + '"' + (val?' checked':'') + '><span class="switch-slider"></span></label>'; }
            else if (typ === 'int'||typ==='number'||typ==='float') { inp = '<input type="number" class="settings-input" data-path="' + path + '" value="' + esc(String(val)) + '" step="' + (typ==='float'?'0.1':'1') + '">'; }
            else { inp = '<input type="text" class="settings-input" data-path="' + path + '" value="' + esc(String(val)) + '">'; }
            row.innerHTML = label + '<div class="settings-control">' + inp + '</div>'; parent.appendChild(row);
        }
    });
    parent.querySelectorAll('.settings-input, .settings-select').forEach(function(el){ el.addEventListener('change', saveSetting); });
    parent.querySelectorAll('.settings-checkbox').forEach(function(el){ el.addEventListener('change', saveSetting); });
}
function lastKey(p) { var ps = p.split('.'); return ps[ps.length - 1]; }
function toggleSec(h) { var b = h.parentElement.querySelector('.settings-section-body'); var a = h.querySelector('.arrow'); if (b.style.display === 'none') { b.style.display = 'block'; a.innerHTML = '\u25BC'; } else { b.style.display = 'none'; a.innerHTML = '\u25B6'; } }
async function saveSetting(ev) { var el = ev.target; var path = el.dataset.path; var val; if (el.type === 'checkbox') val = el.checked; else if (el.tagName === 'SELECT') val = el.value; else if (el.type === 'number') val = el.value.includes('.') ? parseFloat(el.value) : parseInt(el.value); else val = el.value; try { await put('/config/' + path.replace(/\./g,'/'), { value:val, path:path }); el.style.borderColor = 'var(--suc)'; setTimeout(function(){ el.style.borderColor = ''; }, 1500); } catch(e) { el.style.borderColor = 'var(--err)'; } }

/* === 关于 === */
async function loadAbout() { try { var d = await get('/about'); $('#about-version').textContent = '版本 ' + d.version + ' ' + d.stage; $('#about-codename').textContent = '代号: ' + d.codename + ' (' + d.codename_cn + ')'; $('#about-env').innerHTML = '<tr><td>Python</td><td>' + d.python_version + '</td></tr><tr><td>路径</td><td class="dim">' + esc(d.python_path) + '</td></tr><tr><td>OS</td><td>' + esc(d.os) + '</td></tr><tr><td>平台</td><td class="dim">' + esc(d.platform) + '</td></tr><tr><td>虚拟环境</td><td>' + (d.in_virtualenv?'是':'否') + '</td></tr><tr><td>磁盘</td><td>' + d.disk_free_gb + '/' + d.disk_total_gb + ' GB (' + d.disk_free_pct + '%)</td></tr>'; } catch(e) { $('#about-env').innerHTML = '<tr><td>加载失败</td></tr>'; } }
