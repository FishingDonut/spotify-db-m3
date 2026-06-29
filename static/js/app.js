// State Management
let currentSection = 'artistas';
let searchQuery = '';
let caches = {
    artistas: [],
    albuns: [],
    pagamentos: []
};

// DOM Elements
const navLinks = document.querySelectorAll('.nav-link');
const sectionTitle = document.getElementById('section-title');
const searchInput = document.getElementById('search-input');
const addBtn = document.getElementById('add-btn');
const addBtnText = document.getElementById('add-btn-text');
const tableHeaders = document.getElementById('table-headers');
const tableBody = document.getElementById('table-body');
const emptyState = document.getElementById('empty-state');
const dataTable = document.getElementById('data-table');
const consoleBody = document.getElementById('console-body');
const clearConsoleBtn = document.getElementById('clear-console-btn');

// Load App
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

function initApp() {
    setupNavigation();
    setupSearch();
    setupConsole();
    setupModals();
    setupForms();
    
    // Load initial data
    loadSection(currentSection);
    refreshDropdownCaches();
}

// 1. Navigation Setup
function setupNavigation() {
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');
            
            const target = link.getAttribute('data-target');
            currentSection = target;
            
            // Reset search query
            searchQuery = '';
            searchInput.value = '';
            
            // Adjust header UI
            updateHeaderUI();
            
            // Load section
            loadSection(currentSection);
        });
    });
}

function updateHeaderUI() {
    const searchBox = document.querySelector('.search-box');
    
    if (currentSection === 'top-musicas') {
        sectionTitle.textContent = 'Top 10 Músicas Mais Ouvidas';
        searchBox.classList.add('hidden');
        addBtn.classList.add('hidden');
    } else {
        searchBox.classList.remove('hidden');
        addBtn.classList.remove('hidden');
        
        switch (currentSection) {
            case 'artistas':
                sectionTitle.textContent = 'Artistas';
                addBtnText.textContent = 'Novo Artista';
                searchInput.placeholder = 'Buscar artista pelo nome...';
                break;
            case 'albuns':
                sectionTitle.textContent = 'Álbuns';
                addBtnText.textContent = 'Novo Álbum';
                searchInput.placeholder = 'Filtrar álbuns...'; // Client-side filter
                break;
            case 'musicas':
                sectionTitle.textContent = 'Músicas';
                addBtnText.textContent = 'Nova Música';
                searchInput.placeholder = 'Filtrar músicas...'; // Client-side filter
                break;
            case 'usuarios':
                sectionTitle.textContent = 'Usuários';
                addBtnText.textContent = 'Novo Usuário';
                searchInput.placeholder = 'Filtrar usuários...'; // Client-side filter
                break;
        }
    }
}

// 2. Search Setup
function setupSearch() {
    searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value.toLowerCase().trim();
        if (currentSection === 'artistas') {
            // Server-side search for Artistas
            loadSection('artistas');
        } else {
            // Client-side filtering for other entities
            filterTableRows();
        }
    });
}

function filterTableRows() {
    const rows = tableBody.querySelectorAll('tr');
    let hasVisible = false;
    
    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        if (text.includes(searchQuery)) {
            row.classList.remove('hidden');
            hasVisible = true;
        } else {
            row.classList.add('hidden');
        }
    });
    
    if (!hasVisible && rows.length > 0) {
        emptyState.classList.remove('hidden');
        dataTable.classList.add('hidden');
    } else if (rows.length > 0) {
        emptyState.classList.add('hidden');
        dataTable.classList.remove('hidden');
    }
}

// 3. SQL Console Logger Setup
function setupConsole() {
    clearConsoleBtn.addEventListener('click', () => {
        consoleBody.innerHTML = '';
        logToConsole('[SISTEMA] Console limpo.', 'system');
    });
}

function logToConsole(message, type = 'query') {
    const line = document.createElement('div');
    line.className = `console-line ${type}-line`;
    
    const timestamp = new Date().toLocaleTimeString();
    if (type === 'query') {
        line.innerHTML = `<span class="system-line">[${timestamp}] [SQL-ORM]</span> ${message}`;
    } else if (type === 'error') {
        line.innerHTML = `<span class="system-line">[${timestamp}] [ERRO]</span> ${message}`;
    } else {
        line.innerHTML = `<span class="system-line">[${timestamp}]</span> ${message}`;
    }
    
    consoleBody.appendChild(line);
    consoleBody.scrollTop = consoleBody.scrollHeight;
}

// 4. Modals & Forms Manager
let activeModal = null;

