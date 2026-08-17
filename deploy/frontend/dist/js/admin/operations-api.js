async function adminBusinessRequest(path, { method = 'GET', query = {}, body } = {}){
    const params = new URLSearchParams()
    Object.entries(query).forEach(([key, value]) => {
        if(value !== '' && value !== null && value !== undefined) params.set(key, value)
    })
    const queryString = params.toString()
    try {
        const response = await fetch(`${BASE_URL}${path}${queryString ? `?${queryString}` : ''}`, {
            method,
            headers: {
                ...(body === undefined ? {} : { 'Content-Type': 'application/json' }),
                'token': sessionStorage.getItem('token')
            },
            body: body === undefined ? undefined : JSON.stringify(body)
        })
        const result = await response.json().catch(() => ({ message: '服务返回的数据格式不正确' }))
        if(!response.ok || result.code !== 0){
            Toast.failure(result.message || '操作失败')
            return false
        }
        return result.data ?? true
    } catch (error) {
        console.error('管理员业务请求失败', error)
        Toast.failure('网络异常，请稍后重试')
        return false
    }
}
