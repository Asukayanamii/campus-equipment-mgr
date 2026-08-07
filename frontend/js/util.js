const ACCOUNT_RULE = /^[a-zA-Z0-9_]{6,24}$/
const ACCOUNT_RULE_DESCRIPTION = "字母或数字或下划线 ，长度在6-24"
const PASSWORD_RULE = /^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9_\!@#\$%\^&\*\(\)\-=]{6,24}$/
const PASSWORD_RULE_DESCRIPTION = "6-24 位，至少 1 个字母、至少 1 个数字，支持常用符号"


// 设备状态编码与中文互转映射
const EQUIPMENT_STATUS_MAP = {
    available : '可用',
    pending_borrow : '待借用',
    borrowed : '借用中',
    pending_return : '待归还',
    damaged : '损坏',
    repair_pending : '待维修',
    repairing : '维修中',
    repaired : '已维修',
    scrapped : '已报废',
    offline : '下架',
}

// 借用记录状态编码与中文互转映射
const BORROW_RECORD_STATUS_MAP = {
    pending : '待审核',
    approved : '已通过',
    rejected : '已驳回',
    borrowed : '借用中',
    pending_return : '待确认归还',
    completed : '已完成',
}

// 维修工单状态编码与中文互转映射
const REPAIR_ORDER_STATUS_MAP = {
    pending_assign : '待派单',
    pending_repair : '待维修',
    repairing : '维修中',
    pending_confirm : '待确认',
    completed : '已完成',
    unrepairable : '无法维修',
    scrapped : '已报废',
}


// 重写fetch，实现拦截器
const originalFetch = window.fetch;
let isRedirecting = false;
window.fetch = async function (input , init ){

    if(window.location.pathname.includes(`/login`) || window.location.pathname.includes(`/index`)){
        return originalFetch.call(this,input,init)
    }

    const response = await originalFetch.call(this,input,init);


    if(response.status === 401){
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

// 英文状态编码转中文，用于展示
/**
 *
 * @param {Object} statusMap 状态映射对象
 * @param {string} status 英文状态编码
 * @returns {string}
 */
function statusToChinese(statusMap,status){
    return statusMap[status] ?? status
}

// 中文状态转英文状态编码，用于提交
/**
 *
 * @param {Object} statusMap 状态映射对象
 * @param {string} chinese 中文状态
 * @returns {string}
 */
function chineseToStatus(statusMap,chinese){
    return Object.keys(statusMap).find(key => statusMap[key] === chinese) ?? chinese
}

// 根据映射生成状态下拉选项
/**
 *
 * @param {Object} statusMap 状态映射对象
 * @param {string} currentStatus 当前英文状态编码，用于默认选中
 * @returns {string}
 */
function statusSelectOptions(statusMap,currentStatus){
    return Object.entries(statusMap).map(([key,chinese]) =>
        `<option value="${chinese}" ${key === currentStatus ? 'selected' : ''}>${chinese}</option>`
    ).join('')
}

// 生成年份下拉选项
/**
 *
 * @param {string} currentDate 当前日期字符串(如 2026-08-07)，缺省时默认今天
 * @returns {string}
 */
function yearSelectOptions(currentDate){
    const currentYear = new Date().getFullYear()
    const selectedYear = currentDate ? Number(currentDate.slice(0,4)) : currentYear
    const options = []
    for(let y = currentYear; y >= 1990; y--){
        options.push(`<option value="${y}" ${y === selectedYear ? 'selected' : ''}>${y}</option>`)
    }
    return options.join('')
}

// 生成月份下拉选项
/**
 *
 * @param {string} currentDate 当前日期字符串(如 2026-08-07)，缺省时默认今天
 * @returns {string}
 */
function monthSelectOptions(currentDate){
    const selectedMonth = currentDate ? currentDate.slice(5,7) : String(new Date().getMonth() + 1).padStart(2,'0')
    const options = []
    for(let m = 1; m <= 12; m++){
        const month = String(m).padStart(2,'0')
        options.push(`<option value="${month}" ${month === selectedMonth ? 'selected' : ''}>${month}</option>`)
    }
    return options.join('')
}

// 生成日下拉选项
/**
 *
 * @param {string} currentDate 当前日期字符串(如 2026-08-07)，缺省时默认今天
 * @returns {string}
 */
function daySelectOptions(currentDate){
    const selectedDay = currentDate ? currentDate.slice(8,10) : String(new Date().getDate()).padStart(2,'0')
    const options = []
    for(let d = 1; d <= 31; d++){
        const day = String(d).padStart(2,'0')
        options.push(`<option value="${day}" ${day === selectedDay ? 'selected' : ''}>${day}</option>`)
    }
    return options.join('')
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

class EquipmentCreate{
    constructor({
        equipmentNo,
        equipmentName,
        categoryId, 
        spec,
        brand,
        unit,
        location,
        purchaseDate,
        price,
        coverImg,
        status,
        remark,
    } = {}){
        this.equipmentNo = equipmentNo;
        this.equipmentName = equipmentName;
        this.categoryId = categoryId;
        this.spec = spec;
        this.brand = brand;
        this.unit = unit;
        this.location = location;
        this.purchaseDate = purchaseDate;
        this.price = price;
        this.coverImg = coverImg;
        this.status = status;
        this.remark = remark;
    }
}

class CategoryResp{
    constructor( {
        id,
        categoryName,
        sort,
        isDeleted,
        createTime,
        updateTime
    } = {}){
        this.id = id;
        this.categoryName = categoryName;
        this.sort = sort;
        this.isDeleted = isDeleted;
        this.createTime = createTime;
        this.updateTime = updateTime;
    }
}

class Page_CategoryResp{
    constructor({
        items,
        page,
        size,
        pages
    }={}){
        this.items = items;
        this.page = page;
        this.size = size;
        this.pages = pages;
    }
}

class EquipmentUpdate{
    constructor({
        equipmentNo,
        equipmentName,
        categoryId,
        spec,
        brand,
        unit,
        location,
        purchaseDate,
        price,
        coverImg,
        status,
        remark,
    } = {}){
        this.equipmentNo = equipmentNo;
        this.equipmentName = equipmentName;
        this.categoryId = categoryId;
        this.spec = spec;
        this.brand = brand;
        this.unit = unit;
        this.location = location;
        this.purchaseDate = purchaseDate;
        this.price = price;
        this.coverImg = coverImg;
        this.status = status;
        this.remark = remark;
    }
}