function setupModals() {
    addBtn.addEventListener('click', () => {
        openCreateModal();
    });
    
    // Close modal handlers
    document.querySelectorAll('.close-modal-btn, .btn-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal();
        });
    });
    
    // Close on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeModal();
            }
        });
    });
}

function openModal(modalId) {
    closeModal();
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('active');
        activeModal = modal;
    }
}

function closeModal() {
    if (activeModal) {
        activeModal.classList.remove('active');
        const form = activeModal.querySelector('form');
        if (form) form.reset();
        activeModal = null;
    }
}

function openCreateModal() {
    refreshDropdownOptions().then(() => {
        if (currentSection === 'artistas') {
            document.getElementById('modal-artista-title').textContent = 'Novo Artista';
            document.getElementById('form-artista').querySelector('input[name="id"]').value = '';
            openModal('modal-artista');
        } else if (currentSection === 'albuns') {
            document.getElementById('modal-album-title').textContent = 'Novo Álbum';
            document.getElementById('form-album').querySelector('input[name="id"]').value = '';
            document.getElementById('alb-ano').value = new Date().getFullYear();
            openModal('modal-album');
        } else if (currentSection === 'musicas') {
            document.getElementById('modal-musica-title').textContent = 'Nova Música';
            document.getElementById('form-musica').querySelector('input[name="id"]').value = '';
            document.getElementById('mus-ano').value = new Date().getFullYear();
            openModal('modal-musica');
        } else if (currentSection === 'usuarios') {
            document.getElementById('modal-usuario-title').textContent = 'Novo Usuário';
            document.getElementById('form-usuario').querySelector('input[name="id"]').value = '';
            openModal('modal-usuario');
        }
    });
}

// 5. Caches and Dropdowns population
async function refreshDropdownCaches() {
    try {
        const fetchArt = await fetch('/api/artistas');
        const artRes = await fetchArt.json();
        caches.artistas = artRes.data;
        
        const fetchAlb = await fetch('/api/albuns');
        const albRes = await fetchAlb.json();
        caches.albuns = albRes.data;
        
        const fetchPag = await fetch('/api/pagamentos');
        const pagRes = await fetchPag.json();
        caches.pagamentos = pagRes.data;
    } catch (err) {
        console.error("Erro ao carregar caches", err);
    }
}

async function refreshDropdownOptions() {
    await refreshDropdownCaches();
    
    // Artista selectors in Album and Musica
    const albArtistaSelect = document.getElementById('alb-artista');
    const musArtistaSelect = document.getElementById('mus-artista');
    
    const artOptions = caches.artistas.map(a => `<option value="${a.id}">${a.nome}</option>`).join('');
    albArtistaSelect.innerHTML = `<option value="" disabled selected>Selecione um artista...</option>` + artOptions;
    musArtistaSelect.innerHTML = `<option value="" disabled selected>Selecione um artista...</option>` + artOptions;
    
    // Album selector in Musica
    const musAlbumSelect = document.getElementById('mus-album');
    const albOptions = caches.albuns.map(a => `<option value="${a.id}">${a.titulo} (${a.ano})</option>`).join('');
    musAlbumSelect.innerHTML = `<option value="None">Sem Álbum (Single)</option>` + albOptions;
    
    // Pagamento selector in Usuario
    const usrPagamentoSelect = document.getElementById('usr-pagamento');
    const pagOptions = caches.pagamentos.map(p => `<option value="${p.id}">Pagamento #${p.id} - ${p.plano_tipo} (${p.status})</option>`).join('');
    usrPagamentoSelect.innerHTML = `<option value="None">Nenhum plano ativo (Free)</option>` + pagOptions;
}

// 6. Load Data & Render Tables
async function loadSection(section) {
    try {
        let url = `/api/${section}`;
        if (section === 'artistas' && searchQuery) {
            url += `?search=${encodeURIComponent(searchQuery)}`;
        }
        
        const response = await fetch(url);
        const result = await response.json();
        
        // Log query SQL
        if (result.sql) {
            logToConsole(result.sql);
        }
        
        renderTable(section, result.data);
    } catch (err) {
        logToConsole(err.message, 'error');
    }
}

