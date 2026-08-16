(function(){
    document.addEventListener('admin-category-rendered', event => {
        const { bar, categoryId } = event.detail
        const actions = bar.querySelector('.category-actions')
        if(actions.querySelector('.category-edit')) return
        const categoryName = bar.querySelector('.category-name').textContent
        const edit = document.createElement('button');edit.type='button';edit.className='category-edit';edit.title='编辑分类';edit.textContent='编辑'
        const remove = document.createElement('button');remove.type='button';remove.className='category-delete';remove.title='删除分类';remove.textContent='删除'
        edit.setAttribute('aria-label', `编辑${categoryName}分类`)
        remove.setAttribute('aria-label', `删除${categoryName}分类`)
        edit.addEventListener('click',e=>{e.stopPropagation();openEditor(categoryId)})
        remove.addEventListener('click',e=>{e.stopPropagation();deleteCategory(categoryId,bar.querySelector('.category-name').textContent)})
        actions.prepend(edit,remove)
    })
    async function getCategory(id){return adminBusinessRequest(`/admin/equipment-category/${id}`)}
    async function openEditor(id){const category=await getCategory(id);if(!category)return;const dialog=document.createElement('dialog');dialog.className='operation-dialog operation-small-dialog';dialog.innerHTML='<header><div><p>设备分类</p><h2>编辑分类</h2></div><button type="button">×</button></header><form><label>分类名称<input name="categoryName" maxlength="50" required></label><label>排序值<input name="sort" type="number" min="0" required></label><button type="submit">保存</button></form>';dialog.querySelector('[name=categoryName]').value=category.categoryName;dialog.querySelector('[name=sort]').value=category.sort||0;dialog.querySelector('form').addEventListener('submit',async e=>{e.preventDefault();const ok=await adminBusinessRequest(`/admin/equipment-category/${id}`,{method:'PUT',body:{categoryName:e.currentTarget.elements.categoryName.value.trim(),sort:Number(e.currentTarget.elements.sort.value)}});if(ok){Toast.success('分类已更新');invalidateEquipmentCategoryMap();populateEquipmentCategorySelect(document.querySelector('select[data-category-filter="id"]'));dialog.close();renderCategory(defaultCategoryQueryData)}});document.body.appendChild(dialog);dialog.querySelector('header button').addEventListener('click',()=>dialog.close());dialog.addEventListener('close',()=>dialog.remove());dialog.showModal()}
    async function deleteCategory(id,name){if(!confirm(`确认删除分类“${name}”吗？分类下存在设备时服务端可能拒绝删除。`))return;const ok=await adminBusinessRequest(`/admin/equipment-category/${id}`,{method:'DELETE'});if(ok){Toast.success('分类已删除');invalidateEquipmentCategoryMap();populateEquipmentCategorySelect(document.querySelector('select[data-category-filter="id"]'));renderCategory(defaultCategoryQueryData)}}
})()
