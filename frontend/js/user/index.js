const PAGE_SIZE = 24;
const DEFAULT_NAME = '代文秋'
const OFF_SETX = 0
const OFF_SETY = 0
const DEFAULT_PICTURE_URL = '../assets/images/all-icon..png'
const DEFAULT_EMAIL_DECRIPTION = "您当前未绑定邮箱"
const UNDINESE_EXPLAINATION = '未知'

const search = document.querySelector('#search')
const searchWayChoose = document.querySelector('#search-way-choose')

const dataShowing = document.getElementById(`data-showing`)

const profilePictureBox = document.getElementById('profile-picture-box')
const profileName = document.getElementById('profile-name')
const profilePicture = document.getElementById('profile-picture')

const start = document.getElementById('start')
const pre2 = document.getElementById('pre-2')
const pre1 = document.getElementById('pre-1')
const cur = document.getElementById('cur')
const aft1 = document.getElementById('aft-1')
const aft2 = document.getElementById('aft-2')
const end = document.getElementById('end')

const dataCard = document.getElementById('data-showing') 

let pageNow = 1;
let pageAll = 1;
let queryDataYouChange  = ''
const identity = 1
let defaultQueryData = new QueryData({
    page : pageNow,
    size : PAGE_SIZE
});

// 重置查询数据
function resetQueryData(){
    defaultQueryData = {
        page : pageNow,
        size : PAGE_SIZE
    }
}

// 检查按钮重复，务必在pageAll有数值的时候使用
function checkButton(){
    start.style.display = 'block'
    pre2.style.display = 'block'
    pre1.style.display = 'block'
    end.style.display = 'block'
    aft2.style.display = 'block'
    aft1.style.display = 'block'
    switch (Number(cur.innerHTML)){
        case 1 :
            start.style.display = 'none'
            pre2.style.display = 'none'
            pre1.style.display = 'none'
            break
        case 2 :
            pre2.style.display = 'none'
            pre1.style.display = 'none'
            break
        case 3 :
            pre2.style.display = 'none'
            break
    }

    switch(Number(cur.innerText)){
        case pageAll -2:
            end.style.display = 'none'
            break
        case pageAll - 1:
            end.style.display = 'none'
            aft2.style.display = 'none'
            break
        case pageAll :
            end.style.display = 'none'
            aft2.style.display = 'none'
            aft1.style.display = 'none'
            break
    }
    

}

// 给按钮赋值，务必在pageAll有数值的时候使用
function renderButton(){
    start.innerText = 1
    pre2.innerText = pageNow - 2
    pre1.innerText = pageNow - 1
    cur.innerText = pageNow
    aft1.innerText = pageNow + 1
    aft2.innerText = pageNow + 2
    end.innerText = pageAll
    cur.style.backgroundColor = 'red'
}

// 渲染数据
function renderData(QueryData = {}){
    getData(QueryData).then(res => {
        const list = res.data.items;
        dataShowing.innerHTML = ''
        list.forEach(i => {
            dataShowing.insertAdjacentHTML('beforeend',`
                <div class="data-card">
                    <h1>${i.equipmentName}</h1>
                    <p>${i.location}</p>
                    <div class="data-detail-showing">
                        <p>设备 ID:${i.id}</p>
                        <p>设备编号:${i.equipmentNo}</p>
                        <p>设备分类名称:${i.categoryName}</p>
                        <p>设备规格型号 ID:${i.spec}</p>
                        <p>设备品牌:${i.brand}</p>
                        <p>计量单位:${i.unit}</p>
                        <p>采购日期:${i.purchaseDate}</p>
                        <p>采购价格:${i.price}</p>
                        <p>设备状态:${i.status}</p>
                        <p>备注:${i.remark}</p>
                        <p>创建时间:${i.creatTime || UNDINESE_EXPLAINATION}</p>
                        <p>更新时间:${i.updateTime || UNDINESE_EXPLAINATION}</p>
                    </div>
                </div>
            `)
            const card = dataShowing.lastElementChild
            card.style.background = i.coverImg
                ? `linear-gradient(rgba(255,255,255,0.5), rgba(255,255,255,0.5)), url("${i.coverImg}")`
                : 'rgba(255,255,255,0.5)'
        });
        pageAll = res.data.pages;
        renderButton()
        checkButton()
    })
}

// 渲染个人信息
async function renderPersonalData(){
    const personalData = await getPersonalData(apiChoose())



    if(!personalData.name){
        profileName.innerText = `${DEFAULT_NAME}`
    }else{
        profileName.innerText = personalData.name
    }
    
    if(!personalData.image){
        profilePicture.src = '../assets/images/all-icon..png'
    }else{
        profilePicture.src = personalData.image
    }
}

