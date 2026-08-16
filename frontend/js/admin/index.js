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

// 分类页独立的分页与搜索状态
let categoryPageNow = 1;
let categoryPageAll = 1;
let categoryQueryDataYouChange  = ''
let defaultCategoryQueryData = new QueryCategoryData({
    page : 1,
    size : PAGE_SIZE
});

// 记录页独立的分页与搜索状态
let recordPageNow = 1;
let recordPageAll = 1;
let defaultRecordQueryData = new QueryBorrowRecordData({
    page : 1,
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
                <div class="data-card status-${chineseToStatus(EQUIPMENT_STATUS_MAP, i.status || 'unknown')}" data-id="${i.id}">
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
            if(i.coverImg){
                const previewButton = document.createElement('button')
                previewButton.type = 'button'
                previewButton.className = 'data-card-image-preview'
                previewButton.dataset.imagePreviewSrc = i.coverImg
                previewButton.setAttribute('aria-label', `放大查看${i.equipmentName}封面`)
                previewButton.title = '查看封面大图'
                card.appendChild(previewButton)
            }
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
                Toast.warning('第一次密码不能为空')
                return
            }
            if(!newPasswordSecondString){
                Toast.warning('第二次密码不能为空')
            }
            if(newPasswordFirstString !== newPasswordSecondString){
                Toast.warning("两次密码输入不一致")
                return
            }

            const temUserName = (await getPersonalData(apiChoose())).username
            if(!await sendSubmit(temUserName,originPasswordString,apiChoose())){
                Toast.failure('原密码输入错误')
                return
            }

            const temName = (await getPersonalData(apiChoose())).name
            if(await changePersonalData({
                name : changedName.value || temName,
                password : newPasswordFirst.value
            },apiChoose())){
                Toast.failure('修改失败')
            }else{
                Toast.success('修改成功')
            }
        }
    })
}

