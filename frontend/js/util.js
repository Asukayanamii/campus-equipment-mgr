const ACCOUNT_RULE = /^[a-zA-Z0-9_]{6,24}$/
const ACCOUNT_RULE_DESCRIPTION = "字母或数字或下划线 ，长度在6-24"
const PASSWORD_RULE = /^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9_\!@#\$%\^&\*\(\)\-=]{6,24}$/
const PASSWORD_RULE_DESCRIPTION = "6-24 位，至少 1 个字母、至少 1 个数字，支持常用符号"


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
            window.location.replace(`/campus-equipment-mgr/frontend/login.html`);
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

//验证账号是否合规
/**
 * 
 * @param {HTMLHtmlElement} account 
 * @returns 
 */
function checkAccount(account){
    const stringAccount = account.value;
    if(ACCOUNT_RULE.test(stringAccount) === false){
        alert(`您提交的账号不符合要求，必须满足${ACCOUNT_RULE_DESCRIPTION}`);
        return false;
    }
    return stringAccount;
}

//验证密码是否合规
/**
 * 
 * @param {HTMLElement} password 
 * @returns 
 */
function checkPassword(password){
    const stringPassword = password.value;
    if(PASSWORD_RULE.test(stringPassword) === false){
        alert(`您提交的密码不符合要求，必须满足${PASSWORD_RULE_DESCRIPTION}`);
        return false;
    }
    return stringPassword;
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

class Result_Page_EquipmentOut{
    constructor({
        code,
        message,
        data
    } = {}){
        this.code = code
        this.message = message
        this.data = data
    }
}
