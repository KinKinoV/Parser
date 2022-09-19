function addInput(tagPos, context) 
{
    switch(tagPos){
        case 1:
            context['mp_amm'] += 1;
            break;
        case 2:
            context['pp_amm'] += 1;
            break;
        case 3:
            context['tp_amm'] += 1;
            break;
        case 4:
            context['ftp_amm'] += 1;
            break;
    }
    window.location.href = new URL(`http://localhost:5000/tag_definition/${context['mp_amm']}/${context['pp_amm']}/${context['tp_amm']}/${context['ftp_amm']}`);
};