// 重写fetch，实现拦截器
const originalFetch = window.fetch;
let isRedirecting = false;
window.fetch = async function (input , init ){

    if(window.location.pathname.includes(`/login`) || window.location.pathname.includes(`/index`)){
        return originalFetch.call(this,input,init)
    }

    const response = await originalFetch.call(this,input,init);


    if(response.status !== 200){
        if(isRedirecting === false){
            isRedirecting = true;
            sessionStorage.removeItem('token');
            window.location.replace(`campus-equipment-mgr/frontend/login.html`);
        }
    }

    if(response.status !== 200){
        console.error(response.message);
    }

    return response
}
// 身份映射到接口
function apiChoose(){
    if(identity === 1){
        return `user`
    }else if(identity === 2){
        return `admin`
    }else if(identity === 3){
        return `repair`
    }
}

class EquipmentOut{
    constructor({
        id,
        equipmentNo,
        equipmentName,
        categoryId,
        categoryName,
        spec,
        brand,
        unit,
        location,
        purchaseDate,
        price,
        coverImg,
        status,
        remark,
        createTime,
        updateTime,
    } = {}){
        this.id = id;
        this.equipmentNo = equipmentNo;
        this.equipmentName = equipmentName;
        this.categoryId = categoryId;
        this.categoryName = categoryName;
        this.spec = spec;
        this.brand = brand;
        this.unit = unit;
        this.location = location;
        this.purchaseDate = purchaseDate;
        this.price = price;
        this.coverImg = coverImg;
        this.status = status;
        this.remark = remark;
        this.createTime = createTime;
        this.updateTime = updateTime;
    }
}

class Page_EquipmentOut{
    constructor({
        EquipmentOut,
        total,
        page,
        size,
        pages,
    } = {}){
        this.EquipmentOut = EquipmentOut;
        this.total = total;
        this.page = page;
        this.size = size;
        this.pages = pages;
    }
}

class Result {
    constructor({code,message,data} = {}){
        this.code = code;
        this.message = message;
        this.data = data;
    }
}

class QueryData{
    constructor({
        page,
        size,
        categoryId,
        status,
        equipmentName,
        equipmentNo,
        location,
        brand,
        spec,
        startTime,
        endTime,
        sort,
        order,
    } = {}) {
        this.page = page;
        this.size = size;
        this.categoryId = categoryId;
        this.status = status;
        this.equipmentName = equipmentName;
        this.equipmentNo = equipmentNo;
        this.location = location;
        this.brand = brand;
        this.spec = spec;
        this.startTime = startTime;
        this.endTime = endTime;
        this.sort = sort;
        this.order = order;

    }
}

class UpdateInDTO{
    constructor({
        name,
        password,
        image 
    } = {}){
        this.name = name;
        this.password = password;
        this.image = image;
    }
}
 
class GetMeOut {
    constructor({
        id,
        name,
        username,
        image,
        email,
        updateTime,
        createTime
    } = {}){
        this.id = id;
        this.name = name;
        this.username = username;
        this.image = image;
        this.email = email;
        this.updateTime = updateTime;
        this.createTime = createTime;
    }
}


