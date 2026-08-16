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
const equipmentStatusFilter = document.querySelector('[data-equipment-filter="status"]')
if(equipmentStatusFilter?.tagName === 'INPUT'){ const select=document.createElement('select'); select.dataset.equipmentFilter='status'; select.innerHTML='<option value="">全部</option><option value="available">可用</option><option value="borrowed">已借出</option><option value="repair_pending">待维修</option><option value="repairing">维修中</option><option value="repaired">已维修</option><option value="damaged">已损坏</option><option value="scrapped">已报废</option>'; equipmentStatusFilter.replaceWith(select) }
const recordStatusFilter = document.querySelector('[data-record-filter="status"]')
if(recordStatusFilter?.tagName === 'INPUT'){ const select=document.createElement('select'); select.dataset.recordFilter='status'; select.innerHTML='<option value="">全部</option><option value="pending">待审核</option><option value="approved">已通过</option><option value="rejected">已驳回</option><option value="borrowed">借用中</option><option value="completed">已完成</option>'; recordStatusFilter.replaceWith(select) }

document.addEventListener('click', event => {
    if(event.target.closest('.multi-filter-submit')){
        defaultQueryData = {page:1,size:PAGE_SIZE}
        document.querySelectorAll('[data-equipment-filter]').forEach(el=>{if(el.value) defaultQueryData[el.dataset.equipmentFilter]=el.value})
        pageNow=1
        renderData(defaultQueryData)
    }
    if(event.target.closest('.multi-filter-reset')){
        document.querySelectorAll('[data-equipment-filter]').forEach(el=>el.value='')
        defaultQueryData = {page:1,size:PAGE_SIZE}; pageNow=1; renderData(defaultQueryData)
    }
})

let pageNow = 1;
let pageAll = 1;
let queryDataYouChange  = ''
const identity = 1
let defaultQueryData = new QueryData({
    page : pageNow,
    size : PAGE_SIZE
});

// 记录页独立的分页与搜索状态
let recordType = 'borrow'   // 'borrow' 借用记录 | 'repair' 报修记录
let recordPageNow = 1;
let recordPageAll = 1;
let recordQueryDataYouChange  = ''
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
                <div class="data-card status-${chineseToStatus(EQUIPMENT_STATUS_MAP, i.status || 'unknown')}" data-equipment-id="${i.id}">
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
            card.dataset.equipmentId = i.id
            card.dataset.equipmentStatus = i.status
            card.tabIndex = 0
            card.setAttribute('role', 'button')
            card.setAttribute('aria-label', `查看${i.equipmentName}详情`)
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

// ============ 我的记录 ============

// 召唤我的记录页
function callRecordShowing(){
    const recordView = document.querySelector('#record-view')
    if(recordView){
        recordView.style.display = 'flex'
        document.querySelector('#data-view').style.display = 'none'
        return
    }
    document.querySelector('#data-view').style.display = 'none'
    document.querySelector('.right-side').insertAdjacentHTML('beforeend',`
        <!-- 记录类型切换 -->
        <div id="record-view">
            <div class="record-tabs">
                <button id="record-tab-borrow" class="record-tab-active">借用记录</button>
                <button id="record-tab-repair">报修记录</button>
            </div>
            <!-- 搜索框 -->
            <div class="search-box">
                <label>状态<select data-record-filter="status"><option value="">全部</option><option value="pending">待审核</option><option value="approved">已通过</option><option value="rejected">已驳回</option><option value="borrowed">借用中</option><option value="completed">已完成</option></select></label><label>设备名称<input data-record-filter="equipmentName"></label><label>开始时间<input data-record-filter="startTime" type="datetime-local"></label><label>结束时间<input data-record-filter="endTime" type="datetime-local"></label><button type="button" class="record-filter-submit">查询</button><button type="button" class="record-filter-reset">重置</button>
                <input type="hidden" id="record-search">
                <select hidden id="record-search-way-choose" class="search-way-choose">
                    <option value="no">请选择查询方式（支持联查）</option>
                    <option value="reset">重置搜索</option>
                    <option value="status">借用状态</option>
                    <option value="equipmentName">设备名称</option>
                    <option value="startTime">借用开始时间</option>
                    <option value="endTime">借用结束时间</option>
                </select>
            </div>
            <!-- 记录列表 -->
            <div class="record-showing" id="record-showing">

            </div>
            <!-- 页码选择 -->
            <div class="page-choose-box">
                <button id="record-start"></button>
                <button id="record-pre-2"></button>
                <button id="record-pre-1"></button>
                <button id="record-cur"></button>
                <button id="record-aft-1"></button>
                <button id="record-aft-2"></button>
                <button id="record-end"></button>
            </div>
        </div>`
    )
    attachEventsForRecordPageButton()
    attachEventsForRecordSearchWayChoose()
    attachEventsForRecordTab()
    renderRecordData(defaultRecordQueryData)
}

