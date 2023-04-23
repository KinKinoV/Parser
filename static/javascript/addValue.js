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
    location.assign(new URL(`${location.href.slice(0,-23)}/tag_definition/${context['mp_amm']}/${context['pp_amm']}/${context['tp_amm']}/${context['ftp_amm']}`));
};