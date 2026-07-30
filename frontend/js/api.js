const BASE_URL = 'https://frp-put.com:58235'


// 跳转
/**
 * 
 * @param {string} identity 
 * @param {string} location
 */
function goTo(identity , location){
    window.location.href = `${BASE_URL}/${identity}/${location}`
}

// 获取某页的数据
/**`
 * @param {QueryData} QueryData
 * @returns {}
 */
async function getData (QueryData = {}){
    try{
        const params = new URLSearchParams();


        // 为查询的参数列表清除空项
        for(const[k,v] of Object.entries(QueryData)){
            if(v !== null && v !== '' && v !== undefined){
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

// 注册
/**
 * 
 * @param {string} username 
 * @param {string} password 
 * @param {string} identity 
 * @returns {boolean}
 */
async function sendRegister(username , password, identity){

    try{
        const response = await fetch(`${BASE_URL}/${identity}/register`,{
            method : "POST",
            headers : {
                'Content-Type' : 'application/json',
                'token' : sessionStorage.getItem(`token`)
            },
            body : JSON.stringify({
                'username': username,
                'password' : password 
            })
        })

        const res = await response.json()

        if(!response.ok || res.code !== 0){
            if(res.code !== 0){
                alert(`注册失败，${res.message}`)
            }
            console.log(`注册失败,错误码:${response.status},code ${res.code}`)
            return false
        }

        return true

    }catch(error){
        console.error("注册错误")
        return false
    }
}

// 登录
/**
 * 
 * @param {string} username 
 * @param {string} password 
 * @param {string} identity 
 * @returns {boolean}
 */
async function sendSubmit(username , password ,identity){
    try{
        const response = await fetch(`${BASE_URL}/${identity}/login`,{
            method : 'POST',
            headers : {
                'Content-Type' : 'application/json'

            },
            body : JSON.stringify({
                'username' : username,
                'password' : password
            })
        })

        const res = await response.json()

        if(response.ok !== true || res.code !== 0){
            if(res.code !== 0){
                alert(`登录失败，${res.message}`)
            }
            console.log(`注册失败,错误码:${response.status},code ${res.code}`)
            return false
        }
        
        sessionStorage.setItem('token',res.data.token)
        
        return true
    }catch(error){
        console.error('登录错误')
        return false
    }
}

// 查询个人信息或者鉴权
/**
 * 
 * @param {string} identity
 * @returns {GetMeOut} 
 */
async function getPersonalData(identity){
    try{
        const response = await fetch(`${BASE_URL}/${identity}/me`,{
            method : 'GET',
            headers : {
                'Content-Type' : 'application/json',
                'token' : sessionStorage.getItem('token')
            }
        })

        const res = await response.json();


        if(response.ok !== true || res.code !== 0){
            if(res.code !== 0){
                alert(`查询个人信息或者鉴权失败，${res.message}`)
            }
            console.log(`查询个人信息或者鉴权失败,错误码:${response.status},code ${res.code}`)
            return false
        }

        return res.data
    }catch{
        console.error(`查询个人信息或者鉴权失败`)
        return false
    }
}


// 修改个人信息
/**
 * 
 * @param {UpdateInDTO} UpdateInDTO 
 * @param {string} identity 
 * @returns {boolean}
 */
async function changePersonalData(UpdateInDTO,identity){
    try{
        const response = await fetch(`${BASE_URL}/${identity}/update`,{
            method : 'PUT',
            headers : {
                'Content-Type' : 'application/json',
                'token' : sessionStorage.getItem('token')
            },
            body : JSON.stringify({
                UpdateInDTO
            }) 
        })

        const res = await response.json();

        if(response.ok !== true || res.code !== 0){
            if(res.code !== 0){
                alert(`修改个人信息失败，${res.message}`)
            }
            console.log(`修改个人信息失败,错误码:${response.status},code ${res.code}`)
            return false
        }
        
    }catch{
        console.error(`修改个人信息失败`)
        return false
    }
}
