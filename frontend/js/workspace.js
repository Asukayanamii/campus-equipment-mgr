(() => {
    const body = document.body
    const menuButton = document.querySelector('.mobile-menu-button')
    const backdrop = document.querySelector('.nav-backdrop')
    const nav = document.getElementById('nav')
    const navButtons = [...document.querySelectorAll('.nav-options button')]

    function setMenu(open) {
        body.classList.toggle('nav-open', open)
        menuButton?.setAttribute('aria-expanded', String(open))
        menuButton?.setAttribute('aria-label', open ? '关闭导航' : '打开导航')
    }

    function setActive(button) {
        navButtons.forEach(item => item.removeAttribute('aria-current'))
        button?.setAttribute('aria-current', 'page')
    }

    setActive(navButtons[0])
    menuButton?.addEventListener('click', () => setMenu(!body.classList.contains('nav-open')))
    backdrop?.addEventListener('click', () => setMenu(false))
    nav?.addEventListener('click', event => {
        const button = event.target.closest('.nav-options button')
        if (!button) return
        setActive(button)
        if (window.matchMedia('(max-width: 760px)').matches) setMenu(false)
    })
    window.addEventListener('keydown', event => {
        if (event.key === 'Escape') setMenu(false)
    })
    window.addEventListener('resize', () => {
        if (window.innerWidth > 760) setMenu(false)
    })
})()
