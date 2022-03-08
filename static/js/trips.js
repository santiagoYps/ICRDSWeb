const tabs = document.querySelectorAll('#tabs li')
const tables = document.querySelectorAll('.table-container table');
const removeBtns = document.querySelectorAll('.icon.icon-delete');
const detailsBtns = document.querySelectorAll('.icon.icon-details');
const modal = document.getElementById('modal-confirmation');
const initialDate = document.getElementById('initial-date');
const finalDate = document.getElementById('final-date');
const selectVehicle = document.getElementById('vehicle-filter');
const selectRoute = document.getElementById('route-filter');
const clearDateFilterBtn = document.getElementById('clear-date-filter');
const clearVehicleFilterBtn = document.getElementById('clear-vehicle-filter');
const clearRouteFilterBtn = document.getElementById('clear-route-filter');

let tripToRemove = "";
let row = -1;
let device = "smartphone";
let filters = {
  'date': {
    'condition': ['', ''],
    'active': false,
    'filter': function(dateTrip) {
      if ( !(dateTrip >= this.condition[0] && dateTrip <= this.condition[1]))
        return false;
      else
        return true;
    }
  },
  'vehicle': {
    'condition': '',
    'active': false,
    'filter': function (vehicle) {
      if (vehicle === this.condition)
        return true;
      else 
        return false;
    }
  },
  'route': {
    'condition': '',
    'active': false,
    'filter': function (route) {
      if (route === this.condition)
        return true;
      else 
        return false;
    }
  }
}

removeBtns.forEach(btn => {
  btn.addEventListener('click', (e) => {
    tripToRemove = e.target.dataset.item;
    showConfirmationModal(true);
  })
});

addModalListeners();

tabs.forEach(tab => {
  tab.addEventListener('click', handleTabsClick);
});

initialDate.addEventListener('change', (e) => {
  updateDateCondition();
  filterTrips();
}, false);

finalDate.addEventListener('change', (e) => {
  updateDateCondition();
  filterTrips();
}, false);

selectVehicle.addEventListener('change', (e) => {
  updateVehicleCondition();
  filterTrips();
}, false);
selectRoute.addEventListener('change', (e) => {
  updateRouteCondition();
  filterTrips();
}, false);

clearDateFilterBtn.addEventListener('click', (e) => {
  initialDate.value = "";
  finalDate.value = "";
  updateDateCondition();
  filterTrips();
}, false);

clearVehicleFilterBtn.addEventListener('click', (e) => {
  selectVehicle.selectedIndex = 0;
  updateVehicleCondition();
  filterTrips();
}, false);

clearRouteFilterBtn.addEventListener('click', (e) => {
  selectRoute.selectedIndex = 0;
  updateRouteCondition();
  filterTrips();
}, false);

function handleTabsClick(e) {  
  device = e.target.parentElement.dataset.device;
  console.log(device);

  tables.forEach( t => {
    if (t.dataset.tab === device)
      t.classList.remove('is-hidden');
    else
      t.classList.add('is-hidden');
  });
  tabs.forEach(tab => {
    if (tab.dataset.device === device)
      tab.classList.add('is-active')
    else
      tab.classList.remove('is-active')
  });
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
    notification.firstChild.textContent = 'OcurriÃ³ un error al borrar el trayecto';
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

function updateDateCondition(){
  if (initialDate.value !== "" || finalDate.value !== ""){
    const initialDateValue = initialDate.value !== "" ? 
      new Date( Date.parse(initialDate.value + "T00:00") )   : new Date(0);
    const finalDateValue = finalDate.value !== "" ? 
      new Date( Date.parse(finalDate.value + "T00:00") )   : new Date();
    filters.date.condition = [initialDateValue, finalDateValue];
    filters.date.active = true;
    clearDateFilterBtn.classList.remove('is-hidden');
  }
  else {
    filters.date.condition = ["", ""];
    filters.date.active = false;
    clearDateFilterBtn.classList.add('is-hidden');
  }
}

function updateVehicleCondition() {
  if (selectVehicle.selectedIndex !== 0) {
    filters.vehicle.condition = selectVehicle.value;
    filters.vehicle.active = true;
    clearVehicleFilterBtn.classList.remove('is-hidden');
  }
  else {
    filters.vehicle.condition = "";
    filters.vehicle.active = false;
    clearVehicleFilterBtn.classList.add('is-hidden');
  }  
}

function updateRouteCondition() {
  if (selectRoute.selectedIndex !== 0) {
    filters.route.condition = selectRoute.value;
    filters.route.active = true;
    clearRouteFilterBtn.classList.remove('is-hidden');
  }
  else {
    filters.route.condition = "";
    filters.route.active = false;
    clearRouteFilterBtn.classList.add('is-hidden');
  }
}

function filterTrips() {
  tables.forEach( table => {
    table.querySelectorAll("tbody tr").forEach( tr => {
      let results = []
      results[0] = (filters.date.active)
        ? filters.date.filter( strToDate( tr.children[0].textContent ) )
        : true;
      
      results[1] = (filters.vehicle.active)
        ? filters.vehicle.filter( tr.children[3].textContent )
        : true;

      results[2] = (filters.route.active)
        ? filters.route.filter( tr.children[4].textContent )
        : true;

      if ( results.includes(false) )
        tr.classList.add('is-hidden');
      else
        tr.classList.remove('is-hidden');
    });
  });
}

function strToDate( dateStr ) {  
  let [day, monthStr, year] = dateStr.split(" ")[0].split("-");
  if (day > 31){
    let e2 = new Error();
    e2.name = "Invalid Date format";
    e2.message = "Please, supply a date string in the format: dd-MMM-YYYY"
    throw e2;
  }
  let date = new Date(Number(year), monthNumber(monthStr), Number(day));
  return date;
}

function monthNumber(monthStr) {
  monthStr = monthStr.toUpperCase();
  const monthNumbers = {
    "JAN": 0, "ENE": 0,
    "FEB": 1,
    "MAR": 2,
    "APR": 3, "ABR": 3,
    "MAY": 4,
    "JUN": 5,
    "JUL": 6,
    "AUG": 7, "AGO": 7,
    "SEP": 8,
    "OCT": 9,
    "NOV": 10,
    "DEC": 11, "DIC": 11
  }
  let num = monthNumbers[monthStr]
  if (num != undefined)
    return num;
  else 
    return -1;  
}