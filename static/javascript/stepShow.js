const paginationCase = document.getElementById('paginationCase');

const step = document.getElementById('step');
const expl = document.getElementById('paginationExplanation');

paginationCase.addEventListener('change', function handleChange(event) {
    if (event.target.value === 'C') {
        step.style.visibility = 'visible';
        expl.style.visibility = 'visible';
    } else {
        step.style.visibility = 'hidden';
        expl.style.visibility = 'hidden';
    }
});