// 切换记录类型：借用记录 / 报修记录
function switchRecordType(type){
    if(recordType === type) return
    recordType = type
    document.getElementById('record-tab-borrow').classList.toggle('record-tab-active', type === 'borrow')
    document.getElementById('record-tab-repair').classList.toggle('record-tab-active', type === 'repair')
    const searchWayChoose = document.getElementById('record-search-way-choose')
    if(type === 'borrow'){
        searchWayChoose.innerHTML = `
            <option value="no">请选择查询方式（支持联查）</option>
            <option value="reset">重置搜索</option>
            <option value="status">借用状态</option>
            <option value="equipmentName">设备名称</option>
            <option value="startTime">借用开始时间</option>
            <option value="endTime">借用结束时间</option>
        `
        defaultRecordQueryData = new QueryBorrowRecordData({
            page : 1,
            size : PAGE_SIZE
        })
    }else{
        searchWayChoose.innerHTML = `
            <option value="no">请选择查询方式（支持联查）</option>
            <option value="reset">重置搜索</option>
            <option value="status">报修状态</option>
            <option value="equipmentName">设备名称</option>
        `
        defaultRecordQueryData = new QueryRepairReportData({
            page : 1,
            size : PAGE_SIZE
        })
    }
    recordQueryDataYouChange = ''
    document.getElementById('record-search').value = ''
    recordPageNow = 1
    recordPageAll = 1
    renderRecordData(defaultRecordQueryData)
}

// 给记录类型标签绑定事件
function attachEventsForRecordTab(){
    document.getElementById('record-tab-borrow').addEventListener('click',() => switchRecordType('borrow'))
    document.getElementById('record-tab-repair').addEventListener('click',() => switchRecordType('repair'))
}

// 渲染记录列表
async function renderRecordData(QueryData = {}){
    const recordShowing = document.getElementById('record-showing')
    let res
    if(recordType === 'borrow'){
        res = await getBorrowRecordData(QueryData)
    }else{
        res = await getRepairReportData(QueryData)
    }
    if(!res || res.code !== 0 || !res.data) return
    const list = res.data.items || []
    recordShowing.innerHTML = ''
    if(list.length === 0){
        recordShowing.insertAdjacentHTML('beforeend',`
            <p>暂无记录</p>
        `)
    }else if(recordType === 'borrow'){
        const rows = list.map(i => `
            <tr data-record-id="${i.id}">
                <td>${i.equipmentName || ''}</td>
                <td>${i.borrowStartTime || ''}</td>
                <td>${i.borrowEndTime || ''}</td>
                <td>${statusToChinese(BORROW_RECORD_STATUS_MAP,i.status)}</td>
                <td>${i.createTime || ''}</td>
            </tr>
        `).join('')
        recordShowing.insertAdjacentHTML('beforeend',`
            <table class="record-table">
                <thead>
                    <tr><th>设备名称</th><th>借用开始时间</th><th>借用结束时间</th><th>状态</th><th>创建时间</th></tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `)
    }else{
        const rows = list.map(i => `
            <tr data-record-id="${i.id}">
                <td>${i.equipmentName || ''}</td>
                <td>${statusToChinese(REPAIR_REPORT_STATUS_MAP,i.status)}</td>
                <td>${i.createTime || ''}</td>
            </tr>
        `).join('')
        recordShowing.insertAdjacentHTML('beforeend',`
            <table class="record-table">
                <thead>
                    <tr><th>设备名称</th><th>状态</th><th>创建时间</th></tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `)
    }
    recordPageAll = res.data.pages || 1
    renderRecordButton()
    checkRecordButton()
    // 点击一行，弹记录详情
    recordShowing.querySelectorAll('tbody tr[data-record-id]').forEach(row => {
        row.addEventListener('click', async () => {
            let detail
            if(recordType === 'borrow'){
                detail = await getBorrowRecordDetail(row.dataset.recordId)
            }else{
                detail = await getRepairReportDetail(row.dataset.recordId)
            }
            if(!detail) return
            document.body.insertAdjacentHTML('beforeend',`
                <div class="dim-overlay"></div>
            `)
            callRecordDetailWindow(detail)
        })
    })
}

