const originalFetch = window.fetch;
let isRedirecting = false;
class QueryData{
    page
    size
    category_id
    status
    equipment_name
    equipment_no
    location
    brand
    spec
    start_time
    end_time
    sort
    order
}

// 重写fetch，实现拦截器
window.fetch = async function (input , init ){

    if(window.location.pathname.includes(`/login`) || window.location.pathname.includes(`/index`)){
        return originalFetch.call(this,input,init)
    }

    const response = await originalFetch.call(this,input,init);


    if(response.status === 401){
        if(isRedirecting === false){
            isRedirecting = true;
            localStorage.removeItem('token');
            window.location.replace(`/login`);
        }
    }

    return response
}

