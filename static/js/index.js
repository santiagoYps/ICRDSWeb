const tabs = document.getElementById('tabs')
const tables = document.querySelector('.table-container').children;

const handleTabsClick = (e) => {
  device = e.target.parentElement.dataset.device;

  console.log( e.target.parentElement);
  for (t of tables){
    if (t.dataset.tab === device)
      t.classList.remove('is-hidden');
    else
      t.classList.add('is-hidden');
  }
  for (tab of tabs.children){
    if (tab.dataset.device === device)
      tab.classList.add('is-active')
    else
      tab.classList.remove('is-active')
  }
  
}

tabs.addEventListener('click', handleTabsClick, true);
