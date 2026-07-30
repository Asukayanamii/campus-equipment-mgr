// 默认颜色
const DEFAULT_COLOR = ''
// 点击后颜色
const DEFAULT_TARGET_COLOR = 'green'
const ACCOUNT_RULE = /^[a-zA-Z0-9_]{6,24}$/
const ACCOUNT_RULE_DESCRIPTION = "字母或数字或下划线 ，长度在6-24"
const PASSWORD_RULE = /^(?=.*[a-zA-Z])(?=.*[0-9])[a-zA-Z0-9_\!@#\$%\^&\*\(\)\-=]{6,24}$/
const PASSWORD_RULE_DESCRIPTION = "6-24 位，至少 1 个字母、至少 1 个数字，支持常用符号"

const studentLogin  = document.getElementById('student-choose')
const adminLogin = document.getElementById('admin-choose');
const maintainerLogin = document.getElementById('maintainer-choose');

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
    maintainerLogin.style.backgroundColor = `${DEFAULT_COLOR}`
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

//验证账号是否合规
function checkAccount(){
    const stringAccount = account.value;
    if(ACCOUNT_RULE.test(stringAccount) === false){
        alert(`您提交的账号不符合要求，必须满足${ACCOUNT_RULE_DESCRIPTION}`);
        return false;
    }
    return stringAccount;
}

//验证密码是否合规
function checkPassword(){
    const stringPassword = password.value;
    if(PASSWORD_RULE.test(stringPassword) === false){
        alert(`您提交的密码不符合要求，必须满足${PASSWORD_RULE_DESCRIPTION}`);
        return false;
    }
    return stringPassword;
}


// 注册 
async function register(){

    if(checkAccount() !==false && checkPassword() !== false){
        return  await sendRegister(checkAccount(),checkPassword(),apiChoose());
    }else{
        return false;
    }

}

//登录
async function submit(){
    return await sendSubmit(account.value,password.value,apiChoose())
}



studentLogin.addEventListener('click',async () => chooseIdentity(studentLogin))
maintainerLogin.addEventListener('click',async () => chooseIdentity(maintainerLogin))
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