// 渲染详情和修改面板
async function renderChangePanel(){
    const personalData = await getPersonalData(apiChoose())
    document.body.insertAdjacentHTML('beforeend',`
        <div class="change-panel">
            <button class="close-button">X</button> 
            <div class="profile-detail-showing">
                <div class="profile-picture-change-box">
                    <img src="${personalData.image || DEFAULT_PICTURE_URL}" alt="你的头像" class="profile-picture-box">
                    <p class="profile-picture-update-box">点击确认修改头像<input type="file"></p>
                </div>
                <p>你的id:${personalData.id}</p>
                <p>你的昵称:${personalData.name}</p>
                <p>你的账号:${personalData.username}</p>
                <p>你的邮箱:${personalData.email  || DEFAULT_EMAIL_DECRIPTION}</p>
                <p>上传更新时间:${personalData.updateTime}</p>
                <p>账号创建时间:${personalData.createTime}</p>
                <button id="change-profile-button">点击修改个人信息</button>
            </div>
        </div>
        `)
    document.querySelector('.change-panel .close-button').addEventListener('click', closePanel)
    const changeProfile = document.getElementById('change-profile-button')
    changeProfile.addEventListener('click',() => {
        renderChangeProfileSubmitWindow()
    })

}

// 关闭面板
function closePanel(){
      const dimOverlay = document.querySelector('.dim-overlay')
      const changePanel = document.querySelector('.change-panel')
      if(!(dimOverlay && changePanel)){
          console.log('没找到控制板或遮光罩')
          return
      }
      dimOverlay.remove()
      changePanel.remove()
}

// 召唤修改面板
function renderChangeProfileSubmitWindow(){
    document.body.insertAdjacentHTML('beforeend',`
        <div class="change-profile-submit-window">
        <button class="close-button-plus ">X</button>
        <div>
            <p>你修改用户名为：<input type="text" id="changed-name"></p>
        </div>
        <div class="change-profile-submit-window-password">
            <p>请先输入原密码：<input type="password" id="origin-password"></p>
            <p>请输入新的密码：<input type="password" id="new-password-first"></p>
            <p>再次输入新密码：<input type="password" id="new-password-second"></p>
        </div>
        <div class="change-profile-submit-window-button">
            <button>确定提交</button>
        </div>
    </div>`)
    const dimOverlay = document.querySelector('.dim-overlay')
    const closeButtonPlus = document.querySelector('.close-button-plus')
    const changeProfileSubmitWindowButton = document.querySelector('.change-profile-submit-window-button')
    const changedName  = document.querySelector('#changed-name')
    const originPassword = document.querySelector('#origin-password')
    const newPasswordFirst = document.querySelector('#new-password-first')
    const newPasswordSecond  = document.querySelector('#new-password-second')
    dimOverlay.style.zIndex = 600
    closeButtonPlus.addEventListener('click',() => {
        dimOverlay.style.zIndex = 400
        const changeProfileSubmitWindow = document.body.querySelector('.change-profile-submit-window')
        changeProfileSubmitWindow.remove()
    })
    changeProfileSubmitWindowButton.addEventListener('click',async () => {
        if(checkPassword(newPasswordFirst)){
            const originPasswordString = originPassword.value
            const newPasswordFirstString  = newPasswordFirst.value
            const newPasswordSecondString = newPasswordSecond.value
            if(!originPasswordString){
                console.log('原密码不能为空')
                return
            }
            if(!newPasswordFirst){
                alert('第一次密码不能为空')
                return
            }
            if(!newPasswordSecondString){
                alert('第二次密码不能为空')
            }
            if(newPasswordFirstString !== newPasswordSecondString){
                alert("两次密码输入不一致")
                return
            }

            const temUserName = (await getPersonalData(apiChoose())).username
            if(!await sendSubmit(temUserName,originPasswordString,apiChoose())){
                alert('原密码输入错误')
                return
            }

            const temName = (await getPersonalData(apiChoose())).name
            if(await changePersonalData({
                name : changedName.value || temName,
                password : newPasswordFirst.value
            },apiChoose())){
                alert('修改失败')
            }else{
                alert('修改成功')
            }
        }
    })
}


start.addEventListener('click', () =>{
     defaultQueryData.page = 1;
     pageNow = 1
     renderData(defaultQueryData)
})

end.addEventListener('click',() => {
    defaultQueryData.page = pageAll
    pageNow = pageAll
    renderData(defaultQueryData)
})

pre2.addEventListener('click' ,() => {
    defaultQueryData.page = pre2.innerText
    pageNow = pageNow - 2
    renderData(defaultQueryData)
})

pre1.addEventListener('click' ,() => {
    defaultQueryData.page = pre1.innerText
    pageNow = pageNow - 1
    renderData(defaultQueryData)
})

