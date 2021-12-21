const dropdownChartBtn = document.getElementById("dropdown-chart-btn");
const dropdownVariableBtn = document.getElementById("dropdown-variable-btn");

function showDropdownItems(event){
    const div = document.querySelector(`div[data-btn="${event.target.id}"]`)
    div.classList.toggle("is-active")
}


dropdownChartBtn.addEventListener('click', showDropdownItems, false);
dropdownVariableBtn.addEventListener('click', showDropdownItems, false);