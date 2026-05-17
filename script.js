/* ===== 肴柒蟹 - 交互脚本 ===== */

document.addEventListener('DOMContentLoaded', () => {

  // =============================================
  // 1. 导航栏滚动效果
  // =============================================
  const navbar = document.getElementById('navbar');
  const backToTop = document.getElementById('backToTop');

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;

    // 导航栏
    if (scrollY > 50) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }

    // 回到顶部按钮
    if (scrollY > 300) {
      backToTop.classList.add('visible');
    } else {
      backToTop.classList.remove('visible');
    }
  });

  backToTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  // =============================================
  // 2. 移动端菜单
  // =============================================
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const mobileMenu = document.getElementById('mobileMenu');

  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener('click', () => {
      mobileMenu.classList.toggle('hidden');
      const icon = mobileMenuBtn.querySelector('i');
      if (icon) {
        icon.classList.toggle('bi-list');
        icon.classList.toggle('bi-x');
      }
    });

    // 点击菜单项后关闭
    mobileMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        mobileMenu.classList.add('hidden');
        const icon = mobileMenuBtn.querySelector('i');
        if (icon) {
          icon.classList.add('bi-list');
          icon.classList.remove('bi-x');
        }
      });
    });
  }

  // =============================================
  // 3. 模式切换 (已移除 - 改为多页面导航)
  // =============================================
  // 导航栏 active 状态已通过各页面 HTML 中直接设置 text-tech-blue/text-food-red/text-harvest-gold/text-water-green 实现

  // =============================================
  // 4. 滚动渐入动画 (Intersection Observer)
  // =============================================
  const revealElements = document.querySelectorAll('[data-reveal]');

  if (revealElements.length > 0 && 'IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          // 可选：只触发一次
          // revealObserver.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    revealElements.forEach(el => revealObserver.observe(el));
  } else {
    // 降级：直接显示
    revealElements.forEach(el => el.classList.add('revealed'));
  }

  // =============================================
  // 5. 混合模式滚动视差
  // =============================================
  const heroImgPlaceholder = document.querySelector('.hero-img-placeholder');
  if (heroImgPlaceholder) {
    window.addEventListener('scroll', () => {
      const scrollY = window.scrollY;
      const speed = 0.15;
      if (scrollY < window.innerHeight) {
        heroImgPlaceholder.style.transform = `translateY(${scrollY * speed}px)`;
      }
    });
  }

  // =============================================
  // 6. 食材换算器
  // =============================================
  const calcBtn = document.getElementById('calcBtn');
  const ingredientWeight = document.getElementById('ingredientWeight');
  const servingCount = document.getElementById('servingCount');
  const calcResult = document.getElementById('calcResult');

  if (calcBtn && calcResult) {
    calcBtn.addEventListener('click', () => {
      const weight = parseFloat(ingredientWeight?.value || 500);
      const servings = parseFloat(servingCount?.value || 3);

      if (isNaN(weight) || isNaN(servings) || weight <= 0 || servings <= 0) {
        calcResult.innerHTML = '请输入有效的食材重量和人数';
        calcResult.classList.remove('hidden');
        calcResult.classList.add('text-red-600');
        return;
      }

      const ratio = weight / 500;
      const oil = Math.round(30 * ratio);
      const salt = Math.round(5 * ratio);
      const soy = Math.round(10 * ratio);
      const ginger = Math.round(15 * ratio);
      const garlic = Math.round(20 * ratio);
      const chili = Math.round(8 * ratio);

      calcResult.innerHTML = `
        <p class="font-medium text-gray-700">建议配料（${Math.round(servings)}人份）：</p>
        <p class="mt-1">食用油 ${oil}ml · 盐 ${salt}g · 生抽 ${soy}ml · 姜 ${ginger}g · 蒜 ${garlic}g · 辣椒 ${chili}g</p>
      `;
      calcResult.classList.remove('hidden');
      calcResult.classList.remove('text-red-600');
    });
  }

  // =============================================
  // 7. 烹饪计时器
  // =============================================
  const timerDisplay = document.getElementById('timerDisplay');
  const timerStartBtn = document.getElementById('timerStartBtn');
  const timerResetBtn = document.getElementById('timerResetBtn');
  const quickTimers = document.querySelectorAll('.quick-timer');

  let timerSeconds = 0;
  let timerInterval = null;
  let isTimerRunning = false;

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  const updateTimerDisplay = () => {
    if (timerDisplay) {
      timerDisplay.textContent = formatTime(timerSeconds);
    }
  };

  const stopTimer = () => {
    if (timerInterval) {
      clearInterval(timerInterval);
      timerInterval = null;
    }
    isTimerRunning = false;
    if (timerStartBtn) {
      timerStartBtn.innerHTML = '<i class="bi bi-play-fill mr-1"></i> 开始';
      timerStartBtn.classList.remove('bg-yellow-500', 'hover:bg-yellow-600');
      timerStartBtn.classList.add('bg-food-red', 'hover:bg-food-red-dark');
    }
  };

  const startTimer = () => {
    if (isTimerRunning) {
      stopTimer();
      return;
    }

    if (timerSeconds <= 0) {
      return;
    }

    isTimerRunning = true;
    if (timerStartBtn) {
      timerStartBtn.innerHTML = '<i class="bi bi-pause-fill mr-1"></i> 暂停';
      timerStartBtn.classList.remove('bg-food-red', 'hover:bg-food-red-dark');
      timerStartBtn.classList.add('bg-yellow-500', 'hover:bg-yellow-600');
    }

    timerInterval = setInterval(() => {
      if (timerSeconds <= 0) {
        stopTimer();
        timerSeconds = 0;
        updateTimerDisplay();
        // 倒计时结束提示
        if (timerDisplay) {
          timerDisplay.classList.add('text-food-red');
          setTimeout(() => timerDisplay?.classList.remove('text-food-red'), 2000);
        }
        return;
      }
      timerSeconds--;
      updateTimerDisplay();
    }, 1000);
  };

  if (timerStartBtn) {
    timerStartBtn.addEventListener('click', startTimer);
  }

  if (timerResetBtn) {
    timerResetBtn.addEventListener('click', () => {
      stopTimer();
      timerSeconds = 0;
      updateTimerDisplay();
    });
  }

  quickTimers.forEach(btn => {
    btn.addEventListener('click', () => {
      const time = parseInt(btn.dataset.time, 10);
      if (isNaN(time)) return;
      stopTimer();
      timerSeconds = time;
      updateTimerDisplay();
    });
  });

  // =============================================
  // 8. 行情图表 (Chart.js)
  // =============================================
  const priceChartCanvas = document.getElementById('priceChart');
  if (priceChartCanvas && typeof Chart !== 'undefined') {
    const ctx = priceChartCanvas.getContext('2d');

    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, 'rgba(22, 93, 255, 0.15)');
    gradient.addColorStop(1, 'rgba(22, 93, 255, 0)');

    new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['2024年1月', '2024年5月', '2024年9月', '2025年1月', '2025年5月', '2025年9月', '2026年1月', '2026年5月'],
        datasets: [
          {
            label: '小龙虾 (6-8钱) ¥/斤',
            data: [22, 28, 20, 24, 30, 22, 26, 32],
            borderColor: '#FF4D4F',
            backgroundColor: gradient,
            fill: true,
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6,
            pointBackgroundColor: '#FF4D4F',
            borderWidth: 2,
          },
          {
            label: '大闸蟹 (3两公) ¥/斤',
            data: [55, 45, 70, 58, 48, 75, 60, 50],
            borderColor: '#165DFF',
            backgroundColor: 'transparent',
            fill: false,
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6,
            pointBackgroundColor: '#165DFF',
            borderWidth: 2,
            borderDash: [5, 5],
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              usePointStyle: true,
              padding: 16,
              font: { size: 12 },
            },
          },
          tooltip: {
            backgroundColor: 'rgba(0,0,0,0.8)',
            padding: 12,
            cornerRadius: 8,
          },
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { font: { size: 11 } },
          },
          y: {
            beginAtZero: false,
            grid: { color: 'rgba(0,0,0,0.05)' },
            ticks: {
              font: { size: 11 },
              callback: (value) => '¥' + value,
            },
          },
        },
        interaction: {
          intersect: false,
          mode: 'index',
        },
      },
    });
  }

  // =============================================
  // 9. 平滑滚动 (兼容不支持 scroll-behavior 的浏览器)
  // =============================================
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', (e) => {
      const href = anchor.getAttribute('href');
      if (!href || href === '#') return;

      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        const navHeight = navbar.offsetHeight;
        const targetPosition = target.getBoundingClientRect().top + window.scrollY - navHeight;
        window.scrollTo({ top: targetPosition, behavior: 'smooth' });
      }
    });
  });

  // =============================================
  // 10. 菜谱卡片悬停增强
  // =============================================
  document.querySelectorAll('.recipe-card').forEach(card => {
    card.addEventListener('mouseenter', () => {
      const icon = card.querySelector('.text-6xl');
      if (icon) {
        icon.style.transform = 'scale(1.15) rotate(-5deg)';
        icon.style.transition = 'transform 0.4s ease';
      }
    });
    card.addEventListener('mouseleave', () => {
      const icon = card.querySelector('.text-6xl');
      if (icon) {
        icon.style.transform = 'scale(1) rotate(0deg)';
      }
    });
  });

  // =============================================
  // 11. 键盘快捷键
  // =============================================
  document.addEventListener('keydown', (e) => {
    // ESC 关闭移动端菜单
    if (e.key === 'Escape') {
      if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
        mobileMenu.classList.add('hidden');
        const icon = mobileMenuBtn?.querySelector('i');
        if (icon) {
          icon.classList.add('bi-list');
          icon.classList.remove('bi-x');
        }
      }
    }
  });

  console.log('🦀 肴柒蟹 (YaoQiXie) 已加载完成');
  console.log('📦 多页面导航模式 | 首页 · 功能 · 行情 · 菜谱 · 社区');
});
