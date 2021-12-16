const tabs = document.getElementById('tabs')
const tables = document.querySelector('.table-container').children;
const removeBtns = document.querySelectorAll('.icon.icon-delete');
const detailsBtns = document.querySelectorAll('.icon.icon-details');
const modal = document.getElementById('modal-confirmation');
let tripToRemove = "";
let row = -1;
let device = "smartphone";

removeBtns.forEach(btn => {
  btn.addEventListener('click', (e) => {
    tripToRemove = e.target.dataset.item;
    showConfirmationModal(true);
  })
});
addModalListeners();
tabs.addEventListener('click', handleTabsClick);


function handleTabsClick(e) {
  device = e.target.parentElement.dataset.device;
  console.log(device)
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


async function removeTrip() {
  console.log('Removing '+ tripToRemove);
  
  modal.querySelector('button[data-delete]').classList.add('is-loading')
  bodyRequest = {
    idTrip: tripToRemove,
    device: device
  }

  const response = await fetch('/removeTrip', {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(bodyRequest)
  });
  const data = await response.json();

  modal.querySelector('button[data-delete]').classList.remove('is-loading')
  showConfirmationModal(false);
  showNotification(data.result);
  if (data.result == 'success')
    updateTable()
}


function showConfirmationModal(show){
  if (show){
    modal.classList.add('is-active');
  }
  else {
    modal.classList.remove('is-active');
  }
}

function showNotification(result) {
  let notification = document.getElementById('notification');
  notification.classList.remove('is-hidden');

  if (result === 'success'){
    notification.classList.add('is-primary');
    notification.classList.remove('is-danger');
    notification.firstChild.textContent = 'El trayecto y sus datos han sido borrados correctamente';
  }
  else {
    notification.classList.add('is-danger');
    notification.classList.remove('is-primary');
    notification.firstChild.textContent = 'Ocurrió un error al borrar el trayecto';
  }

  notification.querySelector('.delete').addEventListener('click', (e)=>{
    notification.classList.add('is-hidden');
  });
  setTimeout(() => {
    notification.classList.add('is-hidden');
    notification.querySelector('.delete').addEventListener('click', null);
  }, 10000);
}

function updateTable() {
  let row = document.getElementById(tripToRemove);
  row.parentElement.removeChild(row);
  tripToRemove = "";
}

function addModalListeners(){
  const closeElements = ['.modal-background', 'button[data-cancel]', '.modal-close']
  for (element of closeElements) {
    modal.querySelector(element).addEventListener('click', (e) => {
      e.preventDefault();
      showConfirmationModal(false);
    });
  }
  modal.querySelector('button[data-delete]').addEventListener('click', removeTrip)
}