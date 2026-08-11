const AdminRepairReportApi = (function(){
    // 本功能的接口统一在这里处理鉴权、业务状态码和网络错误。
    async function request(path, options = {}){
        try {
            const response = await fetch(`${BASE_URL}${path}`, {
                ...options,
                headers: {
                    ...(options.body ? { 'Content-Type': 'application/json' } : {}),
                    'token': sessionStorage.getItem('token'),
                    ...(options.headers || {})
                }
            })
            const result = await response.json().catch(() => ({ message: '服务返回的数据格式不正确' }))
            if(!response.ok || result.code !== 0){
                Toast.failure(result.message || '报修数据请求失败')
                return false
            }
            return result.data
        } catch (error) {
            console.error('报修数据请求失败', error)
            Toast.failure('网络异常，请稍后重试')
            return false
        }
    }

    function getPage(query = {}){
        const params = new URLSearchParams()
        Object.entries(query).forEach(([key, value]) => {
            if(value !== '' && value !== null && value !== undefined) params.set(key, value)
        })
        return request(`/admin/repair-reports/page?${params.toString()}`)
    }

    function getDetail(repairReportId){
        return request(`/admin/repair-reports/${repairReportId}`)
    }

    function confirmReport(repairReportId){
        return request(`/admin/repair-reports/${repairReportId}/confirm`, { method: 'POST' })
    }

    return { getPage, getDetail, confirmReport }
})()
