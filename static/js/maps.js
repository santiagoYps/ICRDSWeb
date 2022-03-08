const sidebar = document.querySelector("aside");
const closeSidebar = document.querySelector(".sidebar-close-btn");
const burguerMenu = document.querySelector(".burguer-menu");

const deviceSelect = document.getElementById("device-filter");
const routeSelect = document.getElementById("route-filter");
const mapButtons = document.getElementById("map-buttons");
const btnLoadMap = document.getElementById("load-map")
const loading = document.getElementById("map-loading")
const mapMsg = document.getElementById("map-msg");

let isFirstMap = true;

burguerMenu.addEventListener('click', () => {
    sidebar.classList.remove("is-hidden");
});

closeSidebar.addEventListener('click', () => {
    sidebar.classList.add("is-hidden");
});

btnLoadMap.addEventListener('click', () => loadMap(mapButtons.children['heat-map']) );

for (btn of mapButtons.children) {
    btn.addEventListener('click', (e) => loadMap(e.target) );
}

async function loadMap (mapBtn) {
    if (validateOptions()){
        console.log('bien');
        const mapType = updateSelectedMap(mapBtn)
        showLoadingMsg(true);
        disableButtons(true);
        const data = await makeRequest(mapType, deviceSelect.value, routeSelect.value)
        console.log(data);
        showLoadingMsg(false);
        disableButtons(false);
        mapButtons.classList.remove("is-hidden");
        if (isFirstMap){
            btnLoadMap.textContent = "Actualizar Mapa"
            isFirstMap = false;
        }
    }
    else {
        console.log('mal');
    }
}

function updateSelectedMap (selectedMapBtn){
    selectedMap = "";
    for (btn of mapButtons.children) {
        if (btn === selectedMapBtn){
            btn.classList.add('is-info');
            selectedMap = btn.id;
        }
        else {
            btn.classList.remove('is-info');
        }
    };
    return selectedMap;
}

async function makeRequest(map, device, route) {
    const requestData = {
        "mapType": map,
        "device": device,
        "route": route,
    }
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            resolve(requestData)
        }, 3000);
    })

    // const response = await fetch('/endpoint', {
    //     method: 'POST',
    //     headers: {
    //       'Content-Type': 'application/json'
    //     },
    //     body: JSON.stringify(requestData)
    // });
    // return response.json(); 
}

function showLoadingMsg(isLoading) {
    if (isLoading){
        loading.classList.remove("is-hidden");
        mapMsg.classList.remove("is-hidden");
        mapMsg.textContent = "Cargando el mapa ..."
    }
    else {
        loading.classList.add("is-hidden");
        mapMsg.classList.add("is-hidden");
    }
}

function disableButtons(value) {
    routeSelect.disabled = value;
    deviceSelect.disabled = value;
    deviceSelect.disabled = value;
    btnLoadMap.disabled = value;
    for (btn of mapButtons.children) {
        btn.disabled = value;
    }

}

function validateOptions() {
    if (deviceSelect.selectedIndex !== 0 && routeSelect.selectedIndex !== 0)
        return true;
    else 
        return false;
}