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

// 工单操作历史由后端按当前维修人员权限过滤。
function getMyRepairOrderOperationLogs(repairOrderId){
    return requestRepairOrders(`/repair/orders/${repairOrderId}/operation-logs`)
}

async function mutateRepairOrder(path, body){
    try {
        const response = await fetch(`${BASE_URL}${path}`, {
            method: 'POST',
            headers: {
                ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
                'token': sessionStorage.getItem('token')
            },
            body: body === undefined ? undefined : JSON.stringify(body)
        })
        const result = await response.json().catch(() => ({ message: '服务返回的数据格式不正确' }))
        if(!response.ok || result.code !== 0){
            Toast.failure(result.message || '工单操作失败')
            return false
        }
        return result.data || true
    } catch (error) {
        console.error('工单操作失败', error)
        Toast.failure('网络异常，请稍后重试')
        return false
    }
}

function acceptRepairOrder(repairOrderId){
    return mutateRepairOrder(`/repair/orders/${repairOrderId}/accept`)
}

function startRepairOrder(repairOrderId){
    return mutateRepairOrder(`/repair/orders/${repairOrderId}/start`)
}

function completeRepairOrder(repairOrderId, completion){
    return mutateRepairOrder(`/repair/orders/${repairOrderId}/completion`, completion)
}
