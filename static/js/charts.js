const graphSelectContainer = document.getElementById('graph-select');
const variableSelectContainer = document.getElementById('variable-select');
const graphBtn = document.getElementById('graph-btn');
const checkNearCrashBtn = document.getElementById('check-near-crash-btn');
const loadingMsg = document.getElementById('analysis-loading'); //is-hidden
const analysisModal = document.getElementById('modal-analysis'); //is-active
const analysisResult = document.getElementById('analysis-result');
const analysisFailedMsg = document.getElementById('analysis-failed-msg')

const graphMsgs = {
    'pie': 'El diagrama de pastel mostrará solo la clasificación de eventos (near-crash/Sin evento)',
    'scatter': 'El diagrama de dispersión se mostrará todas las variables'
}
const graphsWithVariables = ['lineal', 'histogram']
const changeModalInformation = {
    "none": function () {
        loadingMsg.classList.add('is-hidden');
        analysisResult.classList.add('is-hidden');
        analysisFailedMsg.classList.add('is-hidden');
    },
    "loading": function () {
        loadingMsg.classList.remove('is-hidden');
        analysisResult.classList.add('is-hidden');
        analysisFailedMsg.classList.add('is-hidden');
    },
    "done": function () {
        loadingMsg.classList.add('is-hidden');
        analysisResult.classList.remove('is-hidden');
        analysisFailedMsg.classList.add('is-hidden');
    },
    "error": function () {
        loadingMsg.classList.add('is-hidden');
        analysisResult.classList.add('is-hidden');
        analysisFailedMsg.classList.remove('is-hidden');
    }
}
changeModalInformation['none']();
let analysisDownloaded = false;

graphSelectContainer.addEventListener('change', handleGraphSelection, false);
graphBtn.addEventListener('click', updateGraphics, false);

graphSelectContainer.querySelector('select').selectedIndex = 0;
variableSelectContainer.querySelector('select').selectedIndex = 0;

checkNearCrashBtn.addEventListener('click', checkNearCrashRequest);
addModalListeners();

function handleGraphSelection(e) {
    const graph = e.target.value;
    if (graph === 'pie' || graph === 'scatter')
        showVariableSelection(false, graph);
    else
        showVariableSelection(true);
    
}

function showVariableSelection(show, graph){
    if (show){
        variableSelectContainer.classList.remove('is-hidden');
        const msg = variableSelectContainer.nextElementSibling;
        msg.classList.add('is-hidden');
        msg.textContent = '';
    }
    else{
        variableSelectContainer.classList.add('is-hidden');
        const msg = variableSelectContainer.nextElementSibling;
        msg.classList.remove('is-hidden');
        msg.textContent = graphMsgs[graph];
    }
}

async function updateGraphics(e) {
    e.preventDefault();
    let graphicSelect = graphSelectContainer.querySelector('select');
    let variableSelect = variableSelectContainer.querySelector('select');
    
    let variable = ( graphsWithVariables.includes(graphicSelect.value) )
        ? variableSelect.value
        : 'none';
    
    let isCorrect = validateOptions(graphicSelect, variableSelect, variable);
    console.log(isCorrect);
    if (isCorrect) {
        document.getElementById('error-msg').classList.add('is-hidden');
        document.querySelector('.loading-chart').classList.remove('is-hidden');
        document.getElementById('chart').classList.add('is-invisible');

        const tripId = document.getElementById('trip-info').dataset.tripId;
        let requestData = {
            "graph": graphicSelect.value,
            "variable": variable
        }
        console.log(requestData);
        const response = await fetch('/trips/details/'+tripId, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        const graphJSON = await response.json();
        console.log(graphJSON);

        graphic(graphJSON);
        document.querySelector('.loading-chart').classList.add('is-hidden');
        document.getElementById('chart').classList.remove('is-invisible');
        // hide loading
    }
    else
        document.getElementById('error-msg').classList.remove('is-hidden');
}

function graphic(graphJSON){
    var graphs = graphJSON;
    var config = { responsive: true };
    Plotly.newPlot('chart', graphs, config, {});
}

function validateOptions(graphicSelect, variableSelect, variable) {
    //Si no se debe seleccionar variable y hay un grafico seleccionado
    if (variable === 'none' && graphicSelect.selectedIndex !== 0)
        return true;
    //Si se debe seleccionar variable y hay tanto grafico como variable seleccionada.
    else if (variable !== 'none' && graphicSelect.selectedIndex !== 0 && variableSelect.selectedIndex !== 0)
        return true;
    else
        return false;
}

async function checkNearCrashRequest(e) {
    const tripId = document.getElementById('trip-info').dataset.tripId;
    console.log('checking near crash for trip: '+ tripId);
    
    showModalAnalysis(true);
    //showLoadingAnalysis(true);
    if (!analysisDownloaded) {
        let analyzed = document.getElementById('trip-info').dataset.analyzed.toLowerCase()
        let endPoint = (analyzed === "false") ? "/checkNearCrash" : "/loadNearCrash";

        changeModalInformation['loading']();
        const response = await fetch(endPoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({"tripId": tripId})
        });
        const data = await response.json();
        console.log(data);

        parseAnalysisResults(data);
        //showLoadingAnalysis(false);
    }
    
}

function parseAnalysisResults(data) {
    if (data.code === 200){
        analysisResult.querySelector('#near-crash-amount').textContent = Object.keys(data.nearCrashData).length;
        let tBody = analysisResult.querySelector("tbody");
        let template = analysisResult.querySelector('#near-crash-template');
    
        for (nearCrashKey in data.nearCrashData){
            const nearCrash = data.nearCrashData[nearCrashKey]        
            let th = template.content.querySelector("th");
            th.textContent = nearCrashKey;
    
            let td = template.content.querySelectorAll("td");
            td[0].textContent = nearCrash.timestamp_start.split('.')[0];
            td[1].textContent = nearCrash.latitude;
            td[2].textContent = nearCrash.longitude;
    
            const clone = document.importNode(template.content, true);
            tBody.appendChild(clone)
        }
        //analysisResult.classList.remove('is-hidden');
        changeModalInformation['done']();
        analysisDownloaded = true;
        document.getElementById('trip-info').dataset.analyzed = "true"
    }
    else{
        //analysisFailedMsg.classList.remove('is-hidden')
        changeModalInformation['error']();
    }
}

function showModalAnalysis(show){
    if (show){
        analysisModal.classList.add('is-active');
    }
    else {
        analysisModal.classList.remove('is-active');
    }
}

function showLoadingAnalysis(isLoading) {
    if (isLoading){
        loadingMsg.classList.remove('is-hidden');
        analysisFailedMsg.classList.add('is-hidden')
    }
    else{
        loadingMsg.classList.add('is-hidden');
    }
    
}

function addModalListeners() {
    const closeElements = ['.modal-background', 'button[data-ok]', '.modal-close']
    for (element of closeElements) {
        analysisModal.querySelector(element).addEventListener('click', (e) => {
            e.preventDefault();
            showModalAnalysis(false);
        });
    }
}