function renderTable(section, data) {
    tableHeaders.innerHTML = '';
    tableBody.innerHTML = '';
    
    if (!data || data.length === 0) {
        emptyState.classList.remove('hidden');
        dataTable.classList.add('hidden');
        return;
    }
    
    emptyState.classList.add('hidden');
    dataTable.classList.remove('hidden');
    
    // Render dynamic headers and rows
    if (section === 'artistas') {
        tableHeaders.innerHTML = `
            <th>ID</th>
            <th>Nome</th>
            <th>Descrição</th>
            <th>Seguidores</th>
            <th>Ouvintes Mensais</th>
            <th>Ações</th>
        `;
        data.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>#${item.id}</strong></td>
                <td><span class="text-white font-semibold">${item.nome}</span></td>
                <td title="${item.descricao || ''}">${truncateText(item.descricao || 'Sem descrição', 50)}</td>
                <td>${formatNumber(item.seguidores)}</td>
                <td>${formatNumber(item.ouvintes_mensais)}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-action btn-action-edit" onclick="editItem('artistas', ${item.id})" title="Editar"><i class="fa-solid fa-pen"></i></button>
                        <button class="btn-action btn-action-delete" onclick="deleteItem('artistas', ${item.id})" title="Remover"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </td>
            `;
            tableBody.appendChild(tr);
        });
    } 
    else if (section === 'albuns') {
        tableHeaders.innerHTML = `
            <th>ID</th>
            <th>Título</th>
            <th>Ano</th>
            <th>Artista</th>
            <th>Gênero</th>
            <th>Capa URL</th>
            <th>Ações</th>
        `;
        data.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>#${item.id}</strong></td>
                <td><span class="text-white font-semibold">${item.titulo}</span></td>
                <td>${item.ano}</td>
                <td>${item.artista_nome}</td>
                <td><span class="text-secondary">${item.genero || 'N/A'}</span></td>
                <td><code class="text-muted">${item.capa_url || 'N/A'}</code></td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-action btn-action-edit" onclick="editItem('albuns', ${item.id})" title="Editar"><i class="fa-solid fa-pen"></i></button>
                        <button class="btn-action btn-action-delete" onclick="deleteItem('albuns', ${item.id})" title="Remover"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </td>
            `;
            tableBody.appendChild(tr);
        });
    } 
    else if (section === 'musicas') {
        tableHeaders.innerHTML = `
            <th style="width: 50px;">Ouvir</th>
            <th>ID</th>
            <th>Título</th>
            <th>Duração</th>
            <th>Reproduções</th>
            <th>Artista</th>
            <th>Álbum</th>
            <th>Gênero</th>
            <th>Ano</th>
            <th>Ações</th>
        `;
        data.forEach(item => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>
                    <button class="btn-action btn-action-play" onclick="playMusic(${item.id})" title="Simular Reprodução (Dispara Trigger)">
                        <i class="fa-solid fa-play"></i>
                    </button>
                </td>
                <td><strong>#${item.id}</strong></td>
                <td><span class="text-white font-semibold">${item.titulo}</span></td>
                <td>${formatDuration(item.duracao)}</td>
                <td id="repro-count-${item.id}">${formatNumber(item.reproducoes)}</td>
                <td>${item.artista_nome}</td>
                <td>${item.album_titulo}</td>
                <td>${item.genero || 'N/A'}</td>
                <td>${item.ano}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-action btn-action-edit" onclick="editItem('musicas', ${item.id})" title="Editar"><i class="fa-solid fa-pen"></i></button>
                        <button class="btn-action btn-action-delete" onclick="deleteItem('musicas', ${item.id})" title="Remover"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </td>
            `;
            tableBody.appendChild(tr);
        });
    } 
    else if (section === 'usuarios') {
        tableHeaders.innerHTML = `
            <th>ID</th>
            <th>Nome</th>
            <th>Email</th>
            <th>Nascimento</th>
            <th>País</th>
            <th>Plano</th>
            <th>Status Assinatura</th>
            <th>Ações</th>
        `;
        data.forEach(item => {
            const tr = document.createElement('tr');
            const birthDate = item.data_nascimento ? new Date(item.data_nascimento).toLocaleDateString('pt-BR') : 'N/A';
            const statusClass = (item.pagamento_status || '').toLowerCase();
            tr.innerHTML = `
                <td><strong>#${item.id}</strong></td>
                <td><span class="text-white font-semibold">${item.nome}</span></td>
                <td>${item.email}</td>
                <td>${birthDate}</td>
                <td>${item.pais || 'N/A'}</td>
                <td><span class="text-secondary">${item.plano_tipo}</span></td>
                <td>
                    <span class="pill-badge ${statusClass}">
                        ${item.pagamento_status}
                    </span>
                </td>
                <td>
                    <div class="action-buttons">
                        <button class="btn-action btn-action-edit" onclick="editItem('usuarios', ${item.id})" title="Editar"><i class="fa-solid fa-pen"></i></button>
                        <button class="btn-action btn-action-delete" onclick="deleteItem('usuarios', ${item.id})" title="Remover"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </td>
            `;
            tableBody.appendChild(tr);
        });
    }
    else if (section === 'top-musicas') {
        tableHeaders.innerHTML = `
            <th>Posição</th>
            <th>Música</th>
            <th>Artista</th>
            <th>Total de Reproduções</th>
        `;
        data.forEach((item, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>#${index + 1}</strong></td>
                <td><span class="text-white font-semibold"><i class="fa-solid fa-music text-muted" style="margin-right: 8px;"></i>${item.titulo}</span></td>
                <td>${item.artista}</td>
                <td>${formatNumber(item.reproducoes)} reproduções</td>
            `;
            tableBody.appendChild(tr);
        });
    }
}

