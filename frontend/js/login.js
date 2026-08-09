const studentLogin  = document.getElementById('student-choose')
const adminLogin = document.getElementById('admin-choose');
const repairLogin = document.getElementById('repair-choose');

const registerButton = document.getElementById('register-button')
const submitButton = document.getElementById('submit-button');

const account = document.getElementById(`account`)
const password = document.getElementById(`password`)
const loginForm = document.getElementById('login-form')
const passwordToggle = document.getElementById('password-toggle')
const registrationField = document.querySelector('.registration-field')
const registrationCode = document.getElementById('registration-code')

let identity = 1;

// 重置身份和样式
function resetIdentity(){
    ;[studentLogin, adminLogin, repairLogin].forEach(option => {
        option.classList.remove('is-active')
        option.setAttribute('aria-checked', 'false')
    })
}

// 完成字符 -> 身份映射
/**
 * 
 * @param {HTMLElement} target 
 * @returns 
 */
function showIdentity(target){

    if(target === studentLogin){
        return 1;
    }
    else if(target === adminLogin){
        return 2;
    }
    else if(target === repairLogin){
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
    target.classList.add('is-active');
    target.setAttribute('aria-checked', 'true')
    identity = showIdentity(target);
    const isAdmin = identity === 2
    registrationField.hidden = !isAdmin
    registrationCode.required = isAdmin
}


// 注册 
async function register(){

    if(checkAccount(account) !==false && checkPassword(password) !== false){
        if(identity === 2 && !registrationCode.value.trim()){
            alert('请输入管理员注册码')
            return false
        }
        return  await sendRegister(checkAccount(account),checkPassword(password),apiChoose(),registrationCode.value.trim());
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
loginForm.addEventListener('submit', async event => {
    event.preventDefault()
    if(await submit() === true){
        alert("登录成功")
        window.location.replace(`/campus-equipment-mgr/frontend/pages/${apiChoose()}.html`)
    }
})

passwordToggle.addEventListener('click', () => {
    const shouldShow = password.type === 'password'
    password.type = shouldShow ? 'text' : 'password'
    passwordToggle.textContent = shouldShow ? '隐藏' : '显示'
    passwordToggle.setAttribute('aria-label', shouldShow ? '隐藏密码' : '显示密码')
})