cur.addEventListener('click' ,() => {
    defaultQueryData.page = cur.innerText
    pageNow = pageNow
    renderData(defaultQueryData)
})

aft1.addEventListener('click' ,() => {
    defaultQueryData.page = aft1.innerText
    pageNow = pageNow + 1
    renderData(defaultQueryData)
})

aft2.addEventListener('click' ,() => {
    defaultQueryData.page = aft2.innerText
    pageNow = pageNow + 2
    renderData(defaultQueryData)
})

dataCard.addEventListener('mousemove', (e) => {
    const card = e.target.closest('.data-card')
    if (!card) return 
    const dataDetailShowing = card.querySelector('.data-detail-showing')
    // TODO:硬编码问题，有时间我就来修,这里的几个数字其实是data-detail-showing的大小
    const maxWidth = window.innerWidth
    const maxHeigt = window.innerHeight
    if(e.clientX + OFF_SETX + 200> maxWidth){
        dataDetailShowing.style.left = ( e.clientX + OFF_SETX -200) + 'px'
    }else{
        dataDetailShowing.style.left = (e.clientX + OFF_SETX ) +'px'
    }
    if(e.clientY + OFF_SETY +300> maxHeigt){
        dataDetailShowing.style.top = (e.clientY + OFF_SETY -300) + 'px'
    }else{
        dataDetailShowing.style.top = (e.clientY + OFF_SETY ) +'px'
    }
    
    
})

profilePictureBox.addEventListener('click',() => {
    renderChangePanel().then(() => {
        document.body.insertAdjacentHTML('beforeend',`
            <div class="dim-overlay"></div>
            `)
    })

})

searchWayChoose.addEventListener('change',(e) =>{
    switch (e.target.value){
        case 'no':
            break
        case 'reset':
            resetQueryData()
            queryDataYouChange = ''
            search.value = ''
            searchWayChoose.querySelector('option[value="categoryId"]').textContent = '设备分类ID'
            searchWayChoose.querySelector('option[value="status"]').textContent = '设备状态'
            searchWayChoose.querySelector('option[value="equipmentName"]').textContent = '设备名称'
            searchWayChoose.querySelector('option[value="equipmentNo"]').textContent = '设备编号'
            searchWayChoose.querySelector('option[value="location"]').textContent = '设备存放位置'
            searchWayChoose.querySelector('option[value="brand"]').textContent = '设备品牌'
            searchWayChoose.querySelector('option[value="spec"]').textContent = '设备规格型号'
            searchWayChoose.querySelector('option[value="startTime"]').textContent = '设备采购开始时间'
            searchWayChoose.querySelector('option[value="endTime"]').textContent = '设备采购结束时间'
            renderData(defaultQueryData)
            break
        case 'categoryId':
            queryDataYouChange  = 'categoryId'
            searchWayChoose.querySelector('option[value="categoryId"]').textContent = '设备分类ID（已指定）'
            break
        case 'status':
            queryDataYouChange  = 'status'
            searchWayChoose.querySelector('option[value="status"]').textContent = '设备状态（已指定）'
            break
        case 'equipmentName':
            queryDataYouChange  = 'equipmentName'
            searchWayChoose.querySelector('option[value="equipmentName"]').textContent = '设备名称（已指定）'
            break
        case 'equipmentNo':
            queryDataYouChange  = 'equipmentNo'
            searchWayChoose.querySelector('option[value="equipmentNo"]').textContent = '设备编号（已指定）'
            break
        case 'location':
            queryDataYouChange  = 'location'
            searchWayChoose.querySelector('option[value="location"]').textContent = '设备存放位置（已指定）'
            break
        case 'brand':
            queryDataYouChange  = 'brand'
            searchWayChoose.querySelector('option[value="brand"]').textContent = '设备品牌（已指定）'
            break
        case 'spec':
            queryDataYouChange  = 'spec'
            searchWayChoose.querySelector('option[value="spec"]').textContent = '设备规格型号（已指定）'
            break
        case 'startTime':
            queryDataYouChange  = 'startTime'
            searchWayChoose.querySelector('option[value="startTime"]').textContent = '设备采购开始时间（已指定）'
            break
        case 'endTime':
            queryDataYouChange  = 'endTime'
            searchWayChoose.querySelector('option[value="endTime"]').textContent = '设备采购结束时间（已指定）'
            break
    }
})

search.addEventListener('keydown',(e) =>{
    if(e.key === 'Enter'){
        if(!queryDataYouChange){
            alert('请选择搜索类型')
            return
        }
        defaultQueryData[queryDataYouChange]  = e.target.value
        defaultQueryData.page = 1
        pageNow = 1;
        renderData(defaultQueryData)
    }
})
renderData(defaultQueryData)
renderPersonalData()










