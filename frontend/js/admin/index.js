const PAGE_SIZE = 24;
const DEFAULT_NAME = '代文秋'
const OFF_SETX = 0
const OFF_SETY = 0
const DEFAULT_PICTURE_URL = '../assets/images/all-icon..png'
const DEFAULT_EMAIL_DECRIPTION = "您当前未绑定邮箱"
const UNDINESE_EXPLAINATION = '未知'

const rightSide = document.querySelector('#right-side')



const profilePictureBox = document.getElementById('profile-picture-box')
const profileName = document.getElementById('profile-name')
const profilePicture = document.getElementById('profile-picture')




let pageNow = 1;
let pageAll = 1;
let queryDataYouChange  = ''
const identity = 2
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
    const start = document.getElementById('start')
    const pre2 = document.getElementById('pre-2')
    const pre1 = document.getElementById('pre-1')
    const cur = document.getElementById('cur')
    const aft1 = document.getElementById('aft-1')
    const aft2 = document.getElementById('aft-2')
    const end = document.getElementById('end')
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

// 给按钮赋值，务必在pageAll有数值和几个按钮已被获取的时候使用
function renderButton(){
    const start = document.getElementById('start')
    const pre2 = document.getElementById('pre-2')
    const pre1 = document.getElementById('pre-1')
    const cur = document.getElementById('cur')
    const aft1 = document.getElementById('aft-1')
    const aft2 = document.getElementById('aft-2')
    const end = document.getElementById('end')
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
    const dataShowing = document.getElementById(`data-showing`)
    getData(QueryData).then(res => {
        const list = res.data.items;
        dataShowing.innerHTML = ''
        list.forEach(i => {
            dataShowing.insertAdjacentHTML('beforeend',`
                <div class="data-card" data-id="${i.id}">
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

        // 管理端专属编辑设备
        document.querySelectorAll('.data-card').forEach((card) => {
            card.addEventListener('click', async () => {
                const equipment = await getDataById(card.dataset.id, apiChoose())
                if(!equipment) return        
                addBackgroundShadow()
                callEquipmentDetailWindow(equipment)
            })
        })
        
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

// 召唤渲染修改面板
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

// 召唤数据展示页
function callDataShowing(){
    rightSide.insertAdjacentHTML('beforeend',`
        <!-- 搜索框 -->
         <div class="search-box">
            <p>搜索：<input type="text" class="search" id="search"></p>
            <select id="search-way-choose" class="search-way-choose">
                <option value="no">请选择查询方式（支持联查）</option>
                <option value="reset">重置搜索</option>
                <option value="categoryId">设备分类ID</option>
                <option value="status">设备状态</option>
                <option value="equipmentName">设备名称</option>
                <option value="equipmentNo">设备编号</option>
                <option value="location">设备存放位置</option>
                <option value="brand">设备品牌</option>
                <option value="spec">设备规格型号</option>
                <option value="startTime">设备采购开始时间</option>
                <option value="endTime">设备采购结束时间</option>
            </select>
         </div>
        <!-- 数据展示 -->
        <div class="data-showing" id="data-showing">
            
        </div>

        <!-- 页码选择 -->
        <div class="page-choose-box">
            <button id="start"></button>
            <button id="pre-2"></button>
            <button id="pre-1"></button>
            <button id="cur"></button>
            <button id="aft-1"></button>
            <button id="aft-2"></button>
            <button id="end"></button>
        </div>`
    )
    attachEventsForPageButton()
    attachEventsForDataCard()
    attachEventsForSearchWayChoose()
}

// 给所有转换页码的按钮绑定事件
function attachEventsForPageButton(){
    const start = document.getElementById('start')
    const pre2 = document.getElementById('pre-2')
    const pre1 = document.getElementById('pre-1')
    const cur = document.getElementById('cur')
    const aft1 = document.getElementById('aft-1')
    const aft2 = document.getElementById('aft-2')
    const end = document.getElementById('end')
    start.addEventListener('click', () => {
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
}

// 给数据展示卡片绑定事件
function attachEventsForDataCard(){
    const dataCard = document.getElementById('data-showing') 
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
}

// 给下拉表单和搜索框绑定事件
function attachEventsForSearchWayChoose(){
    const search = document.querySelector('#search')
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
    const searchWayChoose = document.querySelector('#search-way-choose')
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
}

// 管理端特权:召唤并渲染可修改设备详情框
/**
 * 
 * @param {EquipmentOut} EquipmentOut 
 */
function callEquipmentDetailWindow(EquipmentOut){
    if(document.querySelector('.equipment-detail-window')){
        console.log('已唤出可修改设备详情框，无需再次操作')
        return
    }
    document.body.insertAdjacentHTML('beforeend',`
        <div class="equipment-detail-window">
            <button class="close-button-equipment-detail-window" id="close-button-equipment-detail-window">X</button>
            <div class="equipment-detail-window-change">
                <p>设备编号:<input type="text" id="equipmentNo" value="${EquipmentOut.equipmentNo ?? ''}"></p>
                <p>设备名称:<input type="text" id="equipmentName" value="${EquipmentOut.equipmentName ?? ''}"></p>
                <p>分类ID:<input type="text" id="categoryId" value="${EquipmentOut.categoryId ?? ''}"></p>
                <p>规格:<input type="text" id="spec" value="${EquipmentOut.spec ?? ''}"></p>
                <p>品牌:<input type="text" id="brand" value="${EquipmentOut.brand ?? ''}"></p>
                <p>单位:<input type="text" id="unit" value="${EquipmentOut.unit ?? ''}"></p>
                <p>位置:<input type="text" id="location" value="${EquipmentOut.location ?? ''}"></p>
                <p>购买日期:<input type="text" id="purchaseDate" value="${EquipmentOut.purchaseDate ?? ''}"></p>
                <p>价格:<input type="text" id="price" value="${EquipmentOut.price ?? ''}"></p>
                <p>封面图片:<input type="text" id="coverImg" value="${EquipmentOut.coverImg ?? ''}"></p>
                <p>状态:<input type="text" id="status" value="${EquipmentOut.status ?? ''}"></p>
                <p>备注:<input type="text" id="remark" value="${EquipmentOut.remark ?? ''}"></p>
            </div>
            <div class="equipment-detail-window-buttons">
                <button class="equipment-detail-window-delete-button">删除设备</button>
                <button class="equipment-detail-window-submit-button" id="equipment-detail-window-submit-button">提交修改</button>
            </div>
            
        </div>
        `)
    document.querySelector('#close-button-equipment-detail-window').addEventListener('click', () =>{
        document.querySelector('.equipment-detail-window').remove()
        document.querySelector('.dim-overlay')?.remove()
    })
    document.querySelector('#equipment-detail-window-submit-button').addEventListener('click',async() =>{
        const temEquipmentUpdate = new EquipmentUpdate()
        document.querySelectorAll('.equipment-detail-window-change p input').forEach( (e) =>{
            temEquipmentUpdate[e.id] = e.value
        })

        const ok = await updateEquipment(EquipmentOut.id,temEquipmentUpdate,apiChoose())
        if(!ok) return
        alert('更新设备成功')

        document.querySelector('#equipment-detail-window').remove()
        document.querySelector('.dim-overlay')?.remove()

        const fresh = await getDataById(EquipmentOut.id, apiChoose())
        if(!fresh) return         

        addBackgroundShadow()
        callEquipmentDetailWindow(fresh)
    })
    document.querySelector('.equipment-detail-window-delete-button').addEventListener('click',async() =>{
        if(confirm(`你确定要删除${EquipmentOut.equipmentName}吗，改操作不可逆`)){
            if(await deleteEquipment(EquipmentOut.id,apiChoose())){
            alert('删除成功')
            document.querySelector('.equipment-detail-window').remove()
            document.querySelector('.dim-overlay')?.remove()
            renderData(defaultQueryData)
        }
        }
    })
}

// 背景加阴影效果
function addBackgroundShadow(){
    if(document.querySelector('.dim-overlay')){
        console.log('阴影效果已添加，无需再次操作')
        return
    }
    document.body.insertAdjacentHTML('beforeend',`
        <div class="dim-overlay"></div>
        `)
}


// 点击头像时背景加阴影效果
profilePictureBox.addEventListener('click',() => {
    renderChangePanel().then(() => {
        addBackgroundShadow()
    })

})



document.querySelector('#data-showing-button').addEventListener('click',() =>{
    rightSide.innerHTML = ''
    callDataShowing()
    renderData(defaultQueryData)
})

document.querySelector('#admin-equipment-button').addEventListener('click',() =>{

    rightSide.innerHTML = ''
})

document.querySelector('#my-record-button').addEventListener('click',() =>{
    rightSide.innerHTML = ''
})


callDataShowing()
renderData(defaultQueryData)
renderPersonalData()