// 7. Form Submissions (Create and Update)
function setupForms() {
    // Submit Artista Form
    document.getElementById('form-artista').addEventListener('submit', (e) => handleFormSubmit(e, 'artistas', 'form-artista'));
    // Submit Album Form
    document.getElementById('form-album').addEventListener('submit', (e) => handleFormSubmit(e, 'albuns', 'form-album'));
    // Submit Musica Form
    document.getElementById('form-musica').addEventListener('submit', (e) => handleFormSubmit(e, 'musicas', 'form-musica'));
    // Submit Usuario Form
    document.getElementById('form-usuario').addEventListener('submit', (e) => handleFormSubmit(e, 'usuarios', 'form-usuario'));
}

async function handleFormSubmit(e, section, formId) {
    e.preventDefault();
    const form = document.getElementById(formId);
    const formData = new FormData(form);
    
    // Parse to JSON
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });
    
    const id = data.id;
    const isEdit = id && id !== '';
    
    const url = isEdit ? `/api/${section}/${id}` : `/api/${section}`;
    const method = isEdit ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Erro na operação.');
        }
        
        if (result.sql) {
            logToConsole(result.sql);
        }
        
        logToConsole(`[SISTEMA] Registro de ${section} salvo com sucesso!`, 'system');
        closeModal();
        loadSection(currentSection);
        refreshDropdownCaches();
    } catch (err) {
        logToConsole(err.message, 'error');
        alert(err.message);
    }
}

// 8. Edit Operations
async function editItem(section, id) {
    await refreshDropdownOptions();
    
    try {
        // Fetch or read from list cache
        let item = null;
        if (section === 'artistas') {
            item = caches.artistas.find(x => x.id == id);
            if (!item) {
                const response = await fetch(`/api/artistas`);
                const res = await response.json();
                item = res.data.find(x => x.id == id);
            }
            if (item) {
                const form = document.getElementById('form-artista');
                form.querySelector('input[name="id"]').value = item.id;
                form.querySelector('input[name="nome"]').value = item.nome;
                form.querySelector('textarea[name="descricao"]').value = item.descricao || '';
                form.querySelector('input[name="seguidores"]').value = item.seguidores || 0;
                form.querySelector('input[name="ouvintes_mensais"]').value = item.ouvintes_mensais || 0;
                
                document.getElementById('modal-artista-title').textContent = 'Editar Artista';
                openModal('modal-artista');
            }
        } 
        else if (section === 'albuns') {
            item = caches.albuns.find(x => x.id == id);
            if (item) {
                const form = document.getElementById('form-album');
                form.querySelector('input[name="id"]').value = item.id;
                form.querySelector('input[name="titulo"]').value = item.titulo;
                form.querySelector('input[name="ano"]').value = item.ano;
                form.querySelector('select[name="id_artista"]').value = item.id_artista;
                form.querySelector('input[name="genero"]').value = item.genero || '';
                form.querySelector('input[name="capa_url"]').value = item.capa_url || '';
                
                document.getElementById('modal-album-title').textContent = 'Editar Álbum';
                openModal('modal-album');
            }
        } 
        else if (section === 'musicas') {
            // Find music
            const response = await fetch(`/api/musicas`);
            const res = await response.json();
            item = res.data.find(x => x.id == id);
            
            if (item) {
                const form = document.getElementById('form-musica');
                form.querySelector('input[name="id"]').value = item.id;
                form.querySelector('input[name="titulo"]').value = item.titulo;
                form.querySelector('input[name="duracao"]').value = item.duracao;
                form.querySelector('input[name="ano"]').value = item.ano;
                form.querySelector('input[name="genero"]').value = item.genero || '';
                form.querySelector('input[name="reproducoes"]').value = item.reproducoes || 0;
                form.querySelector('select[name="id_artista"]').value = item.id_artista;
                form.querySelector('select[name="id_album"]').value = item.id_album || 'None';
                form.querySelector('textarea[name="letra"]').value = item.letra || '';
                
                document.getElementById('modal-musica-title').textContent = 'Editar Música';
                openModal('modal-musica');
            }
        } 
        else if (section === 'usuarios') {
            const response = await fetch(`/api/usuarios`);
            const res = await response.json();
            item = res.data.find(x => x.id == id);
            
            if (item) {
                const form = document.getElementById('form-usuario');
                form.querySelector('input[name="id"]').value = item.id;
                form.querySelector('input[name="nome"]').value = item.nome;
                form.querySelector('input[name="email"]').value = item.email;
                form.querySelector('input[name="data_nascimento"]').value = item.data_nascimento || '';
                form.querySelector('input[name="pais"]').value = item.pais || '';
                form.querySelector('select[name="id_pagamento"]').value = item.id_pagamento || 'None';
                
                document.getElementById('modal-usuario-title').textContent = 'Editar Usuário';
                openModal('modal-usuario');
            }
        }
    } catch (err) {
        logToConsole(`Erro ao carregar detalhes: ${err.message}`, 'error');
    }
}

