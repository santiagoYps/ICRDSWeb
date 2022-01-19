const graphSelectContainer = document.getElementById('graph-select');
const variableSelectContainer = document.getElementById('variable-select');
const graphBtn = document.getElementById('graph-btn');
const graphMsgs = {
    'pie': 'El diagrama de pastel mostrará solo la clasificación de eventos (near-crash/Sin evento)',
    'scatter': 'El diagrama de dispersión se mostrará todas las variables'
}
const graphsWithVariables = ['lineal', 'histogram']


graphSelectContainer.addEventListener('change', handleGraphSelection, false);
graphBtn.addEventListener('click', updateGraphics, false);

graphSelectContainer.querySelector('select').selectedIndex = 0;
variableSelectContainer.querySelector('select').selectedIndex = 0;

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