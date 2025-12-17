// ========== حماية خفيفة - منع F12 فقط ==========
(function() {
    // منع F12 فقط
    document.addEventListener('keydown', function(e) {
        if (e.key === 'F12' || e.keyCode === 123) {
            e.preventDefault();
            showWarning('F12 is disabled for security reasons!');
            return false;
        }
    });

    // منع النقر بزر الماوس الأيمن
    document.addEventListener('contextmenu', function(e) {
        e.preventDefault();
        return false;
    });

})();

// ========== نظام CAPTCHA المخصص ==========
let currentCaptcha = '';
let captchaAttempts = 0;
const maxCaptchaAttempts = 3;

function generateCaptcha() {
    const canvas = document.getElementById('captchaCanvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // تنظيف Canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // توليد كود عشوائي
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let captcha = '';
    for (let i = 0; i < 6; i++) {
        captcha += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    currentCaptcha = captcha;
    
    // خلفية
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // إضافة ضوضاء
    for (let i = 0; i < 50; i++) {
        ctx.fillStyle = `rgba(255, 255, 255, ${Math.random() * 0.1})`;
        ctx.fillRect(
            Math.random() * canvas.width,
            Math.random() * canvas.height,
            Math.random() * 3,
            Math.random() * 3
        );
    }
    
    // رسم النص
    ctx.font = 'bold 28px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    for (let i = 0; i < captcha.length; i++) {
        // تلوين كل حرف
        const hue = (i * 60 + Math.random() * 30) % 360;
        ctx.fillStyle = `hsl(${hue}, 70%, 60%)`;
        
        // تدوير بسيط
        ctx.save();
        ctx.translate(40 + i * 30, 25);
        ctx.rotate((Math.random() - 0.5) * 0.4);
        
        // رسم الحرف
        ctx.fillText(captcha[i], 0, 0);
        ctx.restore();
    }
    
    // إضافة خطوط
    for (let i = 0; i < 5; i++) {
        ctx.strokeStyle = `rgba(255, 255, 255, ${Math.random() * 0.3})`;
        ctx.lineWidth = Math.random() * 2;
        ctx.beginPath();
        ctx.moveTo(Math.random() * canvas.width, Math.random() * canvas.height);
        ctx.lineTo(Math.random() * canvas.width, Math.random() * canvas.height);
        ctx.stroke();
    }
    
    // إعادة تعيين حالة CAPTCHA
    const statusElement = document.getElementById('captchaStatus');
    if (statusElement) {
        statusElement.textContent = '';
        statusElement.className = 'captcha-status';
    }
}

function playCaptchaAudio() {
    if (!currentCaptcha) return;
    
    const utterance = new SpeechSynthesisUtterance();
    utterance.text = currentCaptcha.split('').join(' ');
    utterance.rate = 0.8;
    utterance.pitch = 1;
    utterance.volume = 1;
    
    window.speechSynthesis.speak(utterance);
}

function validateCaptcha() {
    const userInput = document.getElementById('captchaInput').value.toUpperCase();
    const statusElement = document.getElementById('captchaStatus');
    
    if (!userInput) {
        statusElement.textContent = 'Please enter the code';
        statusElement.className = 'captcha-status captcha-invalid';
        return false;
    }
    
    if (userInput === currentCaptcha) {
        statusElement.textContent = '✓ Verification successful!';
        statusElement.className = 'captcha-status captcha-valid';
        captchaAttempts = 0;
        return true;
    } else {
        captchaAttempts++;
        statusElement.textContent = `✗ Invalid code! Attempts left: ${maxCaptchaAttempts - captchaAttempts}`;
        statusElement.className = 'captcha-status captcha-invalid';
        
        if (captchaAttempts >= maxCaptchaAttempts) {
            statusElement.textContent = '✗ Too many failed attempts! Please refresh the page.';
            document.getElementById('captchaInput').disabled = true;
            setTimeout(() => {
                location.reload();
            }, 3000);
        } else {
            generateCaptcha();
            document.getElementById('captchaInput').value = '';
        }
        return false;
    }
}

// ========== نظام الطلبات ==========
let selectedPlan = '';
let selectedPayment = '';
let orders = JSON.parse(localStorage.getItem('ff_secure_orders')) || [];

function openModal(plan) {
    selectedPlan = plan;
    document.getElementById('purchaseModal').style.display = 'block';
    updateModalTitle(plan);
    
    // توليد CAPTCHA عند فتح النافذة
    setTimeout(() => {
        generateCaptcha();
    }, 100);
}

function closeModal() {
    document.getElementById('purchaseModal').style.display = 'none';
    resetForm();
}

function updateModalTitle(plan) {
    const titles = {
        '7days': 'BOT DANCING 7 DAYS',
        '15days': 'BOT DANCING 15 DAYS', 
        '1month': 'BOT DANCING 1 MONTH'
    };
    document.getElementById('modalTitle').textContent = titles[plan];
}

function selectPayment(method) {
    selectedPayment = method;
    document.querySelectorAll('.payment-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    event.target.classList.add('selected');
    
    document.getElementById('diamondsInstructions').style.display = 'none';
    document.getElementById('dollarsInstructions').style.display = 'none';
    
    if (method === 'diamonds') {
        document.getElementById('diamondsInstructions').style.display = 'block';
        updateDiamondAmount();
    } else if (method === 'dollars') {
        document.getElementById('dollarsInstructions').style.display = 'block';
    }
}

function updateDiamondAmount() {
    const amounts = {
        '7days': '300',
        '15days': '750', 
        '1month': '1200'
    };
    document.getElementById('diamondAmount').textContent = amounts[selectedPlan];
}

function verifySecurity() {
    if (!validateCaptcha()) {
        alert('Please complete the CAPTCHA verification correctly!');
        return false;
    }
    return true;
}

async function processDiamondOrder() {
    if (!verifySecurity()) return;
    
    const username = document.getElementById('telegramUsername').value;
    const freeFireId = document.getElementById('freeFireId').value;
    
    if (!username || !freeFireId) {
        alert('Please fill all fields!');
        return;
    }

    const orderData = {
        id: Date.now(),
        username: username,
        freeFireId: freeFireId,
        plan: selectedPlan,
        payment: 'Diamonds',
        amount: getDiamondAmount(),
        status: 'pending',
        timestamp: new Date().toLocaleString()
    };

    saveSecureOrder(orderData);
    
    const success = await sendToTelegram(orderData);
    
    if (success) {
        alert('✅ Order received! We will verify and activate within 24 hours.');
    } else {
        alert('✅ Order saved! Contact @kali_admin_vip if no response.');
    }
    closeModal();
}

async function processDollarOrder() {
    if (!verifySecurity()) return;
    
    const username = document.getElementById('telegramUsername').value;
    const freeFireId = document.getElementById('freeFireId').value;
    
    if (!username || !freeFireId) {
        alert('Please fill all fields!');
        return;
    }

    const orderData = {
        id: Date.now(),
        username: username,
        freeFireId: freeFireId,
        plan: selectedPlan,
        payment: 'USD',
        amount: getDollarAmount(),
        status: 'pending',
        timestamp: new Date().toLocaleString()
    };

    saveSecureOrder(orderData);
    
    const success = await sendToTelegram(orderData);
    
    if (success) {
        alert('✅ Order received! Complete payment on Telegram.');
    } else {
        alert('✅ Order saved! Contact @kali_admin_vip to pay.');
    }
    closeModal();
}

function getDiamondAmount() {
    const amounts = {
        '7days': '300',
        '15days': '750', 
        '1month': '1200'
    };
    return amounts[selectedPlan];
}

function getDollarAmount() {
    const amounts = {
        '7days': '$5',
        '15days': '$10', 
        '1month': '$25'
    };
    return amounts[selectedPlan];
}

function saveSecureOrder(orderData) {
    orders.push(orderData);
    localStorage.setItem('ff_secure_orders', JSON.stringify(orders));
}

async function sendToTelegram(orderData) {
    try {
        const response = await fetch('https://formspree.io/f/xjvnzzvz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                _subject: `🎮 NEW ORDER - ${orderData.plan}`,
                telegram: orderData.username,
                freefire_id: orderData.freeFireId,
                plan: orderData.plan,
                payment: orderData.payment,
                amount: orderData.amount,
                time: orderData.timestamp,
                _replyto: 'noreply@ffbot.com'
            })
        });
        
        return response.ok;
    } catch (error) {
        console.log('Delivery failed');
        return false;
    }
}

function resetForm() {
    document.getElementById('purchaseForm').reset();
    selectedPayment = '';
    document.querySelectorAll('.payment-option').forEach(opt => {
        opt.classList.remove('selected');
    });
    document.getElementById('diamondsInstructions').style.display = 'none';
    document.getElementById('dollarsInstructions').style.display = 'none';
    
    generateCaptcha();
}

function showWarning(message) {
    const warning = document.createElement('div');
    warning.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #ff6b6b;
        color: white;
        padding: 12px 18px;
        border-radius: 8px;
        z-index: 9999;
        font-family: Arial;
        font-size: 14px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    warning.textContent = message;
    document.body.appendChild(warning);
    
    setTimeout(() => {
        if (warning.parentNode) {
            warning.parentNode.removeChild(warning);
        }
    }, 3000);
}

window.onclick = function(event) {
    const modal = document.getElementById('purchaseModal');
    if (event.target === modal) {
        closeModal();
    }
}

// تهيئة عند تحميل الصفحة
// Initialization handled in index.html with emotes loading