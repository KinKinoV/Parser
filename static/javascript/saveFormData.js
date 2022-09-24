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