// 召唤数据展示页
function callDataShowing(){
    rightSide.insertAdjacentHTML('beforeend',`
        <!-- 搜索框 -->
        <div class="search-box">
            <div class="filter-fields equipment-filter-fields">
                <label>设备分类<select data-equipment-filter="categoryId" disabled><option value="">正在加载分类...</option></select></label>
                <label>设备名称<input data-equipment-filter="equipmentName"></label>
                <label>设备编号<input data-equipment-filter="equipmentNo"></label>
                <label>位置<input data-equipment-filter="location"></label>
                <label>品牌<input data-equipment-filter="brand"></label>
                <label>规格<input data-equipment-filter="spec"></label>
                <label>状态<select data-equipment-filter="status"><option value="">全部</option>${Object.entries(EQUIPMENT_STATUS_MAP).map(([k,v])=>`<option value="${k}">${v}</option>`).join('')}</select></label>
            </div>
            <div class="filter-actions">
                <button type="button" class="equipment-filter-submit">查询</button><button type="button" class="equipment-filter-reset">重置</button><button type="button" class="add-equipment">新增设备</button>
            </div>
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
    attachEquipmentFilters()
    attachEventsForAddButton()
    populateEquipmentCategorySelect(document.querySelector('select[data-equipment-filter="categoryId"]'))
}

// 召唤分类展示页
function callCategoryShowing(){
    rightSide.insertAdjacentHTML('beforeend',`
        <section class="category-management-view">
        <!-- 搜索框 -->
        <div class="search-box">
            <div class="filter-fields">
                <label>设备分类<select data-category-filter="id" disabled><option value="">正在加载分类...</option></select></label>
                <label>分类名称<input data-category-filter="categoryName"></label>
            </div>
            <div class="filter-actions">
                <button type="button" class="category-filter-submit">查询</button><button type="button" class="category-filter-reset">重置</button><button type="button" class="add-category">新增分类</button>
            </div>
        </div>
        <!-- 分类列表 -->
        <div class="category-showing" id="category-showing">

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
        </div>
        </section>`
    )
    attachEventsForCategoryPageButton()
    attachCategoryFilters()
    attachEventsForAddCategoryButton()
    populateEquipmentCategorySelect(document.querySelector('select[data-category-filter="id"]'))
    renderCategory(defaultCategoryQueryData)
}

function attachEquipmentFilters(){
    const root = document.querySelector('.search-box')
    const apply = () => { defaultQueryData = {page:1,size:PAGE_SIZE}; root.querySelectorAll('[data-equipment-filter]').forEach(el=>{if(el.value) defaultQueryData[el.dataset.equipmentFilter]=el.value}); pageNow=1; renderData(defaultQueryData) }
    root.querySelector('.equipment-filter-submit').addEventListener('click', apply)
    root.querySelector('.equipment-filter-reset').addEventListener('click', ()=>{root.querySelectorAll('[data-equipment-filter]').forEach(el=>el.value=''); apply()})
}

function attachCategoryFilters(){
    const root = document.querySelector('.search-box')
    const apply = () => { defaultCategoryQueryData = {page:1,size:PAGE_SIZE}; root.querySelectorAll('[data-category-filter]').forEach(el=>{if(el.value) defaultCategoryQueryData[el.dataset.categoryFilter]=el.value}); categoryPageNow=1; renderCategory(defaultCategoryQueryData) }
    root.querySelector('.category-filter-submit').addEventListener('click', apply)
    root.querySelector('.category-filter-reset').addEventListener('click', ()=>{root.querySelectorAll('[data-category-filter]').forEach(el=>el.value=''); apply()})
}

// 重置分类查询数据
function resetCategoryQueryData(){
    defaultCategoryQueryData = new QueryCategoryData({
        page : categoryPageNow,
        size : PAGE_SIZE
    })
}

// 刷新当前页签的数据，数据展示页和分类展示页通用
function renderCurrentView(){
    if(document.getElementById('data-showing')){
        renderData(defaultQueryData)
    }else if(document.getElementById('category-showing')){
        renderCategory(defaultCategoryQueryData)
    }
}

function layoutCategoryColumns(categoryShowing){
    const cells = Array.from(categoryShowing.querySelectorAll('.category-cell'))
        .sort((left, right) => Number(left.dataset.categoryOrder) - Number(right.dataset.categoryOrder))
    if(cells.length === 0) return

    const minColumnWidth = 300
    const columnGap = 14
    const columnCount = Math.max(1, Math.min(cells.length, Math.floor((categoryShowing.clientWidth + columnGap) / (minColumnWidth + columnGap))))
    categoryShowing.style.setProperty('--category-column-count', columnCount)
    const columns = Array.from({ length: columnCount }, () => {
        const column = document.createElement('div')
        column.className = 'category-col'
        return column
    })

    categoryShowing.replaceChildren(...columns)
    cells.forEach((cell, index) => columns[index % columnCount].appendChild(cell))
}

// 渲染响应式分类卡片，展开设备时只影响当前分类卡片。
async function renderCategory(QueryData = {}){
    const categoryShowing = document.getElementById('category-showing')
    const res = await getCategoryData(QueryData)
    if(!res || res.code !== 0 || !res.data) return
    const list = res.data.items || []
    categoryShowing.innerHTML = ''
    if(list.length === 0){
        categoryShowing.insertAdjacentHTML('beforeend',`
            <p>暂无分类</p>
        `)
        return
    }
    list.forEach((category, index) => {
        categoryShowing.insertAdjacentHTML('beforeend', `
            <div class="category-cell" data-category-order="${index}">
                <div class="category-bar" data-category-id="${category.id}" aria-expanded="false">
                    <span class="category-info">
                        <span class="category-id">分类 #${category.id}</span>
                        <span class="category-name">${category.categoryName}</span>
                    </span>
                    <span class="category-actions">
                        <button class="category-add-equipment" type="button" title="向该分类新增设备" aria-label="向${category.categoryName}分类新增设备">＋</button>
                        <span class="category-arrow" aria-hidden="true">▸</span>
                    </span>
                </div>
                <div class="category-members" id="category-members-${category.id}">
                    <div class="category-members-inner"></div>
                </div>
            </div>
        `)
    })
    layoutCategoryColumns(categoryShowing)
    categoryPageAll = res.data.pages || 1
    renderCategoryButton()
    checkCategoryButton()
    // 给分类条绑定展开/收起，以及新增设备按钮
    categoryShowing.querySelectorAll('.category-bar').forEach(bar => {
        bar.addEventListener('click', async () => {
            await toggleCategoryMembers(bar)
        })
        bar.querySelector('.category-add-equipment').addEventListener('click',(e) =>{
            e.stopPropagation()
            addNewEquipmentPanel(bar.dataset.categoryId)
            addBackgroundShadow()
        })
        document.dispatchEvent(new CustomEvent('admin-category-rendered', {
            detail: { bar, categoryId: Number(bar.dataset.categoryId) }
        }))
    })
}

// 获取某分类下全部设备，自动翻页
async function getAllEquipmentByCategory(categoryId){
    let page = 1
    const all = []
    let pages = 1
    do{
        const res = await getData(new QueryData({ page, size : 100, categoryId }))
        if(!res || res.code !== 0 || !res.data) break
        all.push(...(res.data.items || []))
        pages = res.data.pages
        page++
    }while(page <= pages)
    return all
}

// 展开/收起分类下的成员
async function toggleCategoryMembers(bar){
    const categoryId = bar.dataset.categoryId
    const membersBox = document.getElementById(`category-members-${categoryId}`)
    if(!membersBox) return
    const cell = bar.closest('.category-cell')
    const membersInner = membersBox.querySelector('.category-members-inner') || membersBox

    if(membersBox.dataset.loading === 'true') return
    if(membersBox.classList.contains('is-open')){
        membersBox.classList.remove('is-open')
        cell?.classList.remove('is-open')
        bar.setAttribute('aria-expanded', 'false')
        window.setTimeout(() => {
            if(!membersBox.classList.contains('is-open')) membersInner.innerHTML = ''
        }, 280)
        return
    }

    membersInner.innerHTML = ''
    membersBox.dataset.loading = 'true'
    const members = await getAllEquipmentByCategory(categoryId)
    delete membersBox.dataset.loading
    if(members.length === 0){
        membersInner.insertAdjacentHTML('beforeend', `
            <p class="member-empty">&#x8BE5;&#x5206;&#x7C7B;&#x6682;&#x65E0;&#x8BBE;&#x5907;</p>
        `)
    }else{
        const membersHtml = members.map(equipment => `
            <div class="member-row" data-equipment-id="${equipment.id}">
                <span class="member-name">${equipment.equipmentName}</span>
                <span class="member-meta">${equipment.equipmentNo} - ${statusToChinese(EQUIPMENT_STATUS_MAP,equipment.status)} - ${equipment.location}</span>
            </div>
        `).join('')
        membersInner.insertAdjacentHTML('beforeend', membersHtml)
    }
    void membersBox.offsetHeight
    cell?.classList.add('is-open')
    membersBox.classList.add('is-open')
    bar.setAttribute('aria-expanded', 'true')
    membersInner.querySelectorAll('.member-row').forEach(row => {
        row.addEventListener('click', async () => {
            const equipment = await getDataById(row.dataset.equipmentId, apiChoose())
            if(!equipment) return
            addBackgroundShadow()
            callEquipmentDetailWindow(equipment)
        })
    })
}

// 检查分类页码按钮，务必在categoryPageAll有数值的时候使用
function checkCategoryButton(){
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
        case categoryPageAll - 2:
            end.style.display = 'none'
            break
        case categoryPageAll - 1:
            end.style.display = 'none'
            aft2.style.display = 'none'
            break
        case categoryPageAll :
            end.style.display = 'none'
            aft2.style.display = 'none'
            aft1.style.display = 'none'
            break
    }
}

// 给分类页码按钮赋值，务必在categoryPageAll有数值和几个按钮已被获取的时候使用
function renderCategoryButton(){
    const start = document.getElementById('start')
    const pre2 = document.getElementById('pre-2')
    const pre1 = document.getElementById('pre-1')
    const cur = document.getElementById('cur')
    const aft1 = document.getElementById('aft-1')
    const aft2 = document.getElementById('aft-2')
    const end = document.getElementById('end')
    start.innerText = 1
    pre2.innerText = categoryPageNow - 2
    pre1.innerText = categoryPageNow - 1
    cur.innerText = categoryPageNow
    aft1.innerText = categoryPageNow + 1
    aft2.innerText = categoryPageNow + 2
    end.innerText = categoryPageAll
    cur.style.backgroundColor = 'red'
}

// 给分类页码按钮绑定事件
function attachEventsForCategoryPageButton(){
    const start = document.getElementById('start')
    const pre2 = document.getElementById('pre-2')
    const pre1 = document.getElementById('pre-1')
    const cur = document.getElementById('cur')
    const aft1 = document.getElementById('aft-1')
    const aft2 = document.getElementById('aft-2')
    const end = document.getElementById('end')
    start.addEventListener('click', () => {
        defaultCategoryQueryData.page = 1;
        categoryPageNow = 1
        renderCategory(defaultCategoryQueryData)
    })

    end.addEventListener('click',() => {
        defaultCategoryQueryData.page = categoryPageAll
        categoryPageNow = categoryPageAll
        renderCategory(defaultCategoryQueryData)
    })

    pre2.addEventListener('click' ,() => {
        defaultCategoryQueryData.page = pre2.innerText
        categoryPageNow = categoryPageNow - 2
        renderCategory(defaultCategoryQueryData)
    })

    pre1.addEventListener('click' ,() => {
        defaultCategoryQueryData.page = pre1.innerText
        categoryPageNow = categoryPageNow - 1
        renderCategory(defaultCategoryQueryData)
    })

    cur.addEventListener('click' ,() => {
        defaultCategoryQueryData.page = cur.innerText
        renderCategory(defaultCategoryQueryData)
    })

    aft1.addEventListener('click' ,() => {
        defaultCategoryQueryData.page = aft1.innerText
        categoryPageNow = categoryPageNow + 1
        renderCategory(defaultCategoryQueryData)
    })

    aft2.addEventListener('click' ,() => {
        defaultCategoryQueryData.page = aft2.innerText
        categoryPageNow = categoryPageNow + 2
        renderCategory(defaultCategoryQueryData)
    })
}

// 给分类搜索下拉框绑定事件
function attachEventsForCategorySearchWayChoose(){
    const search = document.querySelector('#search')
    search.addEventListener('keydown',(e) =>{
        if(e.key === 'Enter'){
            if(!categoryQueryDataYouChange){
                Toast.warning('请选择搜索类型')
                return
            }
            defaultCategoryQueryData[categoryQueryDataYouChange]  = e.target.value
            defaultCategoryQueryData.page = 1
            categoryPageNow = 1;
            renderCategory(defaultCategoryQueryData)
        }
    })
    const searchWayChoose = document.querySelector('#search-way-choose')
    searchWayChoose.addEventListener('change',(e) =>{
        switch (e.target.value){
            case 'no':
                break
            case 'reset':
                resetCategoryQueryData()
                categoryQueryDataYouChange = ''
                search.value = ''
                searchWayChoose.querySelector('option[value="id"]').textContent = '设备分类名称'
                searchWayChoose.querySelector('option[value="categoryName"]').textContent = '设备分类名称'
                renderCategory(defaultCategoryQueryData)
                break
            case 'id':
                categoryQueryDataYouChange  = 'id'
                searchWayChoose.querySelector('option[value="id"]').textContent = '设备分类名称（已指定）'
                break
            case 'categoryName':
                categoryQueryDataYouChange  = 'categoryName'
                searchWayChoose.querySelector('option[value="categoryName"]').textContent = '设备分类名称（已指定）'
                break
        }
    })
}

// 给新建分类按钮绑定事件
function attachEventsForAddCategoryButton(){
    const addCategory = document.querySelector('.add-category')
    if(!addCategory){
        return
    }
    addCategory.addEventListener('click',() =>{
        addNewCategoryPanel()
        addBackgroundShadow()
    })
}

// 呼出新增分类面板
function addNewCategoryPanel(){
    const addEquipmentPanel = document.querySelector('.add-equipment-panel')
    if(!addEquipmentPanel){
        console.log('没找到新增分类面板')
        return
    }
    if(addEquipmentPanel.querySelector('.add-equipment-panel-window')){
        console.log('已唤出新增面板，无需再次操作')
        return
    }
    addEquipmentPanel.style.display = 'block'
    addEquipmentPanel.insertAdjacentHTML('beforeend',`
        <div class="add-equipment-panel-window">
            <button class="close-button-plus">X</button>
            <div class="add-equipment-panel-change">
                <p>分类名称:<input type="text" id="categoryName"></p>
            </div>
            <div class="add-equipment-panel-buttons">
                <button class="add-equipment-panel-submit-button">确定提交</button>
            </div>
        </div>
    `)
    const closeButtonPlus = addEquipmentPanel.querySelector('.close-button-plus')
    const addCategoryPanelButton = addEquipmentPanel.querySelector('.add-equipment-panel-submit-button')
    closeButtonPlus.addEventListener('click',closeAddEquipmentPanel)
    addCategoryPanelButton.addEventListener('click',async() =>{
        const temCategoryCreate = new CategoryCreate({
            categoryName : addEquipmentPanel.querySelector('#categoryName').value
        })
        const ok = await addNewCategory(temCategoryCreate)
        if(!ok) return
        Toast.success('新增分类成功')
        invalidateEquipmentCategoryMap()
        populateEquipmentCategorySelect(document.querySelector('select[data-category-filter="id"]'))

        closeAddEquipmentPanel()
        renderCategory(defaultCategoryQueryData)
    })
}

// 给新增设备按钮绑定事件
function attachEventsForAddButton(){
    const addEquipment = document.querySelector('.add-equipment')
    if(!addEquipment){
        return
    }
    addEquipment.addEventListener('click',() =>{
        addNewEquipmentPanel()
        addBackgroundShadow()
    })
}

// 呼出新增设备面板
function addNewEquipmentPanel(categoryId){
    const addEquipmentPanel = document.querySelector('.add-equipment-panel')
    if(!addEquipmentPanel){
        console.log('没找到新增设备面板')
        return
    }
    if(addEquipmentPanel.querySelector('.add-equipment-panel-window')){
        console.log('已唤出新增设备面板，无需再次操作')
        return
    }
    addEquipmentPanel.style.display = 'block'
    addEquipmentPanel.insertAdjacentHTML('beforeend',`
        <div class="add-equipment-panel-window">
            <button class="close-button-plus">X</button>
            <div class="add-equipment-panel-change">
                <p>设备编号:<input type="text" id="equipmentNo"></p>
                <p>设备名称:<input type="text" id="equipmentName"></p>
                <p>分类ID:<input type="text" id="categoryId" value="${categoryId ?? ''}"></p>
                <p>规格:<input type="text" id="spec"></p>
                <p>品牌:<input type="text" id="brand"></p>
                <p>单位:<input type="text" id="unit"></p>
                <p>位置:<input type="text" id="location"></p>
                <p class="date-choose-box">购买日期:
                    <select id="purchaseDateYear">${yearSelectOptions()}</select>年
                    <select id="purchaseDateMonth">${monthSelectOptions()}</select>月
                    <select id="purchaseDateDay">${daySelectOptions()}</select>日
                </p>
                <p>价格:<input type="text" id="price"></p>
                <p>封面图片:<input type="file" id="coverImgFile" accept="image/*"><input type="hidden" id="coverImg"></p>
                <p>状态:<select id="status">${statusSelectOptions(EQUIPMENT_STATUS_MAP)}</select></p>
                <p>备注:<input type="text" id="remark"></p>
            </div>
            <div class="add-equipment-panel-buttons">
                <button class="add-equipment-panel-submit-button">确定提交</button>
            </div>
        </div>
    `)
    const closeButtonPlus = addEquipmentPanel.querySelector('.close-button-plus')
    const addEquipmentPanelButton = addEquipmentPanel.querySelector('.add-equipment-panel-submit-button')
    closeButtonPlus.addEventListener('click',closeAddEquipmentPanel)
    addEquipmentPanel.querySelector('#coverImgFile').addEventListener('change', async event => {
        const url = await uploadImage(event.target.files[0]); if(url) addEquipmentPanel.querySelector('#coverImg').value = url
    })
    addEquipmentPanelButton.addEventListener('click',async() =>{
        const temEquipmentCreate = new EquipmentCreate()
        addEquipmentPanel.querySelectorAll('.add-equipment-panel-change p input, .add-equipment-panel-change p select').forEach( (e) =>{
            if(e.id === 'status'){
                temEquipmentCreate[e.id] = chineseToStatus(EQUIPMENT_STATUS_MAP,e.value)
            }else if(e.id !== 'purchaseDateYear' && e.id !== 'purchaseDateMonth' && e.id !== 'purchaseDateDay'){
                temEquipmentCreate[e.id] = e.value
            }
        })
        temEquipmentCreate.purchaseDate = `${addEquipmentPanel.querySelector('#purchaseDateYear').value}-${addEquipmentPanel.querySelector('#purchaseDateMonth').value}-${addEquipmentPanel.querySelector('#purchaseDateDay').value}`

        const ok = await addNewEquipment(temEquipmentCreate,apiChoose())
        if(!ok) return
        Toast.success('新增设备成功')

        closeAddEquipmentPanel()
        renderCurrentView()
    })
}

function closeAddEquipmentPanel(){
    const addEquipmentPanel = document.querySelector('.add-equipment-panel')
    const dimOverlay = document.querySelector('.dim-overlay')
    if(!addEquipmentPanel){
        console.log('没找到新增设备面板')
        return
    }
    addEquipmentPanel.innerHTML = ''
    addEquipmentPanel.style.display = 'none'
    dimOverlay?.remove()
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
                Toast.warning('请选择搜索类型')
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
                searchWayChoose.querySelector('option[value="categoryId"]').textContent = '设备分类名称'
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
            searchWayChoose.querySelector('option[value="categoryId"]').textContent = '设备分类名称（已指定）'
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
        <div class="equipment-detail-window" role="dialog" aria-modal="true" aria-labelledby="equipment-edit-title">
            <header class="equipment-detail-header">
                <div><p>设备管理</p><h2 id="equipment-edit-title">编辑设备信息</h2></div>
                <button class="close-button-equipment-detail-window" id="close-button-equipment-detail-window" type="button" aria-label="关闭">×</button>
            </header>
            <div class="equipment-detail-window-change">
                <label class="equipment-edit-field"><span>设备编号</span><input data-equipment-edit-field type="text" id="equipmentNo" value="${EquipmentOut.equipmentNo ?? ''}"></label>
                <label class="equipment-edit-field"><span>设备名称</span><input data-equipment-edit-field type="text" id="equipmentName" value="${EquipmentOut.equipmentName ?? ''}"></label>
                <label class="equipment-edit-field"><span>分类 ID</span><input data-equipment-edit-field type="number" id="categoryId" value="${EquipmentOut.categoryId ?? ''}"></label>
                <label class="equipment-edit-field"><span>规格型号</span><input data-equipment-edit-field type="text" id="spec" value="${EquipmentOut.spec ?? ''}"></label>
                <label class="equipment-edit-field"><span>品牌</span><input data-equipment-edit-field type="text" id="brand" value="${EquipmentOut.brand ?? ''}"></label>
                <label class="equipment-edit-field"><span>计量单位</span><input data-equipment-edit-field type="text" id="unit" value="${EquipmentOut.unit ?? ''}"></label>
                <label class="equipment-edit-field"><span>存放位置</span><input data-equipment-edit-field type="text" id="location" value="${EquipmentOut.location ?? ''}"></label>
                <div class="equipment-edit-field date-choose-box"><span>购买日期</span><div class="equipment-date-inputs">
                    <label><select id="purchaseDateYear" aria-label="购买年份">${yearSelectOptions(EquipmentOut.purchaseDate)}</select><span>年</span></label>
                    <label><select id="purchaseDateMonth" aria-label="购买月份">${monthSelectOptions(EquipmentOut.purchaseDate)}</select><span>月</span></label>
                    <label><select id="purchaseDateDay" aria-label="购买日期">${daySelectOptions(EquipmentOut.purchaseDate)}</select><span>日</span></label>
                </div></div>
                <label class="equipment-edit-field"><span>采购价格</span><input data-equipment-edit-field type="number" id="price" min="0" step="0.01" value="${EquipmentOut.price ?? ''}"></label>
                <label class="equipment-edit-field"><span>设备状态</span><select data-equipment-edit-field id="status">${statusSelectOptions(EQUIPMENT_STATUS_MAP, EquipmentOut.status)}</select></label>
                <div class="equipment-edit-field equipment-cover-field"><span>封面图片</span><img class="equipment-cover-preview" alt="设备封面" hidden><div class="equipment-file-control"><label class="equipment-file-picker" for="coverImgFile">选择图片</label><span class="equipment-file-name">${EquipmentOut.coverImg ? '已上传封面，可重新选择' : '暂未上传封面'}</span></div><input type="file" id="coverImgFile" accept="image/*"><input data-equipment-edit-field type="hidden" id="coverImg" value="${EquipmentOut.coverImg ?? ''}"></div>
                <label class="equipment-edit-field equipment-edit-field-wide"><span>备注</span><textarea data-equipment-edit-field id="remark" rows="3">${EquipmentOut.remark ?? ''}</textarea></label>
            </div>
            <div class="equipment-detail-window-buttons">
                <button class="equipment-detail-window-delete-button" type="button">删除设备</button>
                <button class="equipment-detail-window-submit-button" id="equipment-detail-window-submit-button" type="button">保存修改</button>
            </div>
            
        </div>
        `)
    const equipmentWindow = document.querySelector('.equipment-detail-window')
    const coverPreview = equipmentWindow.querySelector('.equipment-cover-preview')
    if(EquipmentOut.coverImg){
        coverPreview.src = EquipmentOut.coverImg
        coverPreview.hidden = false
    }
    if(EquipmentOut.coverImg) equipmentWindow.style.backgroundImage = `linear-gradient(rgba(255,255,255,.86), rgba(255,255,255,.86)), url("${EquipmentOut.coverImg}")`
    equipmentWindow.querySelector('#close-button-equipment-detail-window').addEventListener('click', () =>{
        equipmentWindow.remove()
        document.querySelector('.dim-overlay')?.remove()
    })
    equipmentWindow.querySelector('#coverImgFile').addEventListener('change', async event => {
        const file = event.target.files[0]
        if(!file) return
        const fileName = equipmentWindow.querySelector('.equipment-file-name')
        fileName.textContent = '正在上传...'
        const url = await uploadImage(file)
        if(url){
            equipmentWindow.querySelector('#coverImg').value = url
            coverPreview.src = url
            coverPreview.hidden = false
            fileName.textContent = file.name
        }else{
            fileName.textContent = '上传失败，请重新选择'
        }
    })
    equipmentWindow.querySelector('#equipment-detail-window-submit-button').addEventListener('click',async() =>{
        const temEquipmentUpdate = new EquipmentUpdate()
        equipmentWindow.querySelectorAll('[data-equipment-edit-field]').forEach( (e) =>{
            if(e.id === 'status'){
                temEquipmentUpdate[e.id] = chineseToStatus(EQUIPMENT_STATUS_MAP,e.value)
            }else{
                temEquipmentUpdate[e.id] = e.value
            }
        })
        temEquipmentUpdate.purchaseDate = `${equipmentWindow.querySelector('#purchaseDateYear').value}-${equipmentWindow.querySelector('#purchaseDateMonth').value}-${equipmentWindow.querySelector('#purchaseDateDay').value}`

        const ok = await updateEquipment(EquipmentOut.id,temEquipmentUpdate,apiChoose())
        if(!ok) return
        Toast.success('更新设备成功')

        equipmentWindow.remove()
        document.querySelector('.dim-overlay')?.remove()

        const fresh = await getDataById(EquipmentOut.id, apiChoose())
        if(!fresh) return         

        addBackgroundShadow()
        callEquipmentDetailWindow(fresh)
    })
    equipmentWindow.querySelector('.equipment-detail-window-delete-button').addEventListener('click',async() =>{
        if(confirm(`确定要删除“${EquipmentOut.equipmentName}”吗？该操作不可逆。`)){
            if(await deleteEquipment(EquipmentOut.id,apiChoose())){
            Toast.success('删除成功')
            document.querySelector('.equipment-detail-window').remove()
            document.querySelector('.dim-overlay')?.remove()
            renderCurrentView()
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



// ============ 借用记录（全部借用记录） ============

// 召唤借用记录页
function callRecordShowing(){
    rightSide.insertAdjacentHTML('beforeend',`
        <!-- 搜索框 -->
        <div class="search-box">
            <div class="filter-fields record-filter-fields">
                <label>借用状态<select data-admin-record-filter="status"><option value="">全部状态</option>${Object.entries(BORROW_RECORD_STATUS_MAP).map(([value,label]) => `<option value="${value}">${label}</option>`).join('')}</select></label>
                <label>申请人或设备<input data-admin-record-filter="keyword" maxlength="100"></label>
                <label>申请人 ID<input data-admin-record-filter="userId" type="number" min="1"></label>
                <label>设备 ID<input data-admin-record-filter="equipmentId" type="number" min="1"></label>
                <label>开始时间下限<input data-admin-record-filter="startTime" type="datetime-local"></label>
                <label>结束时间上限<input data-admin-record-filter="endTime" type="datetime-local"></label>
            </div>
            <div class="filter-actions">
                <button class="record-filter-submit admin-record-filter-submit" type="button">查询</button>
                <button class="record-filter-reset admin-record-filter-reset" type="button">重置</button>
            </div>
        </div>
        <!-- 记录列表 -->
        <div class="record-showing" id="record-showing">

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
    attachEventsForRecordPageButton()
    attachAdminRecordFilters()
    renderRecordData(defaultRecordQueryData)
}

function attachAdminRecordFilters(){
    const root = document.querySelector('.record-filter-fields')?.closest('.search-box')
    if(!root) return
    const apply = () => {
        defaultRecordQueryData = new QueryBorrowRecordData({ page: 1, size: PAGE_SIZE })
        root.querySelectorAll('[data-admin-record-filter]').forEach(field => {
            if(field.value) defaultRecordQueryData[field.dataset.adminRecordFilter] = field.value
        })
        recordPageNow = 1
        renderRecordData(defaultRecordQueryData)
    }
    root.querySelector('.admin-record-filter-submit').addEventListener('click', apply)
    root.querySelector('.admin-record-filter-reset').addEventListener('click', () => {
        root.querySelectorAll('[data-admin-record-filter]').forEach(field => { field.value = '' })
        apply()
    })
    root.querySelectorAll('[data-admin-record-filter]').forEach(field => {
        field.addEventListener('keydown', event => {
            if(event.key === 'Enter') apply()
        })
    })
}

// 渲染全部借用记录列表
async function renderRecordData(QueryData = {}){
    const recordShowing = document.getElementById('record-showing')
    const res = await getBorrowRecordData(QueryData)
    if(!res || res.code !== 0 || !res.data) return
    const list = res.data.items || []
    recordShowing.innerHTML = ''
    if(list.length === 0){
        recordShowing.insertAdjacentHTML('beforeend',`
            <p>暂无记录</p>
        `)
    }else{
        const rows = list.map(i => `
            <tr data-record-id="${i.id}">
                <td>${i.userName || i.username || ''}</td>
                <td>${i.equipmentName || ''}</td>
                <td>${i.borrowStartTime || ''}</td>
                <td>${i.borrowEndTime || ''}</td>
                <td>${statusToChinese(BORROW_RECORD_STATUS_MAP,i.status)}</td>
                <td>${i.returnStatus || ''}</td>
                <td>${i.createTime || ''}</td>
            </tr>
        `).join('')
        recordShowing.insertAdjacentHTML('beforeend',`
            <table class="record-table">
                <thead>
                    <tr><th>申请人</th><th>设备名称</th><th>借用开始时间</th><th>借用结束时间</th><th>借用状态</th><th>归还状态</th><th>创建时间</th></tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `)
    }
    recordPageAll = res.data.pages || 1
    renderRecordButton()
    checkRecordButton()
    // 点击一行，弹出借用记录详情和待审核操作。
    recordShowing.querySelectorAll('tbody tr[data-record-id]').forEach(row => {
        row.addEventListener('click', async () => {
            const detail = await getBorrowRecordDetail(row.dataset.recordId)
            if(!detail) return
            addBackgroundShadow()
            callAdminRecordDetailWindow(detail)
        })
    })
}

// 检查记录页码按钮，务必在recordPageAll有数值的时候使用
function checkRecordButton(){
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
        case recordPageAll - 2:
            end.style.display = 'none'
            break
        case recordPageAll - 1:
            end.style.display = 'none'
            aft2.style.display = 'none'
            break
        case recordPageAll :
            end.style.display = 'none'
            aft2.style.display = 'none'
            aft1.style.display = 'none'
            break
    }
}

// 给记录页码按钮赋值，务必在recordPageAll有数值和几个按钮已被获取的时候使用
function renderRecordButton(){
    const start = document.getElementById('start')
    const pre2 = document.getElementById('pre-2')
    const pre1 = document.getElementById('pre-1')
    const cur = document.getElementById('cur')
    const aft1 = document.getElementById('aft-1')
    const aft2 = document.getElementById('aft-2')
    const end = document.getElementById('end')
    start.innerText = 1
    pre2.innerText = recordPageNow - 2
    pre1.innerText = recordPageNow - 1
    cur.innerText = recordPageNow
    aft1.innerText = recordPageNow + 1
    aft2.innerText = recordPageNow + 2
    end.innerText = recordPageAll
    cur.style.backgroundColor = 'red'
}

// 给记录页码按钮绑定事件
function attachEventsForRecordPageButton(){
    const start = document.getElementById('start')
    const pre2 = document.getElementById('pre-2')
    const pre1 = document.getElementById('pre-1')
    const cur = document.getElementById('cur')
    const aft1 = document.getElementById('aft-1')
    const aft2 = document.getElementById('aft-2')
    const end = document.getElementById('end')
    start.addEventListener('click', () => {
        defaultRecordQueryData.page = 1;
        recordPageNow = 1
        renderRecordData(defaultRecordQueryData)
    })

    end.addEventListener('click',() => {
        defaultRecordQueryData.page = recordPageAll
        recordPageNow = recordPageAll
        renderRecordData(defaultRecordQueryData)
    })

    pre2.addEventListener('click' ,() => {
        defaultRecordQueryData.page = pre2.innerText
        recordPageNow = recordPageNow - 2
        renderRecordData(defaultRecordQueryData)
    })

    pre1.addEventListener('click' ,() => {
        defaultRecordQueryData.page = pre1.innerText
        recordPageNow = recordPageNow - 1
        renderRecordData(defaultRecordQueryData)
    })

    cur.addEventListener('click' ,() => {
        defaultRecordQueryData.page = cur.innerText
        renderRecordData(defaultRecordQueryData)
    })

    aft1.addEventListener('click' ,() => {
        defaultRecordQueryData.page = aft1.innerText
        recordPageNow = recordPageNow + 1
        renderRecordData(defaultRecordQueryData)
    })

    aft2.addEventListener('click' ,() => {
        defaultRecordQueryData.page = aft2.innerText
        recordPageNow = recordPageNow + 2
        renderRecordData(defaultRecordQueryData)
    })
}

// 呼出管理端借用记录详情弹窗。
function callAdminRecordDetailWindow(detail){
    const recordStatus = chineseToStatus(BORROW_RECORD_STATUS_MAP, detail.status)
    const canReview = recordStatus === 'pending'
    document.body.insertAdjacentHTML('beforeend',`
        <div class="record-detail-window" id="admin-record-detail-window">
            <button class="close-button-plus" id="close-record-detail">X</button>
            <h1>借用记录详情</h1>
            <div class="record-detail-content"></div>
            ${canReview ? `
                <div class="record-detail-buttons">
                    <button class="record-detail-review-pass">审核通过</button>
                    <button class="record-detail-review-reject">审核驳回</button>
                </div>
            ` : ''}
        </div>
    `)
    const detailWindow = document.querySelector('#admin-record-detail-window')
    const detailContent = detailWindow.querySelector('.record-detail-content')
    const fields = [
        ['记录 ID', detail.id],
        ['申请人 ID', detail.userId],
        ['申请人', detail.userName || detail.username],
        ['设备名称', detail.equipmentName],
        ['设备编号', detail.equipmentNo],
        ['设备分类', detail.categoryName],
        ['存放位置', detail.location],
        ['借用开始时间', detail.borrowStartTime],
        ['借用结束时间', detail.borrowEndTime],
        ['借用用途', detail.purpose],
        ['借用状态', statusToChinese(BORROW_RECORD_STATUS_MAP,detail.status)],
        ['审核备注', detail.reviewRemark],
        ['创建时间', detail.createTime],
        ['更新时间', detail.updateTime]
    ]
    fields.forEach(([label, value]) => {
        const row = document.createElement('div')
        row.className = 'detail-grid-row'
        const labelElement = document.createElement('span')
        labelElement.className = 'detail-grid-label'
        labelElement.textContent = label
        const valueElement = document.createElement('span')
        valueElement.className = 'detail-grid-value'
        valueElement.textContent = value === null || value === undefined || value === '' ? '暂无' : String(value)
        row.append(labelElement, valueElement)
        detailContent.appendChild(row)
    })
    document.querySelector('#close-record-detail').addEventListener('click',() => {
        detailWindow.remove()
        document.querySelector('.dim-overlay')?.remove()
    })
    if(canReview){
        detailWindow.querySelector('.record-detail-review-pass').addEventListener('click',async () => {
            if(!confirm(`确定审核通过记录${detail.id}吗？`)) return
            if(await reviewBorrowRecord(detail.id,new BorrowRecordReview({ approved : true }),apiChoose())){
                Toast.success('审核通过成功')
                detailWindow.remove()
                document.querySelector('.dim-overlay')?.remove()
                renderRecordData(defaultRecordQueryData)
            }
        })
        detailWindow.querySelector('.record-detail-review-reject').addEventListener('click',async () => {
            if(!confirm(`确定审核驳回记录${detail.id}吗？`)) return
            if(await reviewBorrowRecord(detail.id,new BorrowRecordReview({ approved : false }),apiChoose())){
                Toast.success('审核驳回成功')
                detailWindow.remove()
                document.querySelector('.dim-overlay')?.remove()
                renderRecordData(defaultRecordQueryData)
            }
        })
    }
}

document.querySelector('#data-showing-button').addEventListener('click',() =>{
    rightSide.innerHTML = ''
    callDataShowing()
    renderData(defaultQueryData)
})

document.querySelector('#admin-equipment-button').addEventListener('click',() =>{
    rightSide.innerHTML = ''
    callCategoryShowing()
})

document.querySelector('#my-record-button').addEventListener('click',() =>{
    rightSide.innerHTML = ''
    callRecordShowing()
})


callDataShowing()
renderData(defaultQueryData)
renderPersonalData()












