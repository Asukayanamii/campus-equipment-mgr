async function requestRepairOrders(path, queryData = {}){
    const params = new URLSearchParams()
    Object.entries(queryData).forEach(([key, value]) => {
        if(value !== null && value !== undefined && value !== '') params.set(key, value)
    })
    const query = params.toString()

    try {
        const response = await fetch(`${BASE_URL}${path}${query ? `?${query}` : ''}`, {
            headers: { 'token': sessionStorage.getItem('token') }
        })
        const result = await response.json().catch(() => ({ message: '服务返回的数据格式不正确' }))
        if(!response.ok || result.code !== 0){
            Toast.failure(result.message || '维修工单请求失败')
            return false
        }
        return result.data
    } catch (error) {
        console.error('维修工单请求失败', error)
        Toast.failure('网络异常，请稍后重试')
        return false
    }
}

function getMyRepairOrders(queryData){
    return requestRepairOrders('/repair/orders/page', queryData)
}

function getMyRepairOrderDetail(repairOrderId){
    return requestRepairOrders(`/repair/orders/${repairOrderId}`)
}
