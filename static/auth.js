// 认证相关功能

// 登出功能
function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('username');
    // 调用服务器登出接口清除session
    fetch('/logout', {
        method: 'GET',
        redirect: 'follow'
    }).then(() => {
        window.location.href = '/login';
    });
}

// 获取当前用户名
function getUsername() {
    return localStorage.getItem('username') || '用户';
}

// 更新导航栏显示用户信息
function updateNavbarUser() {
    const username = getUsername();
    const navbarMenu = document.querySelector('.navbar-menu');

    if (navbarMenu) {
        // 查找是否已有用户信息元素
        let userInfo = document.getElementById('navUserInfo');
        if (!userInfo) {
            // 创建用户信息元素
            userInfo = document.createElement('div');
            userInfo.id = 'navUserInfo';
            userInfo.style.cssText = `
                display: flex;
                gap: 8px;
                align-items: center;
            `;

            // 添加用户名显示
            const userSpan = document.createElement('span');
            userSpan.className = 'navbar-item';
            userSpan.innerHTML = `<span class="icon">👤</span>${username}`;
            userSpan.style.cursor = 'default';

            // 添加登出按钮
            const logoutBtn = document.createElement('a');
            logoutBtn.href = '#';
            logoutBtn.className = 'navbar-item';
            logoutBtn.innerHTML = '<span class="icon">🚪</span>登出';
            logoutBtn.onclick = function(e) {
                e.preventDefault();
                if (confirm('确定要登出吗？')) {
                    logout();
                }
            };

            userInfo.appendChild(userSpan);
            userInfo.appendChild(logoutBtn);

            // 插入到菜单末尾
            navbarMenu.appendChild(userInfo);
        } else {
            // 更新用户名
            const userSpan = userInfo.querySelector('.navbar-item:first-child');
            if (userSpan) {
                userSpan.innerHTML = `<span class="icon">👤</span>${username}`;
            }
        }
    }
}

// 页面加载时更新导航栏用户信息
document.addEventListener('DOMContentLoaded', function() {
    // 仅在非登录/注册页面更新导航栏
    const currentPath = window.location.pathname;
    if (currentPath !== '/login' && currentPath !== '/register') {
        updateNavbarUser();
    }
});