// 9. Delete Operations
async function deleteItem(section, id) {
    const confirmation = confirm(`Deseja realmente remover este registro (#${id})? Esta ação não pode ser desfeita.`);
    if (!confirmation) return;
    
    try {
        const response = await fetch(`/api/${section}/${id}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Erro ao deletar registro.');
        }
        
        if (result.sql) {
            logToConsole(result.sql);
        }
        
        logToConsole(`[SISTEMA] Registro #${id} em ${section} removido com sucesso.`, 'system');
        loadSection(currentSection);
        refreshDropdownCaches();
    } catch (err) {
        logToConsole(err.message, 'error');
        alert(err.message);
    }
}

// 10. Play Simulation (Triggers & View Demonstration)
async function playMusic(id) {
    try {
        const response = await fetch(`/api/musicas/${id}/reproduzir`, {
            method: 'POST'
        });
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Erro ao simular reprodução.');
        }
        
        // Log SQL queries generated
        if (result.sql) {
            logToConsole(result.sql);
            logToConsole("  ↳ GATILHO DISPARADO: UPDATE Musica SET reproducoes = reproducoes + 1 WHERE id = :id_musica;", "query");
        }
        
        // Update reproducing count on UI without full reload for instant feedback
        const countCell = document.getElementById(`repro-count-${id}`);
        if (countCell) {
            countCell.textContent = formatNumber(result.data.reproducoes);
        }
        
        // Add a micro-toast notification
        showPlayToast(result.data.titulo);
        
    } catch (err) {
        logToConsole(err.message, 'error');
    }
}

function showPlayToast(songTitle) {
    const toast = document.createElement('div');
    toast.style.position = 'fixed';
    toast.style.bottom = '200px';
    toast.style.right = '40px';
    toast.style.backgroundColor = 'var(--spotify-green)';
    toast.style.color = 'var(--bg-sidebar)';
    toast.style.padding = '12px 24px';
    toast.style.borderRadius = '24px';
    toast.style.fontWeight = 'bold';
    toast.style.fontSize = '14px';
    toast.style.zIndex = '9999';
    toast.style.boxShadow = 'var(--shadow-lg)';
    toast.style.pointerEvents = 'none';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s cubic-bezier(0.3, 0, 0, 1)';
    
    toast.innerHTML = `<i class="fa-solid fa-play" style="margin-right: 8px;"></i> Reproduzindo: ${songTitle}`;
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.style.opacity = '1';
        toast.style.transform = 'translateY(0)';
    }, 50);
    
    // Animate out
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px)';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 2500);
}

// 11. Helper formatting utilities
function formatDuration(sec) {
    const m = Math.floor(sec / 60);
    const s = String(sec % 60).padStart(2, '0');
    return `${m}:${s}`;
}

function formatNumber(num) {
    if (num === null || num === undefined) return '0';
    if (num >= 1e9) {
        return (num / 1e9).toFixed(1).replace('.0', '') + 'B';
    }
    if (num >= 1e6) {
        return (num / 1e6).toFixed(1).replace('.0', '') + 'M';
    }
    if (num >= 1e3) {
        return (num / 1e3).toFixed(1).replace('.0', '') + 'K';
    }
    return num.toLocaleString('pt-BR');
}

function truncateText(text, length) {
    if (!text) return '';
    return text.length > length ? text.substring(0, length) + '...' : text;
}
