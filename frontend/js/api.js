const BASE_URL = `https://frp-put.com:58235`


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
 * @returns {Result_Page_EquipmentOut}
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

        const data = await fetch(`${BASE_URL}/${apiChoose()}/equipment/page?${params.toString()}`,{
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

// 获取某页分类数据
/**`
 * @param {QueryData} QueryData
 * @returns {Result_Page_CategoryResp}
 */
async function getCategoryData (QueryData = {}){
    try{
        const params = new URLSearchParams();

        // 为查询的参数列表清除空项
        for(const[k,v] of Object.entries(QueryData)){
            if(v !== null && v !== '' && v !== undefined){
                params.set(k,v);
            }
        }

        const data = await fetch(`${BASE_URL}/${apiChoose()}/equipment-category/page?${params.toString()}`,{
            method : 'GET',
            headers : {
                'content-type' : 'application/json',
                'token' : sessionStorage.getItem(`token`)
            },
        });

        return await data.json();
    }catch(error){
        console.error(`请求分类数据失败`,error)
        throw error;
    }

}

// 管理端新增设备分类
/**
 *
 * @param {CategoryCreate} CategoryCreate
 * @returns {boolean}
 */
async function addNewCategory(CategoryCreate){
    try {
        const response = await fetch(`${BASE_URL}/admin/equipment-category/`,{
            method : 'POST',
            headers : {
                'Content-Type' : 'application/json',
                'token' : sessionStorage.getItem('token')
            },
            body : JSON.stringify(
                CategoryCreate
            )
        })

        const res = await response.json();

        if(response.ok !== true || res.code !== 0){
            if(res.code !== 0){
                Toast.failure(`新增分类失败，${res.message}`)
            }
            console.log(`新增分类失败,错误码:${response.status},code ${res.code}`)
            return false
        }

        return true
    } catch (error) {
        console.error('新增分类失败')
        return false
    }
}

// 根据id获取数据
/**
 * 
 * @param {number} equipmentId 
 * @param {String} identity
 * @returns {EquipmentOut}
 */
async function getDataById(equipmentId,identity){
    try {
        const response = await fetch(`${BASE_URL}/${identity}/equipment/${equipmentId}`,{
            method : 'GET',
            headers : {
                'Content-Type' : 'application/json',
                'token' : sessionStorage.getItem(`token`)
            }
        })

        const res = await response.json()

        if(!response.ok || res.code !== 0){
            if(res.code !== 0){
                Toast.failure(`根据id获取数据失败，${res.message}`)
            }
            console.log(`根据id获取数据失败,错误码:${response.status},code ${res.code}`)
            return false
        }

        return res.data
    } catch (error) {
        console.error('根据id获取数据失败')
        return false
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
async function sendRegister(username , password, identity, registrationCode = ''){

    try{
        const response = await fetch(`${BASE_URL}/${identity}/register`,{
            method : "POST",
            headers : {
                'Content-Type' : 'application/json',
                'token' : sessionStorage.getItem(`token`)
            },
            body : JSON.stringify({
                'username': username,
                'password' : password,
                ...(identity === 'admin' ? {'registration_code': registrationCode} : {})
            })
        })

        const res = await response.json()

        if(!response.ok || res.code !== 0){
            if(res.code !== 0){
                Toast.failure(`注册失败，${res.message}`)
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
    prepareRoleLogin(identity)
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
                Toast.failure(`登录失败，${res.message}`)
            }
            console.log(`登录失败,错误码:${response.status},code ${res.code}`)
            return false
        }
        
        saveAuthSession(identity, res.data)
        
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
                Toast.failure(`查询个人信息或者鉴权失败，${res.message}`)
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
            body : JSON.stringify(
                UpdateInDTO
            ) 
        })

        const res = await response.json();

        if(response.ok !== true || res.code !== 0){
            if(res.code !== 0){
                Toast.failure(`修改个人信息失败，${res.message}`)
            }
            console.log(`修改个人信息失败,错误码:${response.status},code ${res.code}`)
            return false
        }

        return true
    }catch{
        console.error(`修改个人信息失败`)
        return false
    }
}

// 管理端新增设备
/**
 * 
 * @param {EquipmentCreate} EquipmentCreate 
 * @param {String} identity 
 * @returns {boolean}
 */
async function addNewEquipment(EquipmentCreate,identity){
    if(identity !== 'admin'){
        Toast.warning('你无权新增设备！')
        return false
    }
    try {
        const response = await fetch(`${BASE_URL}/admin/equipment/`,{
            method : 'POST',
            headers :{
                'Content-Type' : 'application/json',
                'token' : sessionStorage.getItem('token')
            },
            body : JSON.stringify(
                EquipmentCreate
            )
        })

        const res = await response.json();

        if(response.ok !== true || res.code !== 0){
            if(res.code !== 0){
                Toast.failure(`新增设备失败，${res.message}`)
            }
            console.log(`新增设备失败,错误码:${response.status},code ${res.code}`)
            return false
        }

        return true

    } catch (error) {
        console.error('新增设备失败')
        return false
    }
}

// 管理端根据id更新设备
/**
 * 
 * @param {EquipmentUpdate} EquipmentUpdate 
 * @param {String} identity
 * 
 */
async function updateEquipment(equipmentId,EquipmentUpdate,identity){
    if(identity !== 'admin'){
        Toast.warning('你无权更新！')
        return false
    }
    try {
        const response = await fetch(`${BASE_URL}/${identity}/equipment/${equipmentId}`,{
            method : 'PUT',
            headers : {
                'Content-Type' : 'application/json',
                'token' : sessionStorage.getItem('token')
            },
            body : JSON.stringify(EquipmentUpdate)
        })

        const res = await response.json();

        if(response.ok !== true || res.code !== 0){
            if(res.code !== 0){
                Toast.failure(`根据id更新设备失败，${res.message}`)
            }
            console.log(`根据id更新设备失败,错误码:${response.status},code ${res.code}`)
            return false
        }
        
        
        return true
    } catch (error) {
        console.error('根据id更新设备失败')
        return false
    }
}

// 管理端根据id删除设备
/**
 *
 * @param {number} equipmentId
 * @param {String} identity
 * @returns {boolean}
 */
async function deleteEquipment(equipmentId,identity){
    if(identity !== 'admin'){
        Toast.warning('你无权删除')
        return
    }
    try {
        const response  = await fetch(`${BASE_URL}/${identity}/equipment/${equipmentId}`,{
            method : 'DELETE',
            headers : {
                'Content-Type' : 'application/json',
                'token' : sessionStorage.getItem('token')
            }
        })
        const res = await response.json();

        if(response.ok !== true || res.code !== 0){
            if(res.code !== 0){
                Toast.failure(`根据id删除设备失败，${res.message}`)
            }
            console.log(`根据id删除设备失败,错误码:${response.status},code ${res.code}`)
            return false
        }

        return true
    } catch (error) {
        console.error('根据id删除设备失败')
        return
    }
}

// 获取某页借用记录（学生端本人 / 管理端全部）
/**
 *
 * @param {QueryBorrowRecordData} QueryData
 * @returns {Result_Page_BorrowRecordPageOut__ | Result_Page_AdminBorrowRecordPageOut__}
 */
async function getBorrowRecordData(QueryData = {}){
    try{
        const params = new URLSearchParams();

        // 为查询的参数列表清除空项
        for(const[k,v] of Object.entries(QueryData)){
            if(v !== null && v !== '' && v !== undefined){
                params.set(k,v);
            }
        }

        const data = await fetch(`${BASE_URL}/${apiChoose()}/borrow-records/page?${params.toString()}`,{
            method : 'GET',
            headers : {
                'content-type' : 'application/json',
                'token' : sessionStorage.getItem(`token`)
            },
        });

        return await data.json();
    }catch(error){
        console.error(`请求借用记录数据失败`,error)
        throw error;
    }
}

// 获取某页报修记录（学生端本人）
/**
 *
 * @param {QueryRepairReportData} QueryData
 * @returns {Result_Page_RepairReportPageOut__}
 */
async function getRepairReportData(QueryData = {}){
    try{
        const params = new URLSearchParams();

        // 为查询的参数列表清除空项
        for(const[k,v] of Object.entries(QueryData)){
            if(v !== null && v !== '' && v !== undefined){
                params.set(k,v);
            }
        }

        const data = await fetch(`${BASE_URL}/user/repair-reports/page?${params.toString()}`,{
            method : 'GET',
            headers : {
                'content-type' : 'application/json',
                'token' : sessionStorage.getItem(`token`)
            },
        });

        return await data.json();
    }catch(error){
        console.error(`请求报修记录数据失败`,error)
        throw error;
    }
}

// 根据id获取借用记录详情
/**
 *
 * @param {number} borrowRecordId
 * @returns {BorrowRecordOut | boolean}
 */
async function getBorrowRecordDetail(borrowRecordId){
    try {
        const response = await fetch(`${BASE_URL}/${apiChoose()}/borrow-records/${borrowRecordId}`,{
            method : 'GET',
            headers : {
                'Content-Type' : 'application/json',
                'token' : sessionStorage.getItem(`token`)
            }
        })

        const res = await response.json()

        if(!response.ok || res.code !== 0){
            if(res.code !== 0){
                Toast.failure(`根据id获取借用记录详情失败，${res.message}`)
            }
            console.log(`根据id获取借用记录详情失败,错误码:${response.status},code ${res.code}`)
            return false
        }

        return res.data
    } catch (error) {
        console.error('根据id获取借用记录详情失败')
        return false
    }
}

// 根据id获取报修记录详情（学生端本人）
/**
 *
 * @param {number} repairReportId
 * @returns {RepairReportOut | boolean}
 */
async function getRepairReportDetail(repairReportId){
    try {
        const response = await fetch(`${BASE_URL}/user/repair-reports/${repairReportId}`,{
            method : 'GET',
            headers : {
                'Content-Type' : 'application/json',
                'token' : sessionStorage.getItem(`token`)
            }
        })

        const res = await response.json()

        if(!response.ok || res.code !== 0){
            if(res.code !== 0){
                Toast.failure(`根据id获取报修记录详情失败，${res.message}`)
            }
            console.log(`根据id获取报修记录详情失败,错误码:${response.status},code ${res.code}`)
            return false
        }

        return res.data
    } catch (error) {
        console.error('根据id获取报修记录详情失败')
        return false
    }
}

// 学生提交借用申请。身份由 token 确定，前端只提交设备和借用信息。
async function createBorrowRecord(borrowRecordCreate){
    try {
        const response = await fetch(`${BASE_URL}/user/borrow-records`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'token': sessionStorage.getItem('token')
            },
            body: JSON.stringify(borrowRecordCreate)
        })
        const result = await response.json().catch(() => ({ message: '服务返回的数据格式不正确' }))

        if(!response.ok || result.code !== 0){
            Toast.failure(result.message || '借用申请提交失败')
            return false
        }
        return result.data
    } catch (error) {
        console.error('借用申请提交失败', error)
        Toast.failure('网络异常，请稍后重试')
        return false
    }
}

