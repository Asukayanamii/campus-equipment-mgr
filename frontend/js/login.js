// 默认颜色
const DEFAULT_COLOR = ''
// 点击后颜色
const DEFAULT_TARGET_COLOR = 'green'

const studentLogin  = document.getElementById('student-choose')
const adminLogin = document.getElementById('admin-choose');
const repairLogin = document.getElementById('repair-choose');

const registerButton = document.getElementById('register-button')
const submitButton = document.getElementById('submit-button');

const account = document.getElementById(`account`)
const password = document.getElementById(`password`)

let identity = 1;
studentLogin.style.backgroundColor = `${DEFAULT_TARGET_COLOR}`;

// 重置身份和样式
function resetIdentity(){
    studentLogin.style.backgroundColor = `${DEFAULT_COLOR}`
    adminLogin.style.backgroundColor = `${DEFAULT_COLOR}`
    repairLogin.style.backgroundColor = `${DEFAULT_COLOR}`
}

// 完成字符 -> 身份映射
/**
 * 
 * @param {HTMLElement} target 
 * @returns 
 */
function showIdentity(target){

    if(target.innerText === `我是学生`){
        return 1;
    }
    else if(target.innerText === `我是管理`){
        return 2;
    }
    else if(target.innerText === `我是维修`){
        return 3;
    }
}

// 选择身份和样式
/**
 * 
 * @param {HTMLElement} target 
 */
function chooseIdentity(target){
    resetIdentity();
    target.style.backgroundColor = `${DEFAULT_TARGET_COLOR}`;
    identity = showIdentity(target);
}


// 注册 
async function register(){

    if(checkAccount(account) !==false && checkPassword(password) !== false){
        return  await sendRegister(checkAccount(account),checkPassword(password),apiChoose());
    }else{
        return false;
    }

}

//登录
async function submit(){
    return await sendSubmit(account.value,password.value,apiChoose())
}



studentLogin.addEventListener('click',async () => chooseIdentity(studentLogin))
repairLogin.addEventListener('click',async () => chooseIdentity(repairLogin))
adminLogin.addEventListener('click',async () => chooseIdentity(adminLogin))

registerButton.addEventListener('click',async () => {
    if(await register() === true ){
        alert("注册成功")
    }else{
        alert("注册失败")
    }
})
submitButton.addEventListener('click',async () => {
    if(await submit() === true){
        alert("登录成功")
        window.location.replace(`/campus-equipment-mgr/frontend/pages/${apiChoose()}.html`)
    }
})
