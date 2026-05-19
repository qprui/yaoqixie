/* ===== 肴柒蟹 - 交互脚本 ===== */

// =============================================
// API 配置与认证工具
// =============================================
// 使用阿里云服务器 IP（部署后修改此处）
const API_BASE_URL = "http://182.92.240.192";

const Api = {
  async request(endpoint, options = {}) {
    const token = localStorage.getItem("token");
    const headers = {
      "Content-Type": "application/json",
      ...options.headers,
    };
    if (token) {
      headers["Authorization"] = "Bearer " + token;
    }

    try {
      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
      });
      const data = await res.json();
      return data;
    } catch (err) {
      console.error("API 请求失败:", err);
      return { success: false, message: "网络错误，无法连接到服务器" };
    }
  },

  // 认证相关
  login(username, password) {
    return this.request("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
  },

  register(data) {
    return this.request("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  getMe() {
    return this.request("/api/user/me");
  },

  // 仪表盘
  getDashboard() {
    return this.request("/api/dashboard");
  },

  // 塘口
  getPonds() {
    return this.request("/api/ponds");
  },

  getPond(pondId) {
    return this.request(`/api/ponds/${pondId}`);
  },

  createPond(data) {
    return this.request("/api/ponds", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  updatePond(pondId, data) {
    return this.request(`/api/ponds/${pondId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  deletePond(pondId) {
    return this.request(`/api/ponds/${pondId}`, {
      method: "DELETE",
    });
  },

  // 环境数据
  addEnvData(pondId, data) {
    return this.request(`/api/ponds/${pondId}/env`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  // 养殖日志
  addFarmingLog(pondId, data) {
    return this.request(`/api/ponds/${pondId}/logs`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  },
};

// 认证状态管理
const Auth = {
  isLoggedIn() {
    return !!localStorage.getItem("token");
  },

  getToken() {
    return localStorage.getItem("token");
  },

  getUser() {
    const raw = localStorage.getItem("user");
    if (!raw) return null;
    try {
      return JSON.parse(raw);
    } catch {
      return null;
    }
  },

  login(token, user) {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(user));
  },

  logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "index.html";
  },

  // 检查登录状态，未登录则跳转
  requireAuth() {
    if (!this.isLoggedIn()) {
      window.location.href =
        "login.html?redirect=" + encodeURIComponent(window.location.pathname);
      return false;
    }
    return true;
  },

  // 更新导航栏登录状态
  updateNavbar() {
    const loginLink = document.getElementById("loginLink");
    const registerBtn = document.getElementById("registerBtn");
    const userInfo = document.getElementById("userInfo");
    const userName = document.getElementById("userName");

    if (this.isLoggedIn() && userInfo && userName) {
      const user = this.getUser();
      userInfo.classList.remove("hidden");
      userName.textContent = user?.username || "用户";
      if (loginLink) loginLink.classList.add("hidden");
      if (registerBtn) registerBtn.classList.add("hidden");
    } else {
      if (userInfo) userInfo.classList.add("hidden");
      if (loginLink) loginLink.classList.remove("hidden");
      if (registerBtn) registerBtn.classList.remove("hidden");
    }
  },
};

document.addEventListener("DOMContentLoaded", () => {
  // 更新导航栏登录状态
  Auth.updateNavbar();

  // =============================================
  // 1. 导航栏滚动效果
  // =============================================
  const navbar = document.getElementById("navbar");
  const backToTop = document.getElementById("backToTop");

  window.addEventListener("scroll", () => {
    const scrollY = window.scrollY;

    // 导航栏
    if (scrollY > 50) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }

    // 回到顶部按钮
    if (scrollY > 300) {
      backToTop.classList.add("visible");
    } else {
      backToTop.classList.remove("visible");
    }
  });

  backToTop.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  // =============================================
  // 2. 移动端菜单
  // =============================================
  const mobileMenuBtn = document.getElementById("mobileMenuBtn");
  const mobileMenu = document.getElementById("mobileMenu");

  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener("click", () => {
      mobileMenu.classList.toggle("hidden");
      const icon = mobileMenuBtn.querySelector("i");
      if (icon) {
        icon.classList.toggle("bi-list");
        icon.classList.toggle("bi-x");
      }
    });

    // 点击菜单项后关闭
    mobileMenu.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        mobileMenu.classList.add("hidden");
        const icon = mobileMenuBtn.querySelector("i");
        if (icon) {
          icon.classList.add("bi-list");
          icon.classList.remove("bi-x");
        }
      });
    });
  }

  // =============================================
  // 3. 模式切换 (已移除 - 改为多页面导航)
  // =============================================

  // =============================================
  // 4. 菜谱分类筛选 (recipes.html)
  // =============================================
  const filterBtns = document.querySelectorAll(".filter-btn");
  const recipeSections = document.querySelectorAll(".recipe-detail");

  if (filterBtns.length > 0 && recipeSections.length > 0) {
    // 显示所有菜谱
    const showAllRecipes = () => {
      recipeSections.forEach((section) => {
        section.style.display = "block";
      });
    };

    // 根据分类筛选
    const filterRecipes = (category) => {
      recipeSections.forEach((section) => {
        const cats = section.dataset.category || "";
        if (cats.split(" ").includes(category)) {
          section.style.display = "block";
        } else {
          section.style.display = "none";
        }
      });
    };

    // 更新筛选按钮状态
    const updateFilterBtn = (activeBtn) => {
      filterBtns.forEach((btn) => {
        btn.classList.remove("bg-tech-blue", "text-white");
        btn.classList.add(
          "bg-white",
          "text-gray-600",
          "border",
          "border-gray-200",
          "hover:border-food-red",
          "hover:text-food-red",
        );
      });
      activeBtn.classList.remove(
        "bg-white",
        "text-gray-600",
        "border",
        "border-gray-200",
        "hover:border-food-red",
        "hover:text-food-red",
      );
      activeBtn.classList.add("bg-tech-blue", "text-white");
    };

    filterBtns.forEach((btn) => {
      btn.addEventListener("click", () => {
        const filter = btn.dataset.filter;
        updateFilterBtn(btn);

        if (!filter || filter === "all") {
          showAllRecipes();
        } else {
          filterRecipes(filter);
        }
      });
    });
  }
  // 导航栏 active 状态已通过各页面 HTML 中直接设置 text-tech-blue/text-food-red/text-harvest-gold/text-water-green 实现

  // =============================================
  // 5. 滚动渐入动画 (Intersection Observer)
  // =============================================
  const revealElements = document.querySelectorAll("[data-reveal]");

  if (revealElements.length > 0 && "IntersectionObserver" in window) {
    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("revealed");
            // 可选：只触发一次
            // revealObserver.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px",
      },
    );

    revealElements.forEach((el) => revealObserver.observe(el));
  } else {
    // 降级：直接显示
    revealElements.forEach((el) => el.classList.add("revealed"));
  }

  // =============================================
  // 5. 混合模式滚动视差
  // =============================================
  const heroImgPlaceholder = document.querySelector(".hero-img-placeholder");
  if (heroImgPlaceholder) {
    window.addEventListener("scroll", () => {
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
  const calcBtn = document.getElementById("calcBtn");
  const ingredientWeight = document.getElementById("ingredientWeight");
  const servingCount = document.getElementById("servingCount");
  const calcResult = document.getElementById("calcResult");

  if (calcBtn && calcResult) {
    calcBtn.addEventListener("click", () => {
      const weight = parseFloat(ingredientWeight?.value || 500);
      const servings = parseFloat(servingCount?.value || 3);

      if (isNaN(weight) || isNaN(servings) || weight <= 0 || servings <= 0) {
        calcResult.innerHTML = "请输入有效的食材重量和人数";
        calcResult.classList.remove("hidden");
        calcResult.classList.add("text-red-600");
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
      calcResult.classList.remove("hidden");
      calcResult.classList.remove("text-red-600");
    });
  }

  // =============================================
  // 7. 烹饪计时器
  // =============================================
  const timerDisplay = document.getElementById("timerDisplay");
  const timerStartBtn = document.getElementById("timerStartBtn");
  const timerResetBtn = document.getElementById("timerResetBtn");
  const quickTimers = document.querySelectorAll(".quick-timer");

  let timerSeconds = 0;
  let timerInterval = null;
  let isTimerRunning = false;

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60)
      .toString()
      .padStart(2, "0");
    const s = (seconds % 60).toString().padStart(2, "0");
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
      timerStartBtn.classList.remove("bg-yellow-500", "hover:bg-yellow-600");
      timerStartBtn.classList.add("bg-food-red", "hover:bg-food-red-dark");
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
      timerStartBtn.classList.remove("bg-food-red", "hover:bg-food-red-dark");
      timerStartBtn.classList.add("bg-yellow-500", "hover:bg-yellow-600");
    }

    timerInterval = setInterval(() => {
      if (timerSeconds <= 0) {
        stopTimer();
        timerSeconds = 0;
        updateTimerDisplay();
        // 倒计时结束提示
        if (timerDisplay) {
          timerDisplay.classList.add("text-food-red");
          setTimeout(
            () => timerDisplay?.classList.remove("text-food-red"),
            2000,
          );
        }
        return;
      }
      timerSeconds--;
      updateTimerDisplay();
    }, 1000);
  };

  if (timerStartBtn) {
    timerStartBtn.addEventListener("click", startTimer);
  }

  if (timerResetBtn) {
    timerResetBtn.addEventListener("click", () => {
      stopTimer();
      timerSeconds = 0;
      updateTimerDisplay();
    });
  }

  quickTimers.forEach((btn) => {
    btn.addEventListener("click", () => {
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
  const priceChartCanvas = document.getElementById("priceChart");
  if (priceChartCanvas && typeof Chart !== "undefined") {
    const ctx = priceChartCanvas.getContext("2d");

    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
    gradient.addColorStop(0, "rgba(22, 93, 255, 0.15)");
    gradient.addColorStop(1, "rgba(22, 93, 255, 0)");

    new Chart(ctx, {
      type: "line",
      data: {
        labels: [
          "2024年1月",
          "2024年5月",
          "2024年9月",
          "2025年1月",
          "2025年5月",
          "2025年9月",
          "2026年1月",
          "2026年5月",
        ],
        datasets: [
          {
            label: "小龙虾 (6-8钱) ¥/斤",
            data: [22, 28, 20, 24, 30, 22, 26, 32],
            borderColor: "#FF4D4F",
            backgroundColor: gradient,
            fill: true,
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6,
            pointBackgroundColor: "#FF4D4F",
            borderWidth: 2,
          },
          {
            label: "大闸蟹 (3两公) ¥/斤",
            data: [55, 45, 70, 58, 48, 75, 60, 50],
            borderColor: "#165DFF",
            backgroundColor: "transparent",
            fill: false,
            tension: 0.3,
            pointRadius: 4,
            pointHoverRadius: 6,
            pointBackgroundColor: "#165DFF",
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
            position: "bottom",
            labels: {
              usePointStyle: true,
              padding: 16,
              font: { size: 12 },
            },
          },
          tooltip: {
            backgroundColor: "rgba(0,0,0,0.8)",
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
            grid: { color: "rgba(0,0,0,0.05)" },
            ticks: {
              font: { size: 11 },
              callback: (value) => "¥" + value,
            },
          },
        },
        interaction: {
          intersect: false,
          mode: "index",
        },
      },
    });
  }

  // =============================================
  // 9. 平滑滚动 (兼容不支持 scroll-behavior 的浏览器)
  // =============================================
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (e) => {
      const href = anchor.getAttribute("href");
      if (!href || href === "#") return;

      const target = document.querySelector(href);
      if (target) {
        e.preventDefault();
        const navHeight = navbar.offsetHeight;
        const targetPosition =
          target.getBoundingClientRect().top + window.scrollY - navHeight;
        window.scrollTo({ top: targetPosition, behavior: "smooth" });
      }
    });
  });

  // =============================================
  // 10. 菜谱卡片悬停增强
  // =============================================
  document.querySelectorAll(".recipe-card").forEach((card) => {
    card.addEventListener("mouseenter", () => {
      const icon = card.querySelector(".text-6xl");
      if (icon) {
        icon.style.transform = "scale(1.15) rotate(-5deg)";
        icon.style.transition = "transform 0.4s ease";
      }
    });
    card.addEventListener("mouseleave", () => {
      const icon = card.querySelector(".text-6xl");
      if (icon) {
        icon.style.transform = "scale(1) rotate(0deg)";
      }
    });
  });

  // =============================================
  // 11. 键盘快捷键
  // =============================================
  document.addEventListener("keydown", (e) => {
    // ESC 关闭移动端菜单
    if (e.key === "Escape") {
      if (mobileMenu && !mobileMenu.classList.contains("hidden")) {
        mobileMenu.classList.add("hidden");
        const icon = mobileMenuBtn?.querySelector("i");
        if (icon) {
          icon.classList.add("bi-list");
          icon.classList.remove("bi-x");
        }
      }
    }
  });

  console.log("🦀 肴柒蟹 (YaoQiXie) 已加载完成");
  console.log("📦 多页面导航模式 | 首页 · 养殖 · 行情 · 菜谱 · 社区");

  // =============================================
  // 12. 技术手册下载 (features.html)
  // =============================================
  document.querySelectorAll(".tech-download").forEach((link) => {
    link.addEventListener("click", (e) => {
      e.preventDefault();
      const docName = link.dataset.doc || "技术文档";

      // 创建模拟下载提示
      const toast = document.createElement("div");
      toast.className =
        "fixed top-24 right-4 bg-white rounded-xl shadow-2xl border border-gray-100 p-4 z-50 animate-slide-in";
      toast.style.maxWidth = "320px";
      toast.innerHTML = `
        <div class="flex items-start">
          <div class="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center mr-3 flex-shrink-0">
            <i class="bi bi-check-lg text-green-500 text-xl"></i>
          </div>
          <div>
            <p class="font-medium text-gray-800 text-sm">《${docName}》下载成功</p>
            <p class="text-xs text-gray-400 mt-0.5">PDF 文件已保存到下载目录</p>
            <div class="mt-2 w-full bg-gray-200 rounded-full h-1">
              <div class="bg-green-500 h-1 rounded-full" style="width: 100%"></div>
            </div>
          </div>
          <button class="ml-3 text-gray-400 hover:text-gray-600 flex-shrink-0" onclick="this.parentElement.parentElement.remove()">
            <i class="bi bi-x"></i>
          </button>
        </div>
      `;
      document.body.appendChild(toast);

      // 自动消失
      setTimeout(() => {
        toast.style.transition = "opacity 0.3s, transform 0.3s";
        toast.style.opacity = "0";
        toast.style.transform = "translateX(100px)";
        setTimeout(() => toast.remove(), 300);
      }, 3000);
    });
  });
});
