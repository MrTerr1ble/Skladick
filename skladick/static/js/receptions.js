// Tabs
const tabs = document.querySelectorAll('.tab');
const viewList = document.getElementById('view-list');
const viewCreate = document.getElementById('view-create');
tabs.forEach(t => t.addEventListener('click', () => {
  tabs.forEach(x => x.classList.remove('active'));
  t.classList.add('active');
  const id = t.dataset.tab;
  const toList = id === 'list';
  viewList.hidden = !toList;
  viewCreate.hidden = toList;
}));
document.getElementById('btnCreateFromList')?.addEventListener('click', () => {
  document.querySelector('.tab[data-tab="create"]').click();
  document.getElementById('supplier')?.focus();
});

// Status dropdown
document.querySelectorAll('.status').forEach(st => {
  const menu = st.querySelector('.menu');
  st.addEventListener('click', (e) => {
    e.stopPropagation();
    menu.classList.toggle('open');
    st.setAttribute('aria-expanded', menu.classList.contains('open'));
  });
  menu.querySelectorAll('button').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const label = st.querySelector('.label-status');
      label.textContent = btn.dataset.status;
      const dot = st.querySelector('.dot');
      if(btn.classList.contains('ok')) { dot.style.background = getComputedStyle(document.documentElement).getPropertyValue('--success'); }
      if(btn.classList.contains('bad')){ dot.style.background = getComputedStyle(document.documentElement).getPropertyValue('--danger'); }
      menu.classList.remove('open');
    });
  });
});
document.addEventListener('click', () => {
  document.querySelectorAll('.menu.open').forEach(m => m.classList.remove('open'));
});

// Demo role switch (можно убрать)
const roleText = document.getElementById('roleText');
const roleBadge = document.getElementById('roleBadge');
if (roleBadge && roleText){
  roleBadge.title = "Клик — переключить роль";
  roleBadge.style.cursor = "pointer";
  roleBadge.addEventListener('click', () => {
    roleText.textContent = roleText.textContent === 'Кладовщик' ? 'Руководитель смены' : 'Кладовщик';
  });
}

// Buttons demo
document.getElementById('btnCancel')?.addEventListener('click', () => {
  document.querySelector('.tab[data-tab="list"]').click();
});
document.getElementById('btnSave')?.addEventListener('click', () => alert('Черновик приёмки сохранён'));
document.getElementById('btnAct')?.addEventListener('click', () => alert('Акт приёмки сформирован'));
