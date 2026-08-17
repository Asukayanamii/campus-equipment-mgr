const AdminViewManager = (() => {
    const customViews = new Set()

    function register(view){
        customViews.add(view)
        view.style.display = 'none'
    }

    function hideCustomViews(){
        customViews.forEach(view => { view.style.display = 'none' })
    }

    function show(view){
        hideCustomViews()
        document.querySelector('#right-side').style.display = 'none'
        view.style.display = 'flex'
    }

    // 旧模块仍渲染在 right-side 中；点击旧导航时统一隐藏新增顶层视图。
    document.addEventListener('DOMContentLoaded', () => {
        ['data-showing-button', 'admin-equipment-button', 'my-record-button', 'repair-reports-button']
            .forEach(id => document.getElementById(id)?.addEventListener('click', () => {
                hideCustomViews()
                document.querySelector('#right-side').style.display = 'flex'
            }))
    })

    return { register, show, hideCustomViews }
})()
