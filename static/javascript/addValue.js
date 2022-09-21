// Used for current page's form data fields
window.onload = function() {
    if (sessionStorage.getItem('data')){
        let a = JSON.parse(sessionStorage.getItem('data'));
        var form = document.forms['form'];
        for (var key of Object.keys(a))
        {
            if(form.elements[`${key}`].matches('[type="checkbox"]') && a[`${key}`])
            {
                form.elements[`${key}`].checked = true;
            }
            form.elements[`${key}`].value = `${a[`${key}`]}`;
        }
        
        sessionStorage.clear();
    }    
};

// Needed to save current form data and pass it to new page's form
window.onbeforeunload = function() {
    var form = document.querySelector('#form');
    var dataL = new FormData(form);
    var strData = "{";
    for(var [key, value] of dataL )
    {
        if ( key && value && value.length !== 0 ) strData += `"${key}" : "${value}",`;
    }
    strData = strData.slice(0,-1);
    
    if (strData) strData += "}";

    sessionStorage.setItem('data', strData);
};

// Function to add new input fields through URL modification
function addInput(tagPos, context) 
{
    switch(tagPos){
        case 1:
            // Message parameter ammount
            context['mp_amm'] += 1;
            break;
        case 2:
            // Pagination parameter ammount
            context['pp_amm'] += 1;
            break;
        case 3:
            // Thread post parameter ammount
            context['tp_amm'] += 1;
            break;
        case 4:
            // Forum thread parameter ammount
            context['ftp_amm'] += 1;
            break;
    };

    // Modifying current URL and reloading page
    location.assign(new URL(`http://localhost:5000/tag_definition/${context['mp_amm']}/${context['pp_amm']}/${context['tp_amm']}/${context['ftp_amm']}`));
};