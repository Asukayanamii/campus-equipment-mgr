const BASE_URL = ''
let totalNumbers = 0; 
function getData(){
    fetch(`${BASE_URL}/user/eqequipments`,{
    method : 'GET',
    headers : {

    },
    credentials : 'include'
})
}