// 管理端审核借用申请
/**
 *
 * @param {number} borrowRecordId
 * @param {BorrowRecordReview} BorrowRecordReview
 * @param {String} identity
 * @returns {boolean}
 */
async function reviewBorrowRecord(borrowRecordId, BorrowRecordReview, identity){
    if(identity !== 'admin'){
        Toast.warning('你无权审核！')
        return false
    }
    try {
        const response = await fetch(`${BASE_URL}/admin/borrow-records/${borrowRecordId}/review`,{
            method : 'POST',
            headers : {
                'Content-Type' : 'application/json',
                'token' : sessionStorage.getItem('token')
            },
            body : JSON.stringify(
                BorrowRecordReview
            )
        })

        const res = await response.json();

        if(response.ok !== true || res.code !== 0){
            if(res.code !== 0){
                Toast.failure(`审核借用申请失败，${res.message}`)
            }
            console.log(`审核借用申请失败,错误码:${response.status},code ${res.code}`)
            return false
        }

        return true
    } catch (error) {
        console.error('审核借用申请失败')
        return false
    }
}

// 管理端确认设备归还
/**
 *
 * @param {number} borrowRecordId
 * @param {BorrowReturnConfirm} BorrowReturnConfirm
 * @param {String} identity
 * @returns {boolean}
 */
async function confirmReturnBorrowRecord(borrowRecordId, BorrowReturnConfirm, identity){
    if(identity !== 'admin'){
        Toast.warning('你无权确认归还！')
        return false
    }
    try {
        const response = await fetch(`${BASE_URL}/admin/borrow-records/${borrowRecordId}/confirm-return`,{
            method : 'POST',
            headers : {
                'Content-Type' : 'application/json',
                'token' : sessionStorage.getItem('token')
            },
            body : JSON.stringify(
                BorrowReturnConfirm
            )
        })

        const res = await response.json();

        if(response.ok !== true || res.code !== 0){
            if(res.code !== 0){
                Toast.failure(`确认设备归还失败，${res.message}`)
            }
            console.log(`确认设备归还失败,错误码:${response.status},code ${res.code}`)
            return false
        }

        return true
    } catch (error) {
        console.error('确认设备归还失败')
        return false
    }
}
