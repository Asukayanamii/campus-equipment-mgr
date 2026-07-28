const BASE_URL = 'http://127.0.0.1:4523/m1/8634384-8414797-default'
let pageNow = 1;




// 获取某页的数据
async function getData (QueryData = {}){
    try{
        const params = new URLSearchParams();


        // 为查询的参数列表清除空项
        for(const[k,v] of Object.entries(QueryData)){
            if(v !==null && v !== '' && v!=undefined){
                params.set(k,v);
            }
        }

        let data = await fetch(`${BASE_URL}/user/equipment/page?${params.toString()}`,{
        method : 'GET',
        headers : {
            'content-type' : 'application/json',
            'token' : sessionStorage.getItem(`token`)
        },
        });
        return await data.json();
    }catch(error){
        console.error(`请求数据失败`,error)
        throw error;
    }
    
}