// 检查记录页码按钮，务必在recordPageAll有数值的时候使用
function checkRecordButton(){
    const start = document.getElementById('record-start')
    const pre2 = document.getElementById('record-pre-2')
    const pre1 = document.getElementById('record-pre-1')
    const cur = document.getElementById('record-cur')
    const aft1 = document.getElementById('record-aft-1')
    const aft2 = document.getElementById('record-aft-2')
    const end = document.getElementById('record-end')
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
    const start = document.getElementById('record-start')
    const pre2 = document.getElementById('record-pre-2')
    const pre1 = document.getElementById('record-pre-1')
    const cur = document.getElementById('record-cur')
    const aft1 = document.getElementById('record-aft-1')
    const aft2 = document.getElementById('record-aft-2')
    const end = document.getElementById('record-end')
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
    const start = document.getElementById('record-start')
    const pre2 = document.getElementById('record-pre-2')
    const pre1 = document.getElementById('record-pre-1')
    const cur = document.getElementById('record-cur')
    const aft1 = document.getElementById('record-aft-1')
    const aft2 = document.getElementById('record-aft-2')
    const end = document.getElementById('record-end')
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

// 给记录搜索下拉框绑定事件
function attachEventsForRecordSearchWayChoose(){
    const search = document.getElementById('record-search')
    search.addEventListener('keydown',(e) =>{
        if(e.key === 'Enter'){
            if(!recordQueryDataYouChange){
                Toast.warning('请选择搜索类型')
                return
            }
            defaultRecordQueryData[recordQueryDataYouChange]  = e.target.value
            defaultRecordQueryData.page = 1
            recordPageNow = 1;
            renderRecordData(defaultRecordQueryData)
        }
    })
    const searchWayChoose = document.getElementById('record-search-way-choose')
    searchWayChoose.addEventListener('change',(e) =>{
        switch (e.target.value){
            case 'no':
                break
            case 'reset':
                if(recordType === 'borrow'){
                    defaultRecordQueryData = new QueryBorrowRecordData({
                        page : recordPageNow,
                        size : PAGE_SIZE
                    })
                }else{
                    defaultRecordQueryData = new QueryRepairReportData({
                        page : recordPageNow,
                        size : PAGE_SIZE
                    })
                }
                recordQueryDataYouChange = ''
                search.value = ''
                searchWayChoose.querySelectorAll('option').forEach(opt => {
                    opt.textContent = opt.textContent.replace('（已指定）','')
                })
                renderRecordData(defaultRecordQueryData)
                break
            case 'status':
                recordQueryDataYouChange  = 'status'
                searchWayChoose.querySelector('option[value="status"]').textContent = (recordType === 'borrow' ? '借用状态' : '报修状态') + '（已指定）'
                break
            case 'equipmentName':
                recordQueryDataYouChange  = 'equipmentName'
                searchWayChoose.querySelector('option[value="equipmentName"]').textContent = '设备名称（已指定）'
                break
            case 'startTime':
                recordQueryDataYouChange  = 'startTime'
                searchWayChoose.querySelector('option[value="startTime"]').textContent = '借用开始时间（已指定）'
                break
            case 'endTime':
                recordQueryDataYouChange  = 'endTime'
                searchWayChoose.querySelector('option[value="endTime"]').textContent = '借用结束时间（已指定）'
                break
        }
    })
}

// 呼出记录详情弹窗
function callRecordDetailWindow(detail){
    const row = (label, value) => `<div class="detail-grid-row"><span class="detail-grid-label">${label}</span><span class="detail-grid-value">${value ?? ''}</span></div>`
    let content
    let title
    if(recordType === 'borrow'){
        title = '借用记录详情'
        content = `
            ${row('记录ID',detail.id)}${row('设备名称',detail.equipmentName)}${row('设备编号',detail.equipmentNo)}${row('设备分类',detail.categoryName)}${row('设备品牌',detail.brand)}${row('存放位置',detail.location)}${row('借用开始时间',detail.borrowStartTime)}${row('借用结束时间',detail.borrowEndTime)}${row('借用用途',detail.purpose)}${row('审核备注',detail.reviewRemark)}${row('借用状态',statusToChinese(BORROW_RECORD_STATUS_MAP,detail.status))}${row('创建时间',detail.createTime)}${row('更新时间',detail.updateTime)}
        `
    }else{
        title = '报修记录详情'
        content = `
            ${row('记录ID',detail.id)}${row('设备名称',detail.equipmentName)}${row('设备编号',detail.equipmentNo)}${row('设备分类',detail.categoryName)}${row('损坏说明',detail.damageDescription)}${row('管理员确认状态',detail.confirmStatus)}${row('管理员确认备注',detail.confirmRemark)}${row('报修状态',statusToChinese(REPAIR_REPORT_STATUS_MAP,detail.status))}${row('维修工单状态',statusToChinese(REPAIR_ORDER_STATUS_MAP,detail.repairStatus))}${row('故障原因',detail.faultCause)}${row('维修过程',detail.repairProcess)}${row('维修结果',detail.repairResult)}${row('创建时间',detail.createTime)}${row('更新时间',detail.updateTime)}
        `
    }
    document.body.insertAdjacentHTML('beforeend',`
        <div class="record-detail-window">
            <button class="close-button-plus" id="close-record-detail">X</button>
            <h1>${title}</h1>
            <div class="record-detail-content">${content}</div>
        </div>
    `)
    document.querySelector('#close-record-detail').addEventListener('click',() => {
        document.querySelector('.record-detail-window').remove()
        document.querySelector('.dim-overlay')?.remove()
    })
    document.dispatchEvent(new CustomEvent('record-detail-opened', {
        detail: { recordType, record: detail }
    }))
}

// 记录视图首次进入时才创建，因此切回设备列表时需要兼容它尚未挂载。
function showEquipmentView(){
    const recordView = document.querySelector('#record-view')
    const dataView = document.querySelector('#data-view')
    if(recordView) recordView.style.display = 'none'
    if(dataView) dataView.style.display = 'flex'
}

document.addEventListener('click', event => {
    if(event.target.closest('.record-filter-submit')){
        defaultRecordQueryData = { page: 1, size: PAGE_SIZE }
        document.querySelectorAll('[data-record-filter]').forEach(el => { if(el.value) defaultRecordQueryData[el.dataset.recordFilter] = el.value })
        recordPageNow = 1
        renderRecordData(defaultRecordQueryData)
    }
    if(event.target.closest('.record-filter-reset')){
        document.querySelectorAll('[data-record-filter]').forEach(el => { el.value = '' })
        defaultRecordQueryData = { page: 1, size: PAGE_SIZE }
        recordPageNow = 1
        renderRecordData(defaultRecordQueryData)
    }
})

// 导航：数据展示 / 我的记录
document.querySelector('#data-showing-button').addEventListener('click', showEquipmentView)

document.querySelector('#my-record-button').addEventListener('click',() => {
    callRecordShowing()
})

// 借用模块提交成功后，通过事件刷新记录页，避免跨模块直接依赖内部函数。
document.addEventListener('borrow-record-created', () => {
    if(recordType !== 'borrow'){
        switchRecordType('borrow')
        return
    }
    recordPageNow = 1
    defaultRecordQueryData = new QueryBorrowRecordData({ page: 1, size: PAGE_SIZE })
    renderRecordData(defaultRecordQueryData)
})

document.addEventListener('borrow-returned', event => {
    const nextType = event.detail.damaged ? 'repair' : 'borrow'
    if(recordType !== nextType){
        switchRecordType(nextType)
        return
    }
    recordPageNow = 1
    defaultRecordQueryData = nextType === 'repair'
        ? new QueryRepairReportData({ page: 1, size: PAGE_SIZE })
        : new QueryBorrowRecordData({ page: 1, size: PAGE_SIZE })
    renderRecordData(defaultRecordQueryData)
})

document.addEventListener('profile-updated', renderPersonalData)

renderData(defaultQueryData)
renderPersonalData()
populateEquipmentCategorySelect(document.querySelector('select[data-equipment-filter="categoryId"]'))










