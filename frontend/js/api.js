const BASE_URL = ''


// 获取某页的数据
async function getDataByNumber (pageNumber){
    try{
        const params = new URLSearchParams({
            pageNumber : pageNumber,
        });

        let data = await fetch(`${BASE_URL}/user/eqequipments?${params.toString()}`,{
        method : 'GET',
        headers : {
            'content-type' : 'application/json'
        },
        credentials : 'include'
        });
        return await data.json();
    }catch(error){
        console.log(`${pageNumber}请求数据失败`)
        throw error;
    }
    
}